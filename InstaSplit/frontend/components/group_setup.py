"""
Step 3: Set up group members.
"""
import streamlit as st
import uuid


def render_group_setup_step():
    """Render the group setup step."""
    st.markdown('<div class="step-header">Step 3: Set Up Group</div>', unsafe_allow_html=True)
    
    st.info("👥 Add everyone in your group who will be splitting the bill")
    
    # Initialize group if not exists
    if not st.session_state.group:
        st.session_state.group = {'people': []}
    
    group = st.session_state.group
    
    # Number of people selector
    num_people = st.number_input(
        "Number of people",
        min_value=1,
        max_value=20,
        value=max(2, len(group['people'])),
        step=1
    )
    
    # Adjust people list
    while len(group['people']) < num_people:
        group['people'].append({
            'id': str(uuid.uuid4()),
            'name': f"Person {len(group['people']) + 1}"
        })
    
    while len(group['people']) > num_people:
        group['people'].pop()
    
    st.markdown("### Enter Names")
    
    # Name inputs
    cols_per_row = 3
    for i in range(0, len(group['people']), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, col in enumerate(cols):
            idx = i + j
            if idx < len(group['people']):
                with col:
                    person = group['people'][idx]
                    person['name'] = st.text_input(
                        f"Person {idx + 1}",
                        value=person['name'],
                        key=f"person_name_{idx}"
                    )
    
    # Show summary
    st.markdown("### Group Summary")
    st.write(f"**Total people:** {len(group['people'])}")
    
    people_names = [p['name'] for p in group['people']]
    st.write(", ".join(people_names))
    
    # Validate
    if any(not p['name'].strip() for p in group['people']):
        st.warning("⚠️ Please enter names for all group members")
    else:
        st.success("✅ Group is ready!")
        st.info("👉 Click 'Next' to assign items to people")
    
    # Store group
    st.session_state.group = group
