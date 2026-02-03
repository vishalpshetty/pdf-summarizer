# 🧾 InstaSplit - AI Restaurant Bill Splitter

A production-ready web application for splitting restaurant bills among large groups. Features OCR-first receipt extraction with AI fallback, deterministic bill splitting with exact reconciliation, and a beautiful Streamlit interface.

## ✨ Features

- **📸 OCR-First Pipeline**: Local OCR processing (PaddleOCR/Tesseract) with Claude AI fallback only when needed for cost optimization
- **🎯 8MB Upload Limit**: Enforced at both frontend and backend with smart image preprocessing
- **💰 Exact Reconciliation**: Deterministic bill splitting with penny-perfect rounding
- **👥 Group Management**: Support for large groups with flexible item assignment
- **🔄 Share Modes**: Even split, quantity-based, or fraction-based sharing
- **📊 Detailed Breakdowns**: See exactly what each person owes with full transparency
- **💾 Export Options**: Download results as JSON or CSV
- **🔍 LangChain Tracing**: Full observability with LangSmith integration

## 🏗️ Architecture

### Tech Stack

- **Frontend**: Streamlit (Python)
- **Backend**: FastAPI (Python)
- **OCR**: PaddleOCR (preferred) or Tesseract (fallback)
- **LLM**: Anthropic Claude 3.5 Sonnet via LangChain
- **Deployment**: Docker + Railway

### Pipeline Flow

```
Image Upload (≤8MB)
    ↓
Image Preprocessing
    ↓
Local OCR (PaddleOCR/Tesseract)
    ↓
Deterministic Parser
    ↓
Confidence Check
    ↓
High Confidence? → Use OCR Result
Low Confidence? → Claude Text-to-JSON
Very Poor OCR? → Claude Vision (if enabled)
    ↓
Validated Receipt JSON
    ↓
Bill Splitting Engine
    ↓
Exact Reconciliation
    ↓
Results + Export
```

## 📁 Project Structure

```
InstaSplit/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI application
│   │   ├── schemas.py              # Pydantic models
│   │   ├── ocr/
│   │   │   ├── base.py             # OCR interface
│   │   │   ├── paddle_ocr.py       # PaddleOCR implementation
│   │   │   └── tesseract_ocr.py    # Tesseract implementation
│   │   ├── extraction/
│   │   │   ├── parser.py           # Deterministic parser
│   │   │   └── llm_extractor.py    # Claude-based extraction
│   │   ├── splitting/
│   │   │   └── engine.py           # Bill splitting logic
│   │   └── utils/
│   │       └── image_processing.py # Image preprocessing
│   ├── tests/
│   │   └── test_splitting_engine.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── streamlit_app.py            # Main app
│   ├── components/
│   │   ├── upload.py               # Step 1: Upload
│   │   ├── review.py               # Step 2: Review
│   │   ├── group_setup.py          # Step 3: Group
│   │   ├── assign_items.py         # Step 4: Assign
│   │   └── results.py              # Step 5: Results
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose (for containerized deployment)
- Anthropic API key

### Local Development (Docker Compose)

1. **Clone the repository**
   ```bash
   cd "/Users/vishalhp/AI Folder/InstaSplit"
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

3. **Start services**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - Frontend: http://localhost:8501
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Local Development (Without Docker)

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export ANTHROPIC_API_KEY=your_key_here
export LANGCHAIN_TRACING_V2=true  # optional
export LANGCHAIN_API_KEY=your_langsmith_key  # optional

# Run server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend

```bash
cd frontend

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set backend URL
export BACKEND_URL=http://localhost:8000

# Run Streamlit
streamlit run streamlit_app.py
```

## 🧪 Testing

Run the test suite:

```bash
cd backend
pytest tests/ -v
```

Test coverage includes:
- Even split scenarios
- Quantity-based splits
- Proportional vs. even discounts
- Tax and tip allocation
- Rounding reconciliation
- Service fee distribution

## 📊 API Endpoints

### `POST /receipt/extract`

Extract receipt data from an image.

**Request:**
- `file`: Image file (multipart/form-data, max 8MB)

**Response:**
```json
{
  "receipt": {
    "merchant_name": "Restaurant Name",
    "items": [...],
    "subtotal": 50.00,
    "tax": 5.00,
    "tip": 10.00,
    "total": 65.00,
    "confidence": {...}
  },
  "processing_time_ms": 1234,
  "ocr_method": "PaddleOCR",
  "llm_used": false,
  "vision_used": false
}
```

### `POST /split/calculate`

Calculate bill split.

**Request:**
```json
{
  "receipt": {...},
  "group": {
    "people": [
      {"id": "p1", "name": "Alice"},
      {"id": "p2", "name": "Bob"}
    ]
  },
  "assignments": [
    {
      "item_id": "item1",
      "shares": [
        {"person_id": "p1", "split_mode": "even"},
        {"person_id": "p2", "split_mode": "even"}
      ]
    }
  ],
  "options": {
    "tip_mode": "proportional",
    "discount_mode": "proportional",
    "tax_mode": "proportional"
  }
}
```

