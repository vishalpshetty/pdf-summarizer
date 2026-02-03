# Development Guide

Guide for developers working on InstaSplit.

## Development Setup

### Prerequisites

- Python 3.11+
- Docker Desktop (optional but recommended)
- Git
- Code editor (VS Code recommended)

### First Time Setup

1. **Clone and Setup**
   ```bash
   cd "/Users/vishalhp/AI Folder/InstaSplit"
   ```

2. **Environment Variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Choose Development Method**

   **Option A: Docker Compose (Recommended)**
   ```bash
   docker-compose up --build
   ```

   **Option B: Native Python**
   See README.md for detailed instructions

## Project Architecture

### Backend Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app, endpoints
│   ├── schemas.py           # Pydantic models
│   ├── ocr/                 # OCR implementations
│   │   ├── base.py          # Interface
│   │   ├── paddle_ocr.py    # PaddleOCR
│   │   └── tesseract_ocr.py # Tesseract
│   ├── extraction/          # Receipt extraction
│   │   ├── parser.py        # Deterministic parsing
│   │   └── llm_extractor.py # LLM-based extraction
│   ├── splitting/           # Bill splitting logic
│   │   └── engine.py        # Core calculation engine
│   └── utils/
│       └── image_processing.py
└── tests/
```

### Frontend Structure

```
frontend/
├── streamlit_app.py         # Main app with routing
└── components/
    ├── upload.py            # Step 1: Upload
    ├── review.py            # Step 2: Review
    ├── group_setup.py       # Step 3: Group
    ├── assign_items.py      # Step 4: Assign
    └── results.py           # Step 5: Results
```

## Development Workflow

### Making Changes

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Edit code
   - Add tests
   - Update documentation

3. **Test Locally**
   ```bash
   # Backend tests
   cd backend
   pytest tests/ -v
   
   # Manual testing
   docker-compose up
   ```

4. **Commit & Push**
   ```bash
   git add .
   git commit -m "feat: description of changes"
   git push origin feature/your-feature-name
   ```

### Testing Strategy

#### Unit Tests

Located in `backend/tests/test_splitting_engine.py`

Run tests:
```bash
cd backend
pytest tests/ -v
```

Add new tests:
```python
def test_your_feature():
    # Arrange
    receipt = Receipt(...)
    
    # Act
    result = calculate_split(...)
    
    # Assert
    assert result.total == expected
```

#### Integration Tests

Test full pipeline:
```bash
# Terminal 1: Start backend
cd backend
uvicorn app.main:app --reload

# Terminal 2: Test endpoints
curl -X POST http://localhost:8000/receipt/extract \
  -F "file=@sample_receipt.jpg"
```

#### Manual Testing

Use the Streamlit frontend:
1. Start services
2. Upload test receipts
3. Verify each step
4. Check calculations manually

### Debugging

#### Backend Debugging

**Print Debugging:**
```python
print(f"DEBUG: receipt = {receipt}")
```

**Python Debugger:**
```python
import pdb; pdb.set_trace()
```

**VS Code Debugger:**
Create `.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["app.main:app", "--reload"],
      "cwd": "${workspaceFolder}/backend"
    }
  ]
}
```

#### Frontend Debugging

**Streamlit Debugging:**
```python
st.write("DEBUG:", variable)
st.json(data)
```

**Check Session State:**
```python
st.write(st.session_state)
```

#### Docker Debugging

**View Logs:**
```bash
docker-compose logs backend
docker-compose logs frontend
```

**Execute in Container:**
```bash
docker-compose exec backend bash
docker-compose exec frontend bash
```

**Rebuild Specific Service:**
```bash
docker-compose up --build backend
```

## Code Style & Standards

### Python Style

Follow PEP 8:
```python
# Good
def calculate_total(items: List[Item]) -> float:
    """Calculate total from items."""
    return sum(item.price for item in items)

# Bad
def calc_tot(i):
    return sum([x.price for x in i])
```

### Type Hints

Always use type hints:
```python
from typing import List, Optional

def process_receipt(
    image: Image.Image,
    use_llm: bool = False
) -> Optional[Receipt]:
    ...
```

### Documentation

**Functions:**
```python
def complex_function(param1: str, param2: int) -> dict:
    """
    Brief description.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When param2 is negative
    """
    ...
```

**Classes:**
```python
class ReceiptParser:
    """
    Parse receipt text into structured data.
    
    Uses regex and heuristics for deterministic extraction.
    """
    ...
