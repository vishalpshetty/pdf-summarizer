"""
InstaSplit - Restaurant Bill Splitter
Streamlit frontend with 5-step flow.
"""
import streamlit as st
import os

from components.upload import render_upload_step
from components.review import render_review_step
from components.group_setup import render_group_setup_step
from components.assign_items import render_assign_items_step
from components.results import render_results_step

# Page configuration
st.set_page_config(
    page_title="InstaSplit - Bill Splitter",
    page_icon="🧾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .step-header {
        font-size: 1.8rem;
        font-weight: 600;
        color: #2c3e50;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .warning-box {
        padding: 1rem;
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'receipt' not in st.session_state:
    st.session_state.receipt = None
if 'group' not in st.session_state:
    st.session_state.group = None
if 'assignments' not in st.session_state:
    st.session_state.assignments = {}
if 'split_options' not in st.session_state:
    st.session_state.split_options = {
        'tip_mode': 'proportional',
        'discount_mode': 'proportional',
        'tax_mode': 'proportional'
    }
if 'results' not in st.session_state:
    st.session_state.results = None

# Backend URL
backend_url = os.getenv('BACKEND_URL', 'http://localhost:8000')

# Main header
st.markdown('<div class="main-header">🧾 InstaSplit</div>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #7f8c8d; margin-bottom: 2rem;">Split restaurant bills with your group easily</p>', unsafe_allow_html=True)

# Progress indicator
steps = ["Upload", "Review", "Group", "Assign", "Results"]
current_step = st.session_state.step - 1

cols = st.columns(5)
for idx, (col, step_name) in enumerate(zip(cols, steps)):
    with col:
        if idx < current_step:
            st.markdown(f"✅ **{step_name}**")
        elif idx == current_step:
            st.markdown(f"🔵 **{step_name}**")
        else:
            st.markdown(f"⚪ {step_name}")

st.markdown("---")

# Render current step
if st.session_state.step == 1:
    render_upload_step(backend_url)

elif st.session_state.step == 2:
    render_review_step()

elif st.session_state.step == 3:
    render_group_setup_step()

elif st.session_state.step == 4:
    render_assign_items_step()

elif st.session_state.step == 5:
    render_results_step(backend_url)

# Navigation buttons at bottom
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    if st.session_state.step > 1:
        if st.button("⬅️ Back", use_container_width=True):
            st.session_state.step -= 1
            st.rerun()

with col3:
    if st.session_state.step < 5:
        # Check if can proceed
        can_proceed = False
        if st.session_state.step == 1 and st.session_state.receipt:
            can_proceed = True
        elif st.session_state.step == 2 and st.session_state.receipt:
            can_proceed = True
        elif st.session_state.step == 3 and st.session_state.group:
            can_proceed = True
        elif st.session_state.step == 4:
            can_proceed = True
        
        if st.button("Next ➡️", disabled=not can_proceed, use_container_width=True):
            st.session_state.step += 1
            st.rerun()

# Sidebar with help
with st.sidebar:
    st.header("Help")
    st.markdown("""
    ### How to use:
    
    1. **Upload**: Take or upload a photo of your receipt
    2. **Review**: Verify extracted items and totals
    3. **Group**: Add people in your group
    4. **Assign**: Mark who ate what
    5. **Results**: See what each person owes
    
    ### Tips:
    - Take clear, well-lit photos
    - Ensure all text is readable
    - Items can be shared by multiple people
    - Tax and tip are split automatically
    """)
    
    if st.button("Start Over"):
        for key in ['receipt', 'group', 'assignments', 'results']:
            st.session_state[key] = None
        st.session_state.step = 1
        st.rerun()
