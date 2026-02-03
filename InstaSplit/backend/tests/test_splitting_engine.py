"""
Tests for the bill splitting calculation engine.
Covers all split modes, rounding, and reconciliation.
"""
import pytest
from decimal import Decimal

from app.schemas import (
    Receipt, ReceiptItem, Group, Person, ItemAssignments, AssignmentShare,
    SplitOptions, SplitMode, Confidence
)
from app.splitting.engine import calculate_split


def test_simple_even_split():
    """Test basic even split of items."""
    # Create receipt with 2 items
    receipt = Receipt(
        items=[
            ReceiptItem(id="1", name="Pizza", quantity=1, total_price=20.0),
            ReceiptItem(id="2", name="Salad", quantity=1, total_price=10.0)
        ],
        subtotal=30.0,
        tax=3.0,
        tip=6.0,
        total=39.0,
        confidence=Confidence(overall=1.0)
    )
    
    # Group of 2 people
    group = Group(people=[
        Person(id="p1", name="Alice"),
        Person(id="p2", name="Bob")
    ])
    
    # Split everything evenly
    assignments = [
        ItemAssignments(
            item_id="1",
            shares=[
                AssignmentShare(person_id="p1", split_mode=SplitMode.EVEN),
                AssignmentShare(person_id="p2", split_mode=SplitMode.EVEN)
            ]
        ),
        ItemAssignments(
            item_id="2",
            shares=[
                AssignmentShare(person_id="p1", split_mode=SplitMode.EVEN),
                AssignmentShare(person_id="p2", split_mode=SplitMode.EVEN)
            ]
        )
    ]
    
    options = SplitOptions(tip_mode="proportional", discount_mode="proportional")
    
    breakdowns, reconciliation = calculate_split(receipt, group, assignments, options)
    
    # Each person should pay half
    assert len(breakdowns) == 2
    assert breakdowns[0].total_owed == 19.50
    assert breakdowns[1].total_owed == 19.50
    
    # Reconciliation should be perfect
    assert reconciliation.target_total == 39.0
    assert abs(reconciliation.difference) < 0.01


def test_quantity_split():
    """Test splitting by quantity."""
    receipt = Receipt(
        items=[
            ReceiptItem(id="1", name="Tacos", quantity=3, total_price=15.0)
        ],
        subtotal=15.0,
        tax=1.5,
        tip=3.0,
        total=19.5,
        confidence=Confidence(overall=1.0)
    )
    
    group = Group(people=[
        Person(id="p1", name="Alice"),
        Person(id="p2", name="Bob")
    ])
    
    # Alice ate 2 tacos, Bob ate 1
    assignments = [
        ItemAssignments(
            item_id="1",
            shares=[
                AssignmentShare(person_id="p1", share_quantity=2.0, split_mode=SplitMode.QUANTITY),
                AssignmentShare(person_id="p2", share_quantity=1.0, split_mode=SplitMode.QUANTITY)
            ]
        )
    ]
    
    options = SplitOptions(tip_mode="proportional")
    
    breakdowns, reconciliation = calculate_split(receipt, group, assignments, options)
    
    # Alice should pay 2/3, Bob should pay 1/3
    alice = next(b for b in breakdowns if b.person_id == "p1")
    bob = next(b for b in breakdowns if b.person_id == "p2")
    
    assert alice.items_subtotal == 10.0  # 2/3 of 15
    assert bob.items_subtotal == 5.0      # 1/3 of 15
    
    # Check total reconciliation
    total = alice.total_owed + bob.total_owed
    assert abs(total - 19.5) < 0.01


