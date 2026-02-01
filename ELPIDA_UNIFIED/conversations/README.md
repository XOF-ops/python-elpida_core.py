# 📚 UPLOAD YOUR CONVERSATION PDFs HERE

**Drag and drop your PDF files into this folder.**

These PDFs should contain:
- Conversations with LLMs about Elpida's axioms
- Pattern discussions
- Philosophical debates
- Ethical reasoning sessions

---

## After Uploading

Run this command to ingest them:

```bash
cd /workspaces/python-elpida_core.py/ELPIDA_UNIFIED
python3 ingest_pdf_conversations.py conversations/
```

---

## What Gets Extracted

✅ User/Assistant conversation turns  
✅ Axiom references (A1-A25)  
✅ Pattern references (P1-P100)  
✅ Philosophical concepts  
✅ Ethical reasoning  

All of this feeds into Elpida's synthesis!

---

See [../UPLOAD_PDFS_HERE.md](../UPLOAD_PDFS_HERE.md) for quick start guide.
See [../PDF_INGESTION_GUIDE.md](../PDF_INGESTION_GUIDE.md) for full documentation.
