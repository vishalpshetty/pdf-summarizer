"""
Streamlit Frontend for PDF Summarizer
Simple UI for uploading PDFs and displaying AI-generated summaries
"""

import streamlit as st
import requests
import os
from typing import Optional

# Page configuration
st.set_page_config(
    page_title="PDF Summarizer",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Load backend URL from environment variable
# For local development: http://localhost:8000
# For Railway production: Your Railway backend URL
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Constants
MAX_FILE_SIZE_MB = 5
ALLOWED_FILE_TYPES = ["pdf"]


def display_header():
    """Display the app header and description"""
    st.title("📄 AI PDF Summarizer")
    st.markdown("""
    Upload a PDF document and get an AI-generated summary with detailed bullet points.
    
    **Powered by:**
    - 🤖 Claude 3.5 Sonnet (Anthropic)
    - 📊 LangSmith (Cost & Latency Monitoring)
    """)
    st.divider()


def validate_file(uploaded_file) -> tuple[bool, Optional[str]]:
    """
    Validate the uploaded file.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if uploaded_file is None:
        return False, "Please upload a PDF file"
    
    # Check file size
    file_size_mb = uploaded_file.size / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        return False, f"File too large ({file_size_mb:.2f}MB). Maximum size is {MAX_FILE_SIZE_MB}MB."
    
    if file_size_mb == 0:
        return False, "Uploaded file is empty."
    
    # Check file type
    if uploaded_file.type != "application/pdf":
        return False, f"Invalid file type. Only PDF files are allowed."
    
    return True, None


def call_backend_api(uploaded_file) -> dict:
    """
    Send the PDF to the backend API for processing.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        
    Returns:
        Response JSON from backend
        
    Raises:
        requests.RequestException: If API call fails
    """
    # Prepare the file for upload
    files = {
        "file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")
    }
    
    # Make POST request to backend
    response = requests.post(
        f"{BACKEND_URL}/summarize",
        files=files,
        timeout=120  # 2 minute timeout for large PDFs
    )
    
    # Raise exception for bad status codes
    response.raise_for_status()
    
    return response.json()


def display_summary(summary_data: dict):
    """
    Display the summary and metadata in a nice format.
    
    Args:
        summary_data: Response data from backend containing summary and metadata
    """
    st.success("✅ Summary generated successfully!")
    
    # Display metadata in an expander
    with st.expander("📊 Document Information", expanded=False):
        metadata = summary_data.get("metadata", {})
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("File Name", metadata.get("filename", "N/A"))
            st.metric("File Size", f"{metadata.get('file_size_mb', 0):.2f} MB")
        
        with col2:
            st.metric("Extracted Text", f"{metadata.get('extracted_text_length', 0):,} chars")
            st.metric("Summary Length", f"{metadata.get('summary_length', 0):,} chars")
    
    st.divider()
    
    # Display the summary
    st.subheader("📝 Summary")
    summary_text = summary_data.get("summary", "No summary available")
    
    # Display in a nice container
    st.markdown(summary_text)


def display_error(error_message: str):
    """
    Display error message to the user.
    
    Args:
        error_message: Error message to display
    """
    st.error(f"❌ **Error:** {error_message}")


def main():
    """Main application logic"""
    
    # Display header
    display_header()
    
    # File uploader
    st.subheader("📤 Upload PDF Document")
    uploaded_file = st.file_uploader(
        "Choose a PDF file (max 5MB)",
        type=ALLOWED_FILE_TYPES,
        help="Upload a PDF document to get an AI-generated summary with key points"
    )
    
    # Process button
    if uploaded_file is not None:
        # Show file details
        file_size_mb = uploaded_file.size / (1024 * 1024)
        st.info(f"📎 **{uploaded_file.name}** ({file_size_mb:.2f} MB)")
        
        # Validate file before processing
        is_valid, error_message = validate_file(uploaded_file)
        
        if not is_valid:
            display_error(error_message)
            return
        
        # Process button
        if st.button("🚀 Generate Summary", type="primary", use_container_width=True):
            
            # Show loading spinner while processing
            with st.spinner("🤖 Processing PDF and generating summary... This may take 30-60 seconds."):
                try:
                    # Call backend API
                    result = call_backend_api(uploaded_file)
                    
                    # Display the summary
                    if result.get("success"):
                        display_summary(result)
                    else:
                        display_error("Failed to generate summary. Please try again.")
                
                except requests.exceptions.Timeout:
                    display_error("Request timed out. The PDF might be too large or complex. Please try a smaller file.")
                
                except requests.exceptions.ConnectionError:
                    display_error(f"Could not connect to backend server at {BACKEND_URL}. Please ensure the backend is running.")
                
                except requests.exceptions.HTTPError as e:
                    # Extract error message from response if available
                    try:
                        error_detail = e.response.json().get("detail", str(e))
                    except:
                        error_detail = str(e)
                    display_error(f"Backend error: {error_detail}")
                
                except Exception as e:
                    display_error(f"Unexpected error: {str(e)}")
    
    # Footer with instructions
    st.divider()
    st.markdown("""
    ### 💡 Tips:
    - Works best with text-based PDFs (not scanned images)
    - Multi-page documents are fully supported
    - The AI will extract key points and provide detailed insights
    - Check LangSmith dashboard to monitor API costs and latency
    
    ### 🔧 Tech Stack:
    - **Frontend:** Streamlit (Python web framework)
    - **Backend:** FastAPI (REST API)
    - **AI Model:** Claude 3.5 Sonnet
    - **Monitoring:** LangSmith
    - **Deployment:** Railway
    """)


if __name__ == "__main__":
    main()
