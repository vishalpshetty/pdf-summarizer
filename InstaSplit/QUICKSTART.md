# ⚡ Quick Start Guide

Get InstaSplit running in 5 minutes!

## Prerequisites

- Python 3.11+ OR Docker Desktop
- Anthropic API key ([get one here](https://console.anthropic.com/))

## Fastest Way: Docker Compose

1. **Clone & Navigate**
   ```bash
   cd "/Users/vishalhp/AI Folder/InstaSplit"
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your Anthropic API key:
   ```
   ANTHROPIC_API_KEY=your_key_here
   ```

3. **Start Everything**
   ```bash
   docker-compose up
   ```

4. **Use the App**
   - Open http://localhost:8501 in your browser
   - Upload a receipt photo
   - Follow the 5-step process
   - Done!

## Alternative: Native Python

### Terminal 1 - Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your_key_here
uvicorn app.main:app --reload
```

### Terminal 2 - Frontend
```bash
cd frontend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export BACKEND_URL=http://localhost:8000
streamlit run streamlit_app.py
```

## First Upload Tips

**For Best Results:**

1. Take a clear, well-lit photo
2. Capture the entire receipt
3. Ensure text is readable
4. Keep file under 8MB

**Sample Receipt:**
- Use any restaurant receipt
- Pizza/Chinese takeout work great
- Chain restaurants often have clear receipts

## What Happens Behind the Scenes

1. Image is uploaded (max 8MB)
2. **OCR runs first** (free, fast) - PaddleOCR or Tesseract
3. Smart parser extracts items, prices, totals
4. If OCR is unclear, **Claude helps** (costs ~$0.001)
5. You review and edit
6. Add your group members
7. Assign items to people
8. See exact breakdown with penny-perfect rounding

## Cost Per Receipt

**OCR-Only** (most receipts): **FREE**
- Just server costs

**OCR + Claude Text**: **~$0.001-0.005**
- Only when OCR needs help

**OCR + Claude Vision**: **~$0.01-0.02**
- Rare, only if enabled and OCR completely fails

## Troubleshooting

### "Cannot connect to backend"
**Solution:** Make sure backend is running first, then start frontend

### "OCR failed"
**Solution:** 
- Try a clearer photo
- Ensure good lighting
- Make sure text is in focus

### "Import errors"
**Solution:**
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
pip install -r requirements.txt
```

### "Port already in use"
**Solution:**
```bash
# Kill process on port 8000
lsof -i :8000
kill -9 <PID>

# Or use different ports
uvicorn app.main:app --port 8001
streamlit run streamlit_app.py --server.port 8502
```

## Next Steps

- ✅ Try splitting a real receipt
- 📖 Read full README.md for details
- 🚀 Deploy to Railway (see DEPLOYMENT.md)
- 🛠️ Customize for your needs (see DEVELOPMENT.md)

## Usage Example

```
1. Upload receipt:
   - Pizza: $20
   - Wings: $15
   - Drinks: $10
   - Tax: $4.50
   - Tip: $9
   - Total: $58.50

2. Add group:
   - Alice
   - Bob
   - Charlie

3. Assign items:
   - Pizza: Alice, Bob, Charlie (split evenly)
   - Wings: Bob only
   - Drinks: Alice, Charlie (split evenly)

4. Results:
   - Alice: $17.50
   - Bob: $26.00
   - Charlie: $15.00
   - Total: $58.50 ✅ (matches exactly!)
```

## Support

**Having issues?**
1. Check DEVELOPMENT.md troubleshooting section
2. Review logs in terminal
3. Try with Docker if native Python fails
4. Test with `curl http://localhost:8000/health`

**Want more features?**
- The code is fully documented
- Easy to extend (see DEVELOPMENT.md)
- Add custom split modes
- Integrate with payment apps
- Multi-receipt support

---

**Ready to split some bills? Let's go! 🎉**