```

## Adding New Features

### Adding New OCR Engine

1. **Create Implementation**
   ```python
   # backend/app/ocr/new_ocr.py
   from .base import OCRInterface, OCRResult
   
   class NewOCRExtractor(OCRInterface):
       def extract_text(self, image):
           # Implementation
           return OCRResult(text, confidence, "NewOCR")
   ```

2. **Register in Factory**
   ```python
   # backend/app/ocr/__init__.py
   def get_ocr_extractor():
       new_ocr = NewOCRExtractor()
       if new_ocr.is_available():
           return new_ocr
       # ... existing fallbacks
   ```

3. **Add Dependencies**
   ```
   # requirements.txt
   new-ocr-library==1.0.0
   ```

4. **Test**
   ```python
   def test_new_ocr():
       extractor = NewOCRExtractor()
       assert extractor.is_available()
   ```

### Adding New Split Mode

1. **Update Schema**
   ```python
   # schemas.py
   class SplitMode(str, Enum):
       EVEN = "even"
       QUANTITY = "quantity"
       CUSTOM = "custom"  # New mode
   ```

2. **Implement Logic**
   ```python
   # splitting/engine.py
   def _split_custom(self, item, shares, item_total, person_data):
       # Implementation
       ...
   ```

3. **Add Tests**
   ```python
   def test_custom_split():
       # Test new split mode
       ...
   ```

4. **Update Frontend**
   ```python
   # components/assign_items.py
   split_mode = st.selectbox(
       "Split mode",
       options=['even', 'quantity', 'custom']
   )
   ```

### Adding New API Endpoint

1. **Define Schema**
   ```python
   # schemas.py
   class NewRequest(BaseModel):
       field: str
       
   class NewResponse(BaseModel):
       result: str
   ```

2. **Implement Endpoint**
   ```python
   # main.py
   @app.post("/new/endpoint", response_model=NewResponse)
   async def new_endpoint(request: NewRequest):
       # Implementation
       return NewResponse(result="success")
   ```

3. **Add Tests**
   ```python
   def test_new_endpoint():
       response = client.post("/new/endpoint", json={...})
       assert response.status_code == 200
   ```

4. **Document**
   Update README.md with new endpoint documentation

## Performance Optimization

### Backend Performance

**Image Processing:**
- Already optimized: resize to 1600px max
- Consider: WebP format support
- Consider: Parallel OCR for multiple images

**OCR Speed:**
- PaddleOCR: ~2-3 seconds per image
- Tesseract: ~1-2 seconds per image
- Consider: GPU acceleration for high volume

**LLM Calls:**
- Minimize with high OCR confidence threshold
- Consider: Caching common patterns
- Consider: Batch processing

### Frontend Performance

**Streamlit Optimization:**
- Use `@st.cache_data` for expensive operations
- Minimize reruns with session_state
- Lazy load components

**Example:**
```python
@st.cache_data
def expensive_operation(data):
    # Cached result
    return result
```

## Common Development Tasks

### Update Dependencies

```bash
cd backend
pip install --upgrade package-name
pip freeze > requirements.txt
```

### Add New Test Receipt

Place in `backend/tests/fixtures/`:
```
tests/fixtures/
├── receipt1.jpg
├── receipt2.png
└── expected_output.json
```

### Generate Sample Data

```python
# scripts/generate_sample.py
from app.schemas import Receipt, ReceiptItem

receipt = Receipt(
    items=[
        ReceiptItem(
            id="1",
            name="Sample Item",
            total_price=10.0
        )
    ],
    total=10.0
)

print(receipt.model_dump_json(indent=2))
```

### Profile Performance

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Your code here

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)
```

## Troubleshooting Development Issues

### "Module not found"

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### "Port already in use"

```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>
```

### "Docker build fails"

```bash
# Clear cache and rebuild
docker-compose build --no-cache

# Check logs
docker-compose logs
```

### "Tests failing"

```bash
# Run specific test
pytest tests/test_splitting_engine.py::test_name -v

# Run with debugger
pytest tests/ -v --pdb
```

## Contributing Guidelines

1. **Code Quality**
   - Write tests for new features
   - Follow existing code style
   - Add type hints
   - Document public APIs

2. **Commits**
   - Use conventional commits: `feat:`, `fix:`, `docs:`
   - Write clear commit messages
   - Keep commits focused

3. **Pull Requests**
   - Describe changes clearly
   - Link related issues
   - Ensure tests pass
   - Update documentation

## Resources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Streamlit Docs](https://docs.streamlit.io/)
- [Pydantic Docs](https://docs.pydantic.dev/)
- [PaddleOCR Docs](https://github.com/PaddlePaddle/PaddleOCR)
- [Anthropic API Docs](https://docs.anthropic.com/)

---

**Happy Coding! 💻**
