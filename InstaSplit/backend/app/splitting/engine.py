"""
Bill splitting calculation engine with exact reconciliation.
Handles proportional/even splits, rounding, and penny distribution.
"""
from typing import Dict, List, Tuple
from decimal import Decimal, ROUND_HALF_UP
from collections import defaultdict

from ..schemas import (
    Receipt, Group, ItemAssignments, SplitOptions, SplitMode,
    PersonBreakdown, ReconciliationInfo
)


class SplittingEngine:
    """Calculate bill splits with exact reconciliation."""
    
    def __init__(self, receipt: Receipt, group: Group, assignments: List[ItemAssignments], options: SplitOptions):
        self.receipt = receipt
        self.group = group
        self.assignments = assignments
        self.options = options
        
        # Build person lookup
        self.people = {p.id: p for p in group.people}
        
        # Build assignment lookup
        self.item_assignments = {a.item_id: a for a in assignments}
    
    def calculate(self) -> Tuple[List[PersonBreakdown], ReconciliationInfo]:
        """
        Calculate per-person breakdown with exact reconciliation.
        
        Returns:
            Tuple of (list of PersonBreakdown, ReconciliationInfo)
        """
        # Initialize per-person tracking
        person_data = {
            person_id: {
                'items_subtotal': Decimal('0'),
                'discount_share': Decimal('0'),
                'tax_share': Decimal('0'),
                'fee_share': Decimal('0'),
                'tip_share': Decimal('0'),
                'item_details': []
            }
            for person_id in self.people.keys()
        }
        
        # Step 1: Calculate item subtotals per person
        self._calculate_item_splits(person_data)
        
        # Step 2: Calculate discount shares
        self._calculate_discount_shares(person_data)
        
        # Step 3: Calculate tax shares
        self._calculate_tax_shares(person_data)
        
        # Step 4: Calculate fee shares
        self._calculate_fee_shares(person_data)
        
        # Step 5: Calculate tip shares
        self._calculate_tip_shares(person_data)
        
        # Step 6: Sum up totals (before reconciliation)
        totals = {}
        for person_id, data in person_data.items():
            total = (
                data['items_subtotal'] +
                data['discount_share'] +
                data['tax_share'] +
                data['fee_share'] +
                data['tip_share']
            )
            totals[person_id] = total
        
        # Step 7: Reconcile to match exact receipt total
        reconciled_totals = self._reconcile_totals(totals)
        
        # Step 8: Build PersonBreakdown objects
        breakdowns = []
        for person_id in self.people.keys():
            breakdown = PersonBreakdown(
                person_id=person_id,
                person_name=self.people[person_id].name,
                items_subtotal=float(person_data[person_id]['items_subtotal']),
                discount_share=float(person_data[person_id]['discount_share']),
                tax_share=float(person_data[person_id]['tax_share']),
                fee_share=float(person_data[person_id]['fee_share']),
                tip_share=float(person_data[person_id]['tip_share']),
                total_owed=float(reconciled_totals[person_id]),
                item_details=person_data[person_id]['item_details']
            )
            breakdowns.append(breakdown)
        
        # Step 9: Create reconciliation info
        calculated_total = sum(totals.values())
        reconciled_total = sum(reconciled_totals.values())
        difference = Decimal(str(self.receipt.total)) - calculated_total
        
        reconciliation = ReconciliationInfo(
            target_total=self.receipt.total,
            calculated_total=float(calculated_total),
            difference=float(difference),
            pennies_adjusted=int(abs(difference) * 100)
        )
        
        return breakdowns, reconciliation
    
    def _calculate_item_splits(self, person_data: Dict):
        """Calculate how items are split among people."""
        for item in self.receipt.items:
            assignment = self.item_assignments.get(item.id)
            if not assignment or not assignment.shares:
                # Item not assigned - skip
                continue
            
            item_total = Decimal(str(item.total_price))
            shares = assignment.shares
            
            # Determine split mode
            if len(shares) == 1:
                # Only one person
                person_id = shares[0].person_id
                person_data[person_id]['items_subtotal'] += item_total
                person_data[person_id]['item_details'].append({
                    'item_name': item.name,
                    'item_total': float(item_total),
                    'person_share': float(item_total),
                    'share_mode': 'full'
                })
            else:
                # Multiple people - check split mode
                if shares[0].split_mode == SplitMode.QUANTITY:
                    self._split_by_quantity(item, shares, item_total, person_data)
                elif shares[0].split_mode == SplitMode.FRACTION:
                    self._split_by_fraction(item, shares, item_total, person_data)
                else:  # EVEN
                    self._split_evenly(item, shares, item_total, person_data)
    
    def _split_evenly(self, item, shares, item_total: Decimal, person_data: Dict):
        """Split item evenly among people."""
        num_people = len(shares)
        share_amount = item_total / num_people
        
        for share in shares:
            person_data[share.person_id]['items_subtotal'] += share_amount
            person_data[share.person_id]['item_details'].append({
                'item_name': item.name,
                'item_total': float(item_total),
                'person_share': float(share_amount),
                'share_mode': 'even',
                'num_people': num_people
            })
    
    def _split_by_quantity(self, item, shares, item_total: Decimal, person_data: Dict):
        """Split item by specified quantities."""
        total_qty = sum(Decimal(str(share.share_quantity or 0)) for share in shares)
        
        if total_qty == 0:
            # Fall back to even split
            self._split_evenly(item, shares, item_total, person_data)
            return
        
        for share in shares:
            qty = Decimal(str(share.share_quantity or 0))
            share_amount = (qty / total_qty) * item_total
            person_data[share.person_id]['items_subtotal'] += share_amount
            person_data[share.person_id]['item_details'].append({
                'item_name': item.name,
                'item_total': float(item_total),
                'person_share': float(share_amount),
                'share_mode': 'quantity',
                'quantity': float(qty),
                'total_quantity': float(total_qty)
            })
    
    def _split_by_fraction(self, item, shares, item_total: Decimal, person_data: Dict):
        """Split item by specified fractions."""
        for share in shares:
            fraction = Decimal(str(share.share_fraction or 0))
            share_amount = fraction * item_total
            person_data[share.person_id]['items_subtotal'] += share_amount
            person_data[share.person_id]['item_details'].append({
                'item_name': item.name,
                'item_total': float(item_total),
                'person_share': float(share_amount),
                'share_mode': 'fraction',
                'fraction': float(fraction)
            })
    
    def _calculate_discount_shares(self, person_data: Dict):
        """Allocate discount to people."""
        if not self.receipt.discount_total:
            return
        
        discount = Decimal(str(self.receipt.discount_total))
        
        if self.options.discount_mode == 'even':
            # Split evenly
            num_people = len(self.people)
            per_person = discount / num_people
            for person_id in person_data.keys():
                person_data[person_id]['discount_share'] = per_person
        else:
            # Proportional to items_subtotal
            total_items = sum(data['items_subtotal'] for data in person_data.values())
            if total_items > 0:
                for person_id, data in person_data.items():
                    proportion = data['items_subtotal'] / total_items
                    person_data[person_id]['discount_share'] = proportion * discount
    
    def _calculate_tax_shares(self, person_data: Dict):
        """Allocate tax proportionally."""
        if not self.receipt.tax:
            return
        
        tax = Decimal(str(self.receipt.tax))
        
        if self.options.tax_mode == 'even':
            num_people = len(self.people)
            per_person = tax / num_people
            for person_id in person_data.keys():
                person_data[person_id]['tax_share'] = per_person
        else:
            # Proportional to items_subtotal
            total_items = sum(data['items_subtotal'] for data in person_data.values())
            if total_items > 0:
                for person_id, data in person_data.items():
                    proportion = data['items_subtotal'] / total_items
                    person_data[person_id]['tax_share'] = proportion * tax
    
    def _calculate_fee_shares(self, person_data: Dict):
        """Allocate service fees proportionally."""
        if not self.receipt.service_fee:
            return
        
        fee = Decimal(str(self.receipt.service_fee))
        total_items = sum(data['items_subtotal'] for data in person_data.values())
        
        if total_items > 0:
            for person_id, data in person_data.items():
                proportion = data['items_subtotal'] / total_items
                person_data[person_id]['fee_share'] = proportion * fee
    
    def _calculate_tip_shares(self, person_data: Dict):
        """Allocate tip based on mode."""
        if not self.receipt.tip:
            return
        
        tip = Decimal(str(self.receipt.tip))
        
        if self.options.tip_mode == 'even':
            num_people = len(self.people)
            per_person = tip / num_people
            for person_id in person_data.keys():
                person_data[person_id]['tip_share'] = per_person
        else:
            # Proportional to items_subtotal
            total_items = sum(data['items_subtotal'] for data in person_data.values())
            if total_items > 0:
                for person_id, data in person_data.items():
                    proportion = data['items_subtotal'] / total_items
                    person_data[person_id]['tip_share'] = proportion * tip
    
    def _reconcile_totals(self, totals: Dict[str, Decimal]) -> Dict[str, Decimal]:
        """
        Reconcile totals to match receipt exactly using fair penny distribution.
        
        Args:
            totals: Dict of person_id -> calculated total (Decimal)
            
        Returns:
            Dict of person_id -> reconciled total (Decimal)
        """
        target = Decimal(str(self.receipt.total))
        
        # Round each person's total to cents
        rounded = {}
        for person_id, total in totals.items():
            rounded[person_id] = total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        # Calculate difference
        sum_rounded = sum(rounded.values())
        diff = target - sum_rounded
        
        # Convert difference to pennies
        pennies = int(diff * 100)
        
        if pennies == 0:
            return rounded
        
        # Distribute pennies fairly
        # Sort people by fractional part of their unrounded total
        fractional_parts = []
        for person_id, total in totals.items():
            fractional = total - rounded[person_id]
            fractional_parts.append((abs(fractional), person_id))
        
        # Sort by fractional part (largest first)
        fractional_parts.sort(reverse=True)
        
        # Distribute pennies
        penny_value = Decimal('0.01')
        for i in range(abs(pennies)):
            person_id = fractional_parts[i % len(fractional_parts)][1]
            if pennies > 0:
                rounded[person_id] += penny_value
            else:
                rounded[person_id] -= penny_value
        
        return rounded


def calculate_split(
    receipt: Receipt,
    group: Group,
    assignments: List[ItemAssignments],
    options: SplitOptions
) -> Tuple[List[PersonBreakdown], ReconciliationInfo]:
    """
    Convenience function to calculate bill split.
    
    Args:
        receipt: Receipt object
        group: Group of people
        assignments: Item assignments
        options: Split options
        
    Returns:
        Tuple of (breakdowns, reconciliation info)
    """
    engine = SplittingEngine(receipt, group, assignments, options)
    return engine.calculate()
