# 🚀 Quick Start Guide

Follow these steps to get your PDF Summarizer running locally in under 5 minutes!

## Prerequisites

- Python 3.9 or higher installed
- Your Anthropic API key ready
- (Optional) LangSmith API key for monitoring

## Step 1: Set Up the Backend

```bash
# Navigate to backend folder
cd backend

# Install dependencies
pip3 install -r requirements.txt

# Create environment file
cp .env.example .env
```

Now edit `backend/.env` and add your API keys:

```bash
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
LANGSMITH_API_KEY=lsv2_pt_xxxxxxxxxxxxx  # Optional
LANGSMITH_PROJECT_NAME=pdf-summarizer
```

Start the backend server:

```bash
# Run the backend
python3 -m uvicorn main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

Visit `http://localhost:8000/docs` to see the interactive API documentation!

## Step 2: Set Up the Frontend

Open a **NEW terminal window** (keep the backend running), then:

```bash
# Navigate to frontend folder
cd frontend

# Install dependencies
pip3 install -r requirements.txt

# Create environment file
cp .env.example .env
```

Edit `frontend/.env`:

```bash
BACKEND_URL=http://localhost:8000
```

Start the Streamlit app:

```bash
streamlit run app.py
```

The app will automatically open in your browser at `http://localhost:8501`

## Step 3: Test the App

1. You should see the "AI PDF Summarizer" interface
2. Click "Browse files" to upload a PDF (max 5MB)
3. Click "Generate Summary"
4. Watch the loading spinner (takes 30-60 seconds)
5. View your detailed bullet-point summary!

## 🎉 That's It!

Your app is now running locally. Try uploading a research paper, article, or report to test it out.

## Next Steps

- Read the `README.md` for deployment instructions
- Check out `DEPLOYMENT.md` for Railway deployment details
- Visit your LangSmith dashboard to see the traced API calls
- Explore the code to understand how it works!

## Troubleshooting

### Backend won't start

**Error:** `command not found: uvicorn`
- **Fix:** Use `python3 -m uvicorn main:app --reload --port 8000` instead

**Error:** `ANTHROPIC_API_KEY environment variable is required`
- **Fix:** Make sure you created `backend/.env` and added your API key

### Frontend can't connect

**Error:** `Could not connect to backend server`
- **Fix:** Make sure the backend is running on port 8000
- Check that `frontend/.env` has `BACKEND_URL=http://localhost:8000`

### PDF upload fails

**Error:** `File too large`
- **Fix:** Compress your PDF or use a smaller file (max 5MB)

**Error:** `No text content found in PDF`
- **Fix:** The PDF might be image-based (scanned). Use a text-based PDF instead

## Learning Points

As you explore the code, pay attention to:

1. **Backend (`backend/main.py`)**:
   - How FastAPI handles file uploads with `UploadFile`
   - PDF text extraction using `pypdf`
   - Claude API integration with the `anthropic` SDK
   - LangSmith tracing with the `@traceable` decorator
   - Error handling and HTTP status codes

2. **Frontend (`frontend/app.py`)**:
   - Streamlit's simple file uploader widget
   - Making HTTP POST requests to the backend
   - Using spinners for loading states
   - Displaying errors and success messages

3. **Prompt Engineering**:
   - Look at how the prompt is structured in `summarize_text_with_claude()`
   - Try modifying it to change the summary style!

Enjoy learning! 🚀