**Response:**
```json
{
  "breakdowns": [
    {
      "person_id": "p1",
      "person_name": "Alice",
      "items_subtotal": 25.00,
      "tax_share": 2.50,
      "tip_share": 5.00,
      "total_owed": 32.50
    }
  ],
  "reconciliation": {
    "target_total": 65.00,
    "calculated_total": 65.00,
    "difference": 0.00,
    "pennies_adjusted": 0
  }
}
```

## 🚢 Railway Deployment

### Backend Deployment

1. Create a new Railway project
2. Add a new service from GitHub
3. Select the `backend` directory
4. Set environment variables:
   - `ANTHROPIC_API_KEY`
   - `LANGCHAIN_TRACING_V2` (optional)
   - `LANGCHAIN_API_KEY` (optional)
   - `ALLOW_VISION_FALLBACK` (optional, default: false)
5. Deploy!

Railway will automatically detect the Dockerfile and deploy.

### Frontend Deployment

1. In the same Railway project, add another service
2. Select the `frontend` directory
3. Set environment variables:
   - `BACKEND_URL` (URL of your deployed backend)
4. Deploy!

### Cost Optimization Tips

- Keep `ALLOW_VISION_FALLBACK=false` to minimize AI costs
- The OCR-first pipeline processes most receipts without LLM calls
- Vision model is only used as last resort when enabled
- Typical cost: ~$0.001-0.01 per receipt (mostly OCR-only)

## 🔧 Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | Yes | - | Anthropic API key for Claude |
| `LANGCHAIN_TRACING_V2` | No | `false` | Enable LangSmith tracing |
| `LANGCHAIN_API_KEY` | No | - | LangSmith API key |
| `LANGCHAIN_PROJECT` | No | `instasplit` | LangSmith project name |
| `ALLOW_VISION_FALLBACK` | No | `false` | Enable Claude vision as fallback |
| `BACKEND_URL` | Frontend only | `http://localhost:8000` | Backend API URL |

### Feature Flags

- **OCR-First**: Always enabled (core feature)
- **Vision Fallback**: Controlled by `ALLOW_VISION_FALLBACK`
- **LangChain Tracing**: Controlled by `LANGCHAIN_TRACING_V2`

## 📝 Usage Guide

### Step-by-Step Workflow

1. **Upload Receipt**
   - Take a clear photo of your receipt
   - Ensure good lighting and all text is readable
   - Upload (max 8MB)

2. **Review & Edit**
   - Verify extracted items and prices
   - Add or remove items
   - Correct any OCR mistakes
   - Adjust totals if needed

3. **Set Up Group**
   - Enter number of people
   - Add names for each person

4. **Assign Items**
   - For each item, select who had it
   - Items can be shared (even split or by quantity)
   - Configure tip/tax/discount split modes

5. **View Results**
   - See what each person owes
   - Review detailed breakdowns
   - Export as JSON or CSV
   - Share results via text

### Tips for Best Results

- **Photography**: Take photos straight-on, not at an angle
- **Lighting**: Ensure even lighting without shadows or glare
- **Focus**: Make sure text is sharp and in focus
- **Format**: JPG and PNG work best; HEIC is auto-converted
- **Size**: Images are auto-resized to optimize OCR speed

## 🏗️ Development

### Adding New OCR Engines

1. Create new class in `backend/app/ocr/` implementing `OCRInterface`
2. Add to `get_ocr_extractor()` priority list
3. Update requirements.txt with new dependencies

### Extending Split Logic

The splitting engine in `backend/app/splitting/engine.py` is fully modular:
- Add new split modes to `SplitMode` enum
- Implement new allocation logic in `SplittingEngine`
- Add tests in `tests/test_splitting_engine.py`

## 🐛 Troubleshooting

### "Could not connect to backend"
- Ensure backend is running on correct port
- Check `BACKEND_URL` environment variable
- Verify firewall settings

### "OCR extraction failed"
- Try a clearer photo
- Ensure receipt is well-lit
- Check that text is readable
- Consider enabling vision fallback

### "Rounding doesn't match total"
- This should never happen! The reconciliation engine ensures exact matches
- If you see this, please report as a bug

### "PaddleOCR not working"
- Falls back to Tesseract automatically
- Check Docker logs for errors
- Ensure sufficient memory allocation

## 📜 License

MIT License - feel free to use for personal or commercial projects.

## 🤝 Contributing

This is a personal project, but suggestions and bug reports are welcome!

## 🙏 Acknowledgments

- [Anthropic Claude](https://www.anthropic.com/) for the LLM capabilities
- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) for excellent OCR
- [Streamlit](https://streamlit.io/) for rapid UI development
- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework

---

**Made with ❤️ for splitting bills fairly and easily**
