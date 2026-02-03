"""
Step 5: Show results and export options.
"""
import streamlit as st
import requests
import pandas as pd
import json
from io import StringIO


def render_results_step(backend_url: str):
    """Render the results step."""
    st.markdown('<div class="step-header">Step 5: Results</div>', unsafe_allow_html=True)
    
    if not st.session_state.receipt or not st.session_state.group or not st.session_state.assignments:
        st.warning("⚠️ Missing required data")
        return
    
    # Calculate split if not already done
    if not st.session_state.results:
        calculate_split(backend_url)
    
    results = st.session_state.results
    
    if not results:
        st.error("❌ Failed to calculate split")
        return
    
    # Show results
    st.success("✅ Bill split calculated successfully!")
    
    # Summary metrics
    breakdowns = results['breakdowns']
    reconciliation = results['reconciliation']
    
    st.markdown("### Summary")
    
    cols = st.columns(len(breakdowns))
    for col, breakdown in zip(cols, breakdowns):
        with col:
            st.metric(
                label=breakdown['person_name'],
                value=f"${breakdown['total_owed']:.2f}"
            )
    
    # Detailed breakdowns
    st.markdown("---")
    st.markdown("### Detailed Breakdown")
    
    for breakdown in breakdowns:
        with st.expander(f"**{breakdown['person_name']}** - ${breakdown['total_owed']:.2f}", expanded=True):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Show items
                if breakdown['item_details']:
                    st.markdown("**Items:**")
                    for detail in breakdown['item_details']:
                        st.write(f"- {detail['item_name']}: ${detail['person_share']:.2f}")
            
            with col2:
                # Show breakdown
                st.markdown("**Breakdown:**")
                st.write(f"Items: ${breakdown['items_subtotal']:.2f}")
                if breakdown['discount_share'] != 0:
                    st.write(f"Discount: ${breakdown['discount_share']:.2f}")
                if breakdown['tax_share'] > 0:
                    st.write(f"Tax: ${breakdown['tax_share']:.2f}")
                if breakdown['fee_share'] > 0:
                    st.write(f"Fees: ${breakdown['fee_share']:.2f}")
                if breakdown['tip_share'] > 0:
                    st.write(f"Tip: ${breakdown['tip_share']:.2f}")
                st.markdown(f"**Total: ${breakdown['total_owed']:.2f}**")
    
    # Reconciliation info
    st.markdown("---")
    st.markdown("### Reconciliation")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Receipt Total", f"${reconciliation['target_total']:.2f}")
    with col2:
        calculated = sum(b['total_owed'] for b in breakdowns)
        st.metric("Sum of Splits", f"${calculated:.2f}")
    with col3:
        diff = abs(reconciliation['target_total'] - calculated)
        if diff < 0.01:
            st.metric("Difference", "Perfect! ✅", delta=0)
        else:
            st.metric("Difference", f"${diff:.2f}")
    
    if abs(reconciliation['difference']) > 0.01:
        st.info(f"ℹ️ Adjusted {reconciliation['pennies_adjusted']} pennies for exact reconciliation")
    
    # Export options
    st.markdown("---")
    st.markdown("### Export")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Export as JSON
        json_data = json.dumps(results, indent=2)
        st.download_button(
            label="📥 Download JSON",
            data=json_data,
            file_name="bill_split.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col2:
        # Export as CSV
        csv_data = create_csv_export(breakdowns)
        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name="bill_split.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    # Share results
    st.markdown("---")
    st.markdown("### Share Results")
    
    share_text = create_share_text(breakdowns, st.session_state.receipt)
    st.text_area("Copy and share:", share_text, height=200)


def calculate_split(backend_url: str):
    """Call backend to calculate split."""
    with st.spinner("🔄 Calculating split..."):
        try:
            # Build request
            request_data = build_split_request()
            
            # Call backend
            response = requests.post(
                f"{backend_url}/split/calculate",
                json=request_data,
                timeout=30
            )
            
            if response.status_code == 200:
                st.session_state.results = response.json()
            else:
                st.error(f"❌ Error calculating split: {response.status_code}")
                st.write(response.json())
                
        except requests.exceptions.ConnectionError:
            st.error(f"❌ Could not connect to backend at {backend_url}")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")


def build_split_request():
    """Build the split request from session state."""
    receipt = st.session_state.receipt
    group = st.session_state.group
    assignments = st.session_state.assignments
    options = st.session_state.split_options
    
    # Build assignments in the required format
    formatted_assignments = []
    
    for item_id, assignment in assignments.items():
        if not assignment.get('people'):
            continue
        
        shares = []
        split_mode = assignment.get('split_mode', 'even')
        
        for person_id in assignment['people']:
            share = {
                'person_id': person_id,
                'split_mode': split_mode
            }
            
            if split_mode == 'quantity' and 'quantities' in assignment:
                share['share_quantity'] = assignment['quantities'].get(person_id, 1.0)
            
            shares.append(share)
        
        formatted_assignments.append({
            'item_id': item_id,
            'shares': shares
        })
    
    return {
        'receipt': receipt,
        'group': group,
        'assignments': formatted_assignments,
        'options': options
    }


def create_csv_export(breakdowns):
    """Create CSV export of results."""
    rows = []
    
    for breakdown in breakdowns:
        rows.append({
            'Person': breakdown['person_name'],
            'Items Subtotal': f"${breakdown['items_subtotal']:.2f}",
            'Discount': f"${breakdown['discount_share']:.2f}",
            'Tax': f"${breakdown['tax_share']:.2f}",
            'Fees': f"${breakdown['fee_share']:.2f}",
            'Tip': f"${breakdown['tip_share']:.2f}",
            'Total Owed': f"${breakdown['total_owed']:.2f}"
        })
    
    df = pd.DataFrame(rows)
    return df.to_csv(index=False)


def create_share_text(breakdowns, receipt):
    """Create shareable text summary."""
    lines = [
        "💰 Bill Split Results",
        "=" * 40,
        ""
    ]
    
    if receipt.get('merchant_name'):
        lines.append(f"Restaurant: {receipt['merchant_name']}")
        lines.append("")
    
    lines.append(f"Total: ${receipt['total']:.2f}")
    lines.append("")
    
    for breakdown in breakdowns:
        lines.append(f"{breakdown['person_name']}: ${breakdown['total_owed']:.2f}")
    
    lines.append("")
    lines.append("Generated by InstaSplit")
    
    return "\n".join(lines)