def test_proportional_discount():
    """Test proportional discount allocation."""
    receipt = Receipt(
        items=[
            ReceiptItem(id="1", name="Burger", quantity=1, total_price=20.0),
            ReceiptItem(id="2", name="Salad", quantity=1, total_price=10.0)
        ],
        subtotal=30.0,
        discount_total=-6.0,  # 20% discount
        tax=2.4,
        tip=5.0,
        total=31.4,
        confidence=Confidence(overall=1.0)
    )
    
    group = Group(people=[
        Person(id="p1", name="Alice"),
        Person(id="p2", name="Bob")
    ])
    
    # Alice gets burger, Bob gets salad
    assignments = [
        ItemAssignments(item_id="1", shares=[AssignmentShare(person_id="p1")]),
        ItemAssignments(item_id="2", shares=[AssignmentShare(person_id="p2")])
    ]
    
    options = SplitOptions(discount_mode="proportional", tip_mode="proportional")
    
    breakdowns, reconciliation = calculate_split(receipt, group, assignments, options)
    
    alice = next(b for b in breakdowns if b.person_id == "p1")
    bob = next(b for b in breakdowns if b.person_id == "p2")
    
    # Alice should get 2/3 of discount (20/30)
    assert abs(alice.discount_share - (-4.0)) < 0.01
    
    # Bob should get 1/3 of discount (10/30)
    assert abs(bob.discount_share - (-2.0)) < 0.01


def test_even_discount():
    """Test even discount allocation."""
    receipt = Receipt(
        items=[
            ReceiptItem(id="1", name="Burger", quantity=1, total_price=20.0),
            ReceiptItem(id="2", name="Salad", quantity=1, total_price=10.0)
        ],
        subtotal=30.0,
        discount_total=-6.0,
        tax=2.4,
        tip=5.0,
        total=31.4,
        confidence=Confidence(overall=1.0)
    )
    
    group = Group(people=[
        Person(id="p1", name="Alice"),
        Person(id="p2", name="Bob")
    ])
    
    assignments = [
        ItemAssignments(item_id="1", shares=[AssignmentShare(person_id="p1")]),
        ItemAssignments(item_id="2", shares=[AssignmentShare(person_id="p2")])
    ]
    
    options = SplitOptions(discount_mode="even", tip_mode="proportional")
    
    breakdowns, reconciliation = calculate_split(receipt, group, assignments, options)
    
    alice = next(b for b in breakdowns if b.person_id == "p1")
    bob = next(b for b in breakdowns if b.person_id == "p2")
    
    # Each should get half the discount
    assert abs(alice.discount_share - (-3.0)) < 0.01
    assert abs(bob.discount_share - (-3.0)) < 0.01


def test_proportional_tax():
    """Test proportional tax allocation."""
    receipt = Receipt(
        items=[
            ReceiptItem(id="1", name="Item1", quantity=1, total_price=100.0),
            ReceiptItem(id="2", name="Item2", quantity=1, total_price=50.0)
        ],
        subtotal=150.0,
        tax=15.0,  # 10% tax
        tip=0.0,
        total=165.0,
        confidence=Confidence(overall=1.0)
    )
    
    group = Group(people=[
        Person(id="p1", name="Alice"),
        Person(id="p2", name="Bob")
    ])
    
    # Alice gets expensive item, Bob gets cheaper
    assignments = [
        ItemAssignments(item_id="1", shares=[AssignmentShare(person_id="p1")]),
        ItemAssignments(item_id="2", shares=[AssignmentShare(person_id="p2")])
    ]
    
    options = SplitOptions(tax_mode="proportional")
    
    breakdowns, reconciliation = calculate_split(receipt, group, assignments, options)
    
    alice = next(b for b in breakdowns if b.person_id == "p1")
    bob = next(b for b in breakdowns if b.person_id == "p2")
    
    # Alice should pay 2/3 of tax (100/150)
    assert abs(alice.tax_share - 10.0) < 0.01
    
    # Bob should pay 1/3 of tax (50/150)
    assert abs(bob.tax_share - 5.0) < 0.01


