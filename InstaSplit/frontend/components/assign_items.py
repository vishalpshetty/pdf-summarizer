"""
Step 4: Assign items to people.
"""
import streamlit as st


def render_assign_items_step():
    """Render the item assignment step."""
    st.markdown('<div class="step-header">Step 4: Assign Items</div>', unsafe_allow_html=True)
    
    if not st.session_state.receipt or not st.session_state.group:
        st.warning("⚠️ Missing receipt or group data")
        return
    
    receipt = st.session_state.receipt
    group = st.session_state.group
    
    st.info("🍽️ Select who ate each item. Items can be shared by multiple people.")
    
    # Options
    col1, col2, col3 = st.columns(3)
    with col1:
        tip_mode = st.selectbox(
            "Tip Split Mode",
            options=['proportional', 'even'],
            index=0,
            help="Proportional: based on what you ate. Even: split equally"
        )
        st.session_state.split_options['tip_mode'] = tip_mode
    
    with col2:
        discount_mode = st.selectbox(
            "Discount Split Mode",
            options=['proportional', 'even'],
            index=0,
            help="How to allocate discounts"
        )
        st.session_state.split_options['discount_mode'] = discount_mode
    
    with col3:
        tax_mode = st.selectbox(
            "Tax Split Mode",
            options=['proportional', 'even'],
            index=0,
            help="How to allocate tax"
        )
        st.session_state.split_options['tax_mode'] = tax_mode
    
    st.markdown("---")
    st.markdown("### Assign Items to People")
    
    # Initialize assignments
    if not st.session_state.assignments:
        st.session_state.assignments = {}
    
    assignments = st.session_state.assignments
    people = group['people']
    
    # Assign each item
    for idx, item in enumerate(receipt['items']):
        item_id = item['id']
        
        with st.expander(f"**{item['name']}** - ${item['total_price']:.2f}", expanded=True):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Multi-select for people
                selected_people = st.multiselect(
                    "Who had this item?",
                    options=[p['id'] for p in people],
                    format_func=lambda pid: next(p['name'] for p in people if p['id'] == pid),
                    default=assignments.get(item_id, {}).get('people', []),
                    key=f"item_{idx}_people"
                )
                
                # Store assignment
                if item_id not in assignments:
                    assignments[item_id] = {}
                assignments[item_id]['people'] = selected_people
            
            with col2:
                # Split mode
                if len(selected_people) > 1:
                    split_mode = st.selectbox(
                        "Split mode",
                        options=['even', 'quantity'],
                        index=0,
                        key=f"item_{idx}_split_mode",
                        help="Even: equal split. Quantity: specify portions"
                    )
                    assignments[item_id]['split_mode'] = split_mode
                    
                    # If quantity mode, show quantity inputs
                    if split_mode == 'quantity':
                        st.markdown("**Quantities:**")
                        quantities = {}
                        for person_id in selected_people:
                            person_name = next(p['name'] for p in people if p['id'] == person_id)
                            qty = st.number_input(
                                person_name,
                                min_value=0.1,
                                max_value=float(item['quantity']),
                                value=1.0,
                                step=0.5,
                                key=f"item_{idx}_qty_{person_id}"
                            )
                            quantities[person_id] = qty
                        assignments[item_id]['quantities'] = quantities
                else:
                    assignments[item_id]['split_mode'] = 'even'
    
    # Show assignment summary
    st.markdown("---")
    st.markdown("### Assignment Summary")
    
    for person in people:
        person_items = []
        for item in receipt['items']:
            if item['id'] in assignments and person['id'] in assignments[item['id']]['people']:
                person_items.append(item['name'])
        
        if person_items:
            st.write(f"**{person['name']}:** {', '.join(person_items)}")
        else:
            st.write(f"**{person['name']}:** *(no items assigned)*")
    
    # Check if all items are assigned
    unassigned_items = [
        item['name'] for item in receipt['items']
        if item['id'] not in assignments or not assignments[item['id']]['people']
    ]
    
    if unassigned_items:
        st.warning(f"⚠️ Unassigned items: {', '.join(unassigned_items)}")
    else:
        st.success("✅ All items assigned!")
    
    st.info("👉 Click 'Next' to see the results")
    
    # Store assignments
    st.session_state.assignments = assignments
