"""
FastAPI Backend for PDF Summarizer
Handles PDF upload, text extraction, and Claude AI summarization with LangSmith monitoring
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from typing import Dict
import anthropic
from pypdf import PdfReader
import io
from dotenv import load_dotenv
import traceback

# Try to import LangSmith traceable, but make it optional
try:
    from langsmith import traceable
except ImportError:
    # If LangSmith is not available, create a dummy decorator
    def traceable(name=None):
        def decorator(func):
            return func
        return decorator

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="PDF Summarizer API",
    description="API for extracting and summarizing PDF content using Claude AI",
    version="1.0.0"
)

# CORS Configuration - Allow Streamlit frontend to make requests
# In production, replace "*" with your specific frontend URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: ["https://your-frontend.railway.app"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load environment variables
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT_NAME", "pdf-summarizer")

# Enable LangSmith tracing if API key is present
if LANGSMITH_API_KEY:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = LANGSMITH_API_KEY
    os.environ["LANGCHAIN_PROJECT"] = LANGSMITH_PROJECT
    print(f"✅ LangSmith tracing enabled for project: {LANGSMITH_PROJECT}")
else:
    print("⚠️  LangSmith API key not found - tracing disabled")

# Validate API keys
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY environment variable is required")

# Initialize Anthropic client
anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# Constants
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB in bytes
ALLOWED_CONTENT_TYPES = ["application/pdf"]


def extract_text_from_pdf(pdf_file: bytes) -> str:
    """
    Extract text content from a PDF file using pypdf library.
    
    Args:
        pdf_file: PDF file content as bytes
        
    Returns:
        Extracted text as a string
        
    Raises:
        ValueError: If PDF is corrupted or cannot be read
    """
    try:
        # Create a PDF reader object from bytes
        pdf_reader = PdfReader(io.BytesIO(pdf_file))
        
        # Extract text from all pages
        text = ""
        for page_num, page in enumerate(pdf_reader.pages, 1):
            page_text = page.extract_text()
            if page_text:
                text += f"\n--- Page {page_num} ---\n{page_text}"
        
        if not text.strip():
            raise ValueError("No text content found in PDF. The PDF might be image-based or empty.")
        
        return text.strip()
    
    except Exception as e:
        raise ValueError(f"Failed to extract text from PDF: {str(e)}")


@traceable(name="summarize_with_claude")
def summarize_text_with_claude(text: str) -> str:
    """
    Summarize text using Claude 3.5 Sonnet with detailed bullet points.
    The @traceable decorator sends this function's execution to LangSmith for monitoring.
    
    Args:
        text: Text content to summarize
        
    Returns:
        Detailed summary with bullet points
        
    Raises:
        Exception: If Claude API call fails
    """
    try:
        # Construct the prompt for Claude
        # This prompt engineering ensures we get structured bullet-point output
        prompt = f"""You are a professional document summarizer. Your task is to read the document below and create a clear, concise summary with bullet points.

DO NOT reproduce the entire document. Instead, provide:
1. A brief 2-3 sentence overview at the top
2. Key points in bullet format (use • bullets)
3. Important insights, facts, or conclusions

Keep the summary to 300-500 words maximum.

DOCUMENT TO SUMMARIZE:
---
{text}
---

Now provide your summary:"""

        # Call Claude API
        # Using Claude 3 Haiku - fast and widely available
        message = anthropic_client.messages.create(
            model="claude-3-haiku-20240307",  # Claude 3 Haiku (available to all)
            max_tokens=2048,  # Enough for detailed summaries
            temperature=0.3,  # Lower temperature for more focused, consistent summaries
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        # Extract the summary from Claude's response
        summary = message.content[0].text
        
        return summary
    
    except anthropic.APIError as e:
        raise Exception(f"Claude API error: {str(e)}")
    except Exception as e:
        raise Exception(f"Summarization failed: {str(e)}")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "PDF Summarizer API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for Railway and monitoring.
    Verifies that API keys are configured.
    """
    return {
        "status": "healthy",
        "anthropic_configured": bool(ANTHROPIC_API_KEY),
        "langsmith_configured": bool(LANGSMITH_API_KEY)
    }


@app.post("/summarize")
async def summarize_pdf(file: UploadFile = File(...)) -> Dict:
    """
    Main endpoint: Upload a PDF and get an AI-generated summary.
    
    Process:
    1. Validate file type and size
    2. Extract text from PDF
    3. Send text to Claude for summarization
    4. Return structured summary with metadata
    
    Args:
        file: Uploaded PDF file (max 5MB)
        
    Returns:
        JSON response with summary, metadata, and status
        
    Raises:
        HTTPException: For various error conditions (file too large, invalid format, etc.)
    """
    
    # Step 1: Validate file type
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Only PDF files are allowed. Received: {file.content_type}"
        )
    
    # Step 2: Read and validate file size
    pdf_content = await file.read()
    file_size = len(pdf_content)
    
    if file_size > MAX_FILE_SIZE:
        file_size_mb = file_size / (1024 * 1024)
        raise HTTPException(
            status_code=400,
            detail=f"File too large ({file_size_mb:.2f}MB). Maximum allowed size is 5MB."
        )
    
    if file_size == 0:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty."
        )
    
    try:
        # Step 3: Extract text from PDF
        extracted_text = extract_text_from_pdf(pdf_content)
        
        # Step 4: Summarize with Claude (traced by LangSmith)
        summary = summarize_text_with_claude(extracted_text)
        
        # Step 5: Return structured response
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "summary": summary,
                "metadata": {
                    "filename": file.filename,
                    "file_size_mb": round(file_size / (1024 * 1024), 2),
                    "extracted_text_length": len(extracted_text),
                    "summary_length": len(summary)
                }
            }
        )
    
    except ValueError as e:
        # PDF extraction errors (corrupted PDF, no text, etc.)
        raise HTTPException(
            status_code=400,
            detail=f"PDF processing error: {str(e)}"
        )
    
    except Exception as e:
        # Any other unexpected errors - log the full traceback for debugging
        import traceback
        print("=" * 80)
        print("UNEXPECTED ERROR:")
        print(traceback.format_exc())
        print("=" * 80)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


# For local development
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
