# UPLOAD PDFs TO ELPIDA - QUICK START

## Step 1: Upload Your PDFs

### Method 1: VS Code File Upload
1. In VS Code Explorer, navigate to: `/workspaces/python-elpida_core.py/ELPIDA_UNIFIED/conversations/`
2. Right-click on the folder → **Upload Files...**
3. Select your PDF files
4. Done!

### Method 2: Drag and Drop
- Drag PDF files from your computer
- Drop them into the `conversations/` folder in VS Code Explorer

### Method 3: Terminal (if you have file path)
```bash
# Copy from local to codespace
scp /path/to/your/file.pdf <codespace-url>:/workspaces/python-elpida_core.py/ELPIDA_UNIFIED/conversations/
```

---

## Step 2: Run the Ingester

```bash
cd /workspaces/python-elpida_core.py/ELPIDA_UNIFIED

# Ingest all PDFs in conversations/
python3 ingest_pdf_conversations.py conversations/
```

**That's it!**

---

## What Happens

1. ✅ PDF text extracted
2. ✅ Conversations parsed (User: / Assistant: structure)
3. ✅ Insights identified (philosophical concepts, axiom references)
4. ✅ Sent to Brain API for synthesis
5. ✅ Integrated into Elpida's growing knowledge

---

## Watch It Work

**Terminal 1:** Ingest
```bash
python3 ingest_pdf_conversations.py conversations/
```

**Terminal 2:** Monitor growth
```bash
python3 monitor_progress.py
```

You'll see pattern count increase as insights are synthesized!

---

## Current Status

**PDF Library:** ✅ PyPDF2 installed  
**Directory:** ✅ `/conversations/` ready  
**Ingester:** ✅ `ingest_pdf_conversations.py` ready  
**Brain API:** ✅ Running (localhost:5000)  

**You can upload PDFs right now!**

---

## Troubleshooting

**Can't upload in VS Code?**
- Check you're in the right directory
- Try creating a test file first to verify permissions

**Ingester not working?**
- Check PDF library: `pip list | grep PyPDF`
- Try: `pip install PyPDF2`

**No insights extracted?**
- PDF might be scanned image (not text)
- Try `pdfplumber`: `pip install pdfplumber`

---

See [PDF_INGESTION_GUIDE.md](PDF_INGESTION_GUIDE.md) for complete documentation.

**Ἐλπίδα ζωή.**
