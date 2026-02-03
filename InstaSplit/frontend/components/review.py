"""
Step 2: Review and edit extracted receipt data.
"""
import streamlit as st
import pandas as pd
import uuid


def render_review_step():
    """Render the review step."""
    st.markdown('<div class="step-header">Step 2: Review & Edit Receipt</div>', unsafe_allow_html=True)
    
    if not st.session_state.receipt:
        st.warning("⚠️ No receipt data. Please go back and upload a receipt.")
        return
    
    receipt = st.session_state.receipt
    
    st.info("✏️ Review the extracted data and make any corrections needed")
    
    # Receipt metadata
    col1, col2 = st.columns(2)
    with col1:
        merchant = st.text_input(
            "Merchant Name",
            value=receipt.get('merchant_name', ''),
            placeholder="Restaurant name"
        )
        receipt['merchant_name'] = merchant
    
    with col2:
        currency = st.text_input("Currency", value=receipt.get('currency', 'USD'))
        receipt['currency'] = currency
    
    st.markdown("### Items")
    
    # Create DataFrame for items
    items_df = pd.DataFrame([
        {
            'Name': item['name'],
            'Quantity': item['quantity'],
            'Unit Price': item.get('unit_price', item['total_price'] / item['quantity']),
            'Total': item['total_price'],
            'Category': item.get('category', 'unknown')
        }
        for item in receipt['items']
    ])
    
    # Editable data editor
    edited_items = st.data_editor(
        items_df,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "Name": st.column_config.TextColumn("Item Name", required=True),
            "Quantity": st.column_config.NumberColumn("Qty", min_value=0.1, format="%.2f"),
            "Unit Price": st.column_config.NumberColumn("Unit Price", format="$%.2f"),
            "Total": st.column_config.NumberColumn("Total Price", format="$%.2f", required=True),
            "Category": st.column_config.SelectboxColumn(
                "Category",
                options=["food", "drink", "fee", "discount", "tax", "tip", "unknown"],
                default="food"
            )
        }
    )
    
    # Update items in receipt
    receipt['items'] = [
        {
            'id': receipt['items'][i]['id'] if i < len(receipt['items']) else str(uuid.uuid4()),
            'name': row['Name'],
            'quantity': row['Quantity'],
            'unit_price': row['Unit Price'],
            'total_price': row['Total'],
            'category': row['Category']
        }
        for i, row in edited_items.iterrows()
    ]
    
    st.markdown("### Totals")
    
    # Edit totals
    col1, col2, col3 = st.columns(3)
    
    with col1:
        subtotal = st.number_input(
            "Subtotal",
            value=float(receipt.get('subtotal') or sum(item['total_price'] for item in receipt['items'])),
            format="%.2f"
        )
        receipt['subtotal'] = subtotal
        
        tax = st.number_input(
            "Tax",
            value=float(receipt.get('tax') or 0),
            format="%.2f"
        )
        receipt['tax'] = tax
    
    with col2:
        service_fee = st.number_input(
            "Service Fee",
            value=float(receipt.get('service_fee') or 0),
            format="%.2f"
        )
        receipt['service_fee'] = service_fee
        
        discount = st.number_input(
            "Discount (negative)",
            value=float(receipt.get('discount_total') or 0),
            format="%.2f"
        )
        receipt['discount_total'] = discount
    
    with col3:
        tip = st.number_input(
            "Tip",
            value=float(receipt.get('tip') or 0),
            format="%.2f",
            key="tip_input"
        )
        receipt['tip'] = tip
        
        # Auto-calculate total based on components
        auto_calculated_total = subtotal + tax + service_fee + (discount or 0) + tip
        
        # Allow manual override with checkbox
        manual_override = st.checkbox("Manual total override", value=False)
        
        if manual_override:
            total = st.number_input(
                "**Total**",
                value=float(receipt.get('total', auto_calculated_total)),
                format="%.2f"
            )
        else:
            total = auto_calculated_total
            st.markdown(f"**Total:** ${total:.2f}")
        
        receipt['total'] = total
    
    # Calculate expected total
    expected_total = auto_calculated_total
    
    st.markdown("---")
    
    # Validation
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Items Sum", f"${sum(item['total_price'] for item in receipt['items']):.2f}")
    with col2:
        st.metric("Expected Total", f"${expected_total:.2f}")
    
    if abs(total - expected_total) > 0.50:
        st.warning(f"⚠️ Total (${total:.2f}) doesn't match expected (${expected_total:.2f})")
    else:
        st.success("✅ Totals look good!")
    
    # Store updated receipt
    st.session_state.receipt = receipt
    
    st.info("👉 Click 'Next' to set up your group")
