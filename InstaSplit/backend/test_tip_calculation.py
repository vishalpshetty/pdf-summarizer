"""
Test cases to verify tip calculation is included in bill splitting.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from app.schemas import Receipt, ReceiptItem, Group, Person, ItemAssignments, AssignmentShare, SplitOptions
from app.splitting import calculate_split


def test_tip_included_in_split():
    """Test that tip is correctly included in the final split."""
    
    # Create a simple receipt with tip
    receipt = Receipt(
        merchant_name="Test Restaurant",
        items=[
            ReceiptItem(
                id="item1",
                name="Burger",
                quantity=1.0,
                total_price=20.0,
                category="food"
            ),
            ReceiptItem(
                id="item2",
                name="Fries",
                quantity=1.0,
                total_price=10.0,
                category="food"
            )
        ],
        subtotal=30.0,
        tax=3.0,
        tip=6.0,  # 20% tip
        total=39.0  # subtotal + tax + tip
    )
    
    # Create a group with 2 people
    group = Group(
        people=[
            Person(id="person1", name="Alice"),
            Person(id="person2", name="Bob")
        ]
    )
    
    # Assign items (Alice gets burger, Bob gets fries)
    assignments = [
        ItemAssignments(
            item_id="item1",
            shares=[AssignmentShare(person_id="person1", split_mode="even")]
        ),
        ItemAssignments(
            item_id="item2",
            shares=[AssignmentShare(person_id="person2", split_mode="even")]
        )
    ]
    
    # Split options (proportional tip)
    options = SplitOptions(
        tax_mode="proportional",
        tip_mode="proportional"
    )
    
    # Calculate split
    breakdowns, reconciliation = calculate_split(receipt, group, assignments, options)
    
    print("=" * 60)
    print("TEST: Tip Included in Split (Proportional)")
    print("=" * 60)
    print(f"\nReceipt Total: ${receipt.total:.2f}")
    print(f"Subtotal: ${receipt.subtotal:.2f}")
    print(f"Tax: ${receipt.tax:.2f}")
    print(f"Tip: ${receipt.tip:.2f}")
    print()
    
    for breakdown in breakdowns:
        print(f"\n{breakdown.person_name}:")
        print(f"  Items: ${breakdown.items_subtotal:.2f}")
        print(f"  Tax Share: ${breakdown.tax_share:.2f}")
        print(f"  Tip Share: ${breakdown.tip_share:.2f}")
        print(f"  TOTAL: ${breakdown.total_owed:.2f}")
    
    print(f"\n{'='*60}")
    print(f"Sum of all splits: ${sum(b.total_owed for b in breakdowns):.2f}")
    print(f"Receipt total: ${receipt.total:.2f}")
    print(f"Difference: ${abs(sum(b.total_owed for b in breakdowns) - receipt.total):.2f}")
    print(f"{'='*60}\n")
    
    # Verify tip was included
    total_tip_shares = sum(b.tip_share for b in breakdowns)
    assert abs(total_tip_shares - receipt.tip) < 0.01, f"Tip shares ({total_tip_shares}) don't match tip ({receipt.tip})"
    
    # Verify totals match
    total_owed = sum(b.total_owed for b in breakdowns)
    assert abs(total_owed - receipt.total) < 0.01, f"Total owed ({total_owed}) doesn't match receipt ({receipt.total})"
    
    print("✅ TEST PASSED: Tip is correctly included in the split!\n")


def test_tip_even_split():
    """Test that tip is correctly split evenly when mode is 'even'."""
    
    # Create a receipt
    receipt = Receipt(
        merchant_name="Test Restaurant",
        items=[
            ReceiptItem(
                id="item1",
                name="Pizza",
                quantity=1.0,
                total_price=30.0,
                category="food"
            )
        ],
        subtotal=30.0,
        tax=3.0,
        tip=9.0,  # $9 tip
        total=42.0
    )
    
    # 3 people splitting evenly
    group = Group(
        people=[
            Person(id="p1", name="Alice"),
            Person(id="p2", name="Bob"),
            Person(id="p3", name="Charlie")
        ]
    )
    
    # All share the pizza
    assignments = [
        ItemAssignments(
            item_id="item1",
            shares=[
                AssignmentShare(person_id="p1", split_mode="even"),
                AssignmentShare(person_id="p2", split_mode="even"),
                AssignmentShare(person_id="p3", split_mode="even")
            ]
        )
    ]
    
    # Even split for tip
    options = SplitOptions(
        tax_mode="even",
        tip_mode="even"
    )
    
    breakdowns, _ = calculate_split(receipt, group, assignments, options)
    
    print("=" * 60)
    print("TEST: Tip Split Evenly")
    print("=" * 60)
    print(f"\nTotal Tip: ${receipt.tip:.2f}")
    print(f"Expected per person: ${receipt.tip / 3:.2f}\n")
    
    for breakdown in breakdowns:
        print(f"{breakdown.person_name}: Tip Share = ${breakdown.tip_share:.2f}")
        assert abs(breakdown.tip_share - (receipt.tip / 3)) < 0.02, f"Tip not split evenly for {breakdown.person_name}"
    
    print("\n✅ TEST PASSED: Tip split evenly!\n")


def test_no_tip():
    """Test that calculation works when tip is 0 or None."""
    
    receipt = Receipt(
        merchant_name="Test Restaurant",
        items=[
            ReceiptItem(
                id="item1",
                name="Coffee",
                quantity=1.0,
                total_price=5.0,
                category="drink"
            )
        ],
        subtotal=5.0,
        tax=0.5,
        tip=0.0,  # No tip
        total=5.5
    )
    
    group = Group(people=[Person(id="p1", name="Alice")])
    
    assignments = [
        ItemAssignments(
            item_id="item1",
            shares=[AssignmentShare(person_id="p1", split_mode="even")]
        )
    ]
    
    options = SplitOptions()
    
    breakdowns, _ = calculate_split(receipt, group, assignments, options)
    
    print("=" * 60)
    print("TEST: No Tip")
    print("=" * 60)
    print(f"\nReceipt total: ${receipt.total:.2f}")
    print(f"Person owes: ${breakdowns[0].total_owed:.2f}")
    print(f"Tip share: ${breakdowns[0].tip_share:.2f}")
    
    assert breakdowns[0].tip_share == 0.0, "Tip share should be 0"
    assert abs(breakdowns[0].total_owed - receipt.total) < 0.01, "Total should match"
    
    print("\n✅ TEST PASSED: No tip calculation works!\n")


if __name__ == "__main__":
    test_tip_included_in_split()
    test_tip_even_split()
    test_no_tip()
    
    print("=" * 60)
    print("🎉 ALL TESTS PASSED!")
    print("=" * 60)