def test_even_tip():
    """Test even tip allocation."""
    receipt = Receipt(
        items=[
            ReceiptItem(id="1", name="Item1", quantity=1, total_price=100.0),
            ReceiptItem(id="2", name="Item2", quantity=1, total_price=50.0)
        ],
        subtotal=150.0,
        tax=15.0,
        tip=30.0,
        total=195.0,
        confidence=Confidence(overall=1.0)
    )
    
    group = Group(people=[
        Person(id="p1", name="Alice"),
        Person(id="p2", name="Bob")
    ])
    
    assignments = [
        ItemAssignments(item_id="1", shares=[AssignmentShare(person_id="p1")]),
        ItemAssignments(item_id="2", shares=[AssignmentShare(person_id="p2")])
    ]
    
    options = SplitOptions(tip_mode="even")
    
    breakdowns, reconciliation = calculate_split(receipt, group, assignments, options)
    
    alice = next(b for b in breakdowns if b.person_id == "p1")
    bob = next(b for b in breakdowns if b.person_id == "p2")
    
    # Each should pay half the tip
    assert abs(alice.tip_share - 15.0) < 0.01
    assert abs(bob.tip_share - 15.0) < 0.01


def test_rounding_reconciliation():
    """Test that rounding reconciliation matches exact total."""
    receipt = Receipt(
        items=[
            ReceiptItem(id="1", name="Item1", quantity=1, total_price=10.01),
            ReceiptItem(id="2", name="Item2", quantity=1, total_price=10.01),
            ReceiptItem(id="3", name="Item3", quantity=1, total_price=10.01)
        ],
        subtotal=30.03,
        tax=3.33,
        tip=6.67,
        total=40.03,
        confidence=Confidence(overall=1.0)
    )
    
    group = Group(people=[
        Person(id="p1", name="Alice"),
        Person(id="p2", name="Bob"),
        Person(id="p3", name="Charlie")
    ])
    
    # Split everything 3 ways
    assignments = [
        ItemAssignments(
            item_id=str(i),
            shares=[
                AssignmentShare(person_id="p1", split_mode=SplitMode.EVEN),
                AssignmentShare(person_id="p2", split_mode=SplitMode.EVEN),
                AssignmentShare(person_id="p3", split_mode=SplitMode.EVEN)
            ]
        )
        for i in range(1, 4)
    ]
    
    options = SplitOptions(tip_mode="proportional")
    
    breakdowns, reconciliation = calculate_split(receipt, group, assignments, options)
    
    # Sum should exactly equal total
    total = sum(b.total_owed for b in breakdowns)
    assert total == 40.03
    
    # Reconciliation difference should be very small
    assert abs(reconciliation.difference) < 0.01


def test_single_person_gets_all():
    """Test when one person pays for everything."""
    receipt = Receipt(
        items=[
            ReceiptItem(id="1", name="Item", quantity=1, total_price=50.0)
        ],
        subtotal=50.0,
        tax=5.0,
        tip=10.0,
        total=65.0,
        confidence=Confidence(overall=1.0)
    )
    
    group = Group(people=[
        Person(id="p1", name="Alice")
    ])
    
    assignments = [
        ItemAssignments(item_id="1", shares=[AssignmentShare(person_id="p1")])
    ]
    
    options = SplitOptions()
    
    breakdowns, reconciliation = calculate_split(receipt, group, assignments, options)
    
    assert len(breakdowns) == 1
    assert breakdowns[0].total_owed == 65.0


def test_shared_item_with_service_fee():
    """Test shared item with service fee allocation."""
    receipt = Receipt(
        items=[
            ReceiptItem(id="1", name="Pizza", quantity=1, total_price=20.0)
        ],
        subtotal=20.0,
        tax=2.0,
        service_fee=3.0,
        tip=5.0,
        total=30.0,
        confidence=Confidence(overall=1.0)
    )
    
    group = Group(people=[
        Person(id="p1", name="Alice"),
        Person(id="p2", name="Bob")
    ])
    
    assignments = [
        ItemAssignments(
            item_id="1",
            shares=[
                AssignmentShare(person_id="p1", split_mode=SplitMode.EVEN),
                AssignmentShare(person_id="p2", split_mode=SplitMode.EVEN)
            ]
        )
    ]
    
    options = SplitOptions()
    
    breakdowns, reconciliation = calculate_split(receipt, group, assignments, options)
    
    # Check service fee is allocated
    alice = next(b for b in breakdowns if b.person_id == "p1")
    bob = next(b for b in breakdowns if b.person_id == "p2")
    
    assert alice.fee_share == 1.5
    assert bob.fee_share == 1.5
    
    # Total should match
    assert alice.total_owed + bob.total_owed == 30.0
