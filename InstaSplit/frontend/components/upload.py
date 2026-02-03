"""
Step 1: Upload receipt image.
"""
import streamlit as st
import requests
import time
from PIL import Image
import io


def render_upload_step(backend_url: str):
    """Render the upload step."""
    st.markdown('<div class="step-header">Step 1: Upload Receipt</div>', unsafe_allow_html=True)
    
    st.info("📸 Take a photo or upload an image of your receipt. Max size: 8 MB")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose receipt image",
        type=['jpg', 'jpeg', 'png', 'heic'],
        help="Supported formats: JPG, PNG, HEIC (max 8 MB)"
    )
    
    if uploaded_file is not None:
        # Show uploaded image
        col1, col2 = st.columns([1, 2])
        
        with col1:
            try:
                # Reset file pointer to beginning
                uploaded_file.seek(0)
                
                # Try to open and display the image
                # For HEIC files, we'll convert to display format
                if uploaded_file.name.lower().endswith('.heic'):
                    try:
                        # Try to register HEIC support
                        from pillow_heif import register_heif_opener
                        register_heif_opener()
                        image = Image.open(uploaded_file)
                        st.image(image, caption="Uploaded Receipt (HEIC)", use_container_width=True)
                    except ImportError:
                        # If pillow_heif not available in frontend, just show a placeholder
                        st.info("📸 HEIC image uploaded. Preview not available, but will be processed by backend.")
                        st.write(f"**File:** {uploaded_file.name}")
                        st.write(f"**Size:** {len(uploaded_file.getvalue()) / 1024:.1f} KB")
                else:
                    # For regular images (JPG, PNG)
                    st.image(uploaded_file, caption="Uploaded Receipt", use_container_width=True)
            except Exception as e:
                # Fallback: show file info if image preview fails
                st.warning(f"Preview not available, but file will be processed.")
                st.write(f"**File:** {uploaded_file.name}")
                st.write(f"**Size:** {len(uploaded_file.getvalue()) / 1024:.1f} KB")
        
        with col2:
            # Check file size
            file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
            
            if file_size_mb > 8:
                st.error(f"❌ File too large: {file_size_mb:.2f} MB (max 8 MB)")
                st.stop()
            
            st.success(f"✅ File size: {file_size_mb:.2f} MB")
            
            if st.button("🔍 Extract Receipt Data", type="primary", use_container_width=True):
                extract_receipt(backend_url, uploaded_file)


def extract_receipt(backend_url: str, uploaded_file):
    """Call backend to extract receipt data."""
    with st.spinner("🔄 Processing receipt... This may take a moment."):
        try:
            # Reset file pointer and prepare file for upload
            uploaded_file.seek(0)
            file_bytes = uploaded_file.getvalue()
            files = {
                'file': (uploaded_file.name, file_bytes, uploaded_file.type)
            }
            
            # Call backend
            start_time = time.time()
            response = requests.post(
                f"{backend_url}/receipt/extract",
                files=files,
                timeout=60
            )
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                receipt = data['receipt']
                
                # Store in session state
                st.session_state.receipt = receipt
                st.session_state.extraction_metadata = {
                    'processing_time_ms': data['processing_time_ms'],
                    'ocr_method': data['ocr_method'],
                    'llm_used': data['llm_used'],
                    'vision_used': data['vision_used']
                }
                
                # Show success
                st.success(f"✅ Receipt extracted successfully in {elapsed:.2f}s!")
                
                # Show extraction info
                with st.expander("📊 Extraction Details"):
                    st.write(f"**OCR Method:** {data['ocr_method']}")
                    st.write(f"**LLM Used:** {'Yes' if data['llm_used'] else 'No'}")
                    st.write(f"**Vision Model Used:** {'Yes' if data['vision_used'] else 'No'}")
                    st.write(f"**Processing Time:** {data['processing_time_ms']:.0f} ms")
                    st.write(f"**Confidence:** {receipt.get('confidence', {}).get('overall', 0):.2%}")
                
                # Show quick preview
                st.markdown("### Quick Preview")
                st.write(f"**Merchant:** {receipt.get('merchant_name', 'Unknown')}")
                st.write(f"**Total:** ${receipt['total']:.2f}")
                st.write(f"**Items:** {len(receipt['items'])}")
                
                st.info("👉 Click 'Next' to review and edit the extracted data")
                
            elif response.status_code == 413:
                st.error("❌ File too large (max 8 MB)")
            elif response.status_code == 422:
                error_detail = response.json().get('detail', 'Could not extract receipt data')
                st.error(f"❌ {error_detail}")
                st.warning("💡 Try taking a clearer photo with better lighting")
            else:
                st.error(f"❌ Error: {response.status_code}")
                st.write(response.json())
                
        except requests.exceptions.Timeout:
            st.error("❌ Request timed out. Please try again.")
        except requests.exceptions.ConnectionError:
            st.error(f"❌ Could not connect to backend at {backend_url}")
            st.info("💡 Make sure the backend server is running")
        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")
