# PDF Summarizer AI App

An AI-powered PDF summarization application that extracts content from PDFs and generates detailed summaries using Claude 3.5 Sonnet.

## 🏗️ Architecture

- **Frontend**: Streamlit (Simple Python UI framework)
- **Backend**: FastAPI (Modern Python API framework)
- **AI Model**: Claude 3.5 Sonnet (via Anthropic API)
- **Monitoring**: LangSmith (Tracks costs, latency, and performance)
- **Deployment**: Railway (PaaS for both services)
- **Git Flow**: Push-to-Deploy from GitHub

## 📁 Project Structure

```
pdf-summarizer/
├── backend/          # FastAPI service
│   ├── main.py       # API endpoints and PDF processing
│   ├── requirements.txt
│   ├── .env.example
│   └── Procfile      # Railway deployment config
├── frontend/         # Streamlit UI
│   ├── app.py        # Main Streamlit application
│   ├── requirements.txt
│   ├── .env.example
│   └── Procfile      # Railway deployment config
├── .gitignore
└── README.md
```

## 🚀 Features

- ✅ Upload PDF documents (up to 5MB)
- ✅ Extract text from multi-page PDFs
- ✅ AI-powered summarization with bullet points
- ✅ Real-time loading indicators
- ✅ Error handling and user feedback
- ✅ Cost and latency monitoring via LangSmith

## 🛠️ Local Development Setup

### Prerequisites

- Python 3.9+ installed
- Anthropic API key
- LangSmith API key (optional for local testing)

### Backend Setup

```bash
cd backend
pip3 install -r requirements.txt

# Create .env file with your API keys
cp .env.example .env
# Edit .env and add your keys

# Run the backend server
python3 -m uvicorn main:app --reload --port 8000
```

The backend will be available at `http://localhost:8000`
API docs will be at `http://localhost:8000/docs`

### Frontend Setup

```bash
cd frontend
pip3 install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and set BACKEND_URL=http://localhost:8000

# Run the Streamlit app
python3 -m streamlit run app.py
```

The frontend will open in your browser at `http://localhost:8501`

## 🌐 Railway Deployment

### Step 1: Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit: PDF Summarizer app"
git remote add origin <your-github-repo-url>
git push -u origin main
```

### Step 2: Deploy Backend on Railway

1. Go to [Railway](https://railway.app/) and create a new project
2. Connect your GitHub repository
3. Select the `backend` folder as the root directory
4. Add environment variables:
   - `ANTHROPIC_API_KEY`
   - `LANGSMITH_API_KEY`
   - `LANGSMITH_PROJECT_NAME`
5. Railway will automatically detect the Procfile and deploy
6. Copy the deployed backend URL (e.g., `https://your-app.railway.app`)

### Step 3: Deploy Frontend on Railway

1. Create another new project in Railway
2. Connect the same GitHub repository
3. Select the `frontend` folder as the root directory
4. Add environment variable:
   - `BACKEND_URL` = Your backend URL from Step 2
5. Railway will deploy the Streamlit app
6. Access your app via the Railway-provided URL

### Step 4: Set up Auto-Deploy

Railway automatically sets up GitHub webhook for push-to-deploy. Every push to `main` branch will trigger a new deployment.

## 📚 Learning Resources

### Key Concepts You'll Learn

1. **FastAPI Basics**:
   - Creating REST APIs with automatic documentation
   - File upload handling with `UploadFile`
   - CORS configuration for frontend-backend communication
   - Error handling and HTTP status codes

2. **Streamlit Basics**:
   - Building web UIs with pure Python
   - File uploaders and form handling
   - Displaying loading states with spinners
   - Error messages and success notifications

3. **PDF Processing**:
   - Using `pypdf` library to extract text
   - Handling multi-page documents
   - Managing file size limits

4. **Claude API**:
   - Using Anthropic's Python SDK
   - Prompt engineering for summarization
   - Token management and context limits

5. **LangSmith Integration**:
   - Tracing LLM calls for debugging
   - Monitoring costs and performance
   - Analyzing prompt effectiveness

6. **Railway Deployment**:
   - Platform-as-a-Service (PaaS) deployment
   - Environment variable management
   - GitHub integration and CI/CD

## 🔧 Testing the App

1. Start both backend and frontend locally
2. Open the Streamlit UI in your browser
3. Upload a sample PDF (try a research paper, article, or report)
4. Watch the loading indicator while processing
5. View the detailed bullet-point summary
6. Check LangSmith dashboard to see the traced API call

## 🐛 Common Issues and Solutions

### Issue: "Connection refused" error
- **Solution**: Make sure the backend is running and the `BACKEND_URL` in frontend `.env` is correct

### Issue: "File too large" error
- **Solution**: PDF must be under 5MB. Compress the PDF or use a smaller file

### Issue: "Corrupted PDF" error
- **Solution**: Ensure the PDF is valid and not password-protected

### Issue: Railway deployment fails
- **Solution**: Check the build logs in Railway dashboard. Ensure `Procfile` and `requirements.txt` are correct

## 📊 Monitoring with LangSmith

After deployment, visit your LangSmith dashboard to see:
- **Traces**: Every Claude API call with inputs/outputs
- **Cost**: Token usage and estimated costs per request
- **Latency**: Response times for debugging performance
- **Errors**: Failed API calls for troubleshooting

## 📖 Next Steps to Enhance

Once you understand the basics, try adding:
- Support for multiple file formats (DOCX, TXT)
- Save summaries to a database
- User authentication
- Batch processing multiple PDFs
- Different summary styles (brief, detailed, technical)
- Export summaries as PDF or DOCX

## 🤝 Contributing

This is a learning project! Feel free to:
- Add new features
- Improve error handling
- Enhance the UI
- Optimize the summarization prompts

## 📝 License

MIT License - Feel free to use this project for learning!

---

**Happy Learning! 🚀**
