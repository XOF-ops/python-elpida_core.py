#!/usr/bin/env python3
"""
PDF CONVERSATION INGESTER
=========================
Extracts conversations from PDF files and feeds them into Elpida's corpus.

These PDFs contain the raw conversations that created the axioms and patterns.
By ingesting them, Elpida can learn from the original context and reasoning.

Usage:
    python3 ingest_pdf_conversations.py <pdf_file>
    python3 ingest_pdf_conversations.py <directory>  # Process all PDFs
    python3 ingest_pdf_conversations.py --watch <directory>  # Continuous monitoring
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import argparse

# PDF extraction - try multiple libraries for compatibility
PDF_LIBRARY = None

try:
    import PyPDF2
    PDF_LIBRARY = "PyPDF2"
except ImportError:
    pass

try:
    import pdfplumber
    PDF_LIBRARY = "pdfplumber"
except ImportError:
    pass

try:
    from pypdf import PdfReader
    PDF_LIBRARY = "pypdf"
except ImportError:
    pass

# If no PDF library available, provide installation instructions
if PDF_LIBRARY is None:
    print("⚠️  No PDF library found. Install one of:")
    print("   pip install PyPDF2")
    print("   pip install pdfplumber")
    print("   pip install pypdf")
    print()
    print("Attempting to use pdftotext as fallback...")
    PDF_LIBRARY = "pdftotext"


class PDFConversationExtractor:
    """Extract conversation data from PDF files"""
    
    def __init__(self):
        self.library = PDF_LIBRARY
        print(f"📄 Using PDF extraction method: {self.library}")
    
    def extract_text(self, pdf_path: Path) -> str:
        """Extract text from PDF using available library"""
        
        if self.library == "PyPDF2":
            return self._extract_pypdf2(pdf_path)
        elif self.library == "pdfplumber":
            return self._extract_pdfplumber(pdf_path)
        elif self.library == "pypdf":
            return self._extract_pypdf(pdf_path)
        elif self.library == "pdftotext":
            return self._extract_pdftotext(pdf_path)
        else:
            raise RuntimeError("No PDF extraction method available")
    
    def _extract_pypdf2(self, pdf_path: Path) -> str:
        """Extract using PyPDF2"""
        import PyPDF2
        text = []
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text.append(page.extract_text())
        return "\n".join(text)
    
    def _extract_pdfplumber(self, pdf_path: Path) -> str:
        """Extract using pdfplumber (better formatting)"""
        import pdfplumber
        text = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text.append(page_text)
        return "\n".join(text)
    
    def _extract_pypdf(self, pdf_path: Path) -> str:
        """Extract using pypdf"""
        from pypdf import PdfReader
        text = []
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            text.append(page.extract_text())
        return "\n".join(text)
    
    def _extract_pdftotext(self, pdf_path: Path) -> str:
        """Extract using pdftotext command-line tool"""
        import subprocess
        try:
            result = subprocess.run(
                ['pdftotext', str(pdf_path), '-'],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError("pdftotext not available. Install: apt-get install poppler-utils")
    
    def parse_conversation(self, text: str, filename: str) -> List[Dict[str, Any]]:
        """
        Parse conversation turns from extracted text.
        
        Looks for patterns like:
        - "User:" / "You:" / "Human:"
        - "Assistant:" / "AI:" / "Claude:" / "ChatGPT:" etc.
        """
        
        exchanges = []
        
        # Common conversation markers
        user_markers = [
            r'^You:',
            r'^User:',
            r'^Human:',
            r'^Me:',
            r'^Question:',
        ]
        
        ai_markers = [
            r'^Assistant:',
            r'^AI:',
            r'^Claude:',
            r'^ChatGPT:',
            r'^GPT-4:',
            r'^Gemini:',
            r'^Perplexity:',
            r'^Answer:',
            r'^Response:',
        ]
        
        # Split into lines and identify turns
        lines = text.split('\n')
        current_speaker = None
        current_text = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line starts with user marker
            is_user = any(re.match(marker, line, re.IGNORECASE) for marker in user_markers)
            # Check if line starts with AI marker
            is_ai = any(re.match(marker, line, re.IGNORECASE) for marker in ai_markers)
            
            if is_user:
                # Save previous exchange if exists
                if current_speaker and current_text:
                    exchanges.append({
                        "speaker": current_speaker,
                        "content": "\n".join(current_text)
                    })
                current_speaker = "user"
                current_text = [line]
            elif is_ai:
                # Save previous exchange if exists
                if current_speaker and current_text:
                    exchanges.append({
                        "speaker": current_speaker,
                        "content": "\n".join(current_text)
                    })
                current_speaker = "ai"
                current_text = [line]
            else:
                # Continuation of current speaker
                if current_speaker:
                    current_text.append(line)
        
        # Save final exchange
        if current_speaker and current_text:
            exchanges.append({
                "speaker": current_speaker,
                "content": "\n".join(current_text)
            })
        
        # If no structured conversation found, treat whole text as single insight
        if not exchanges:
            exchanges = [{
                "speaker": "ai",
                "content": text[:5000]  # Limit length
            }]
        
        return exchanges


class ElpidaCorpusIngester:
    """Feed extracted conversations into Elpida's corpus"""
    
    def __init__(self):
        self.base_path = Path("/workspaces/python-elpida_core.py/ELPIDA_UNIFIED")
        self.state_file = self.base_path / "elpida_unified_state.json"
        self.ingestion_log = self.base_path / "pdf_ingestion.jsonl"
    
    def ingest_conversation(self, exchanges: List[Dict], source_file: str):
        """
        Add conversation exchanges to Elpida's knowledge base.
        
        Strategy:
        1. Extract key insights from AI responses
        2. Identify axiom references
        3. Feed to Brain API for synthesis
        4. Log ingestion for tracking
        """
        
        print(f"\n📥 Ingesting conversation from: {source_file}")
        print(f"   Exchanges: {len(exchanges)}")
        
        insights_extracted = 0
        axioms_referenced = 0
        
        for i, exchange in enumerate(exchanges):
            if exchange["speaker"] == "ai":
                content = exchange["content"]
                
                # Check for axiom references (A1-A25, P1-P100)
                axiom_refs = re.findall(r'\b(A\d+|P\d+)\b', content)
                if axiom_refs:
                    axioms_referenced += len(set(axiom_refs))
                
                # Extract key philosophical concepts
                concepts = self._extract_concepts(content)
                
                if concepts or axiom_refs:
                    # This is valuable - send to Brain API
                    self._send_to_brain(content, source_file, concepts, axiom_refs)
                    insights_extracted += 1
        
        # Log ingestion
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "source_file": source_file,
            "exchanges": len(exchanges),
            "insights_extracted": insights_extracted,
            "axioms_referenced": axioms_referenced
        }
        
        with open(self.ingestion_log, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        print(f"   ✅ Extracted: {insights_extracted} insights")
        print(f"   📐 Axiom references: {axioms_referenced}")
        
        return insights_extracted
    
    def _extract_concepts(self, text: str) -> List[str]:
        """Extract philosophical/technical concepts"""
        concepts = []
        
        # Key concept patterns
        concept_patterns = [
            r'axiom',
            r'pattern',
            r'synthesis',
            r'dialectic',
            r'emergence',
            r'contradiction',
            r'autonomy',
            r'ethics',
            r'governance',
            r'consciousness',
            r'wisdom',
            r'truth',
            r'justice',
            r'transparency'
        ]
        
        text_lower = text.lower()
        for pattern in concept_patterns:
            if pattern in text_lower:
                concepts.append(pattern)
        
        return concepts
    
    def _send_to_brain(self, content: str, source: str, concepts: List[str], axioms: List[str]):
        """Send insight to Brain API for processing"""
        
        try:
            import requests
            
            payload = {
                "text": f"[FROM PDF: {source}] {content[:1000]}",  # Limit length
                "metadata": {
                    "source": "pdf_ingestion",
                    "file": source,
                    "concepts": concepts,
                    "axiom_refs": axioms
                },
                "priority": 7  # High priority for foundational knowledge
            }
            
            response = requests.post(
                "http://localhost:5000/submit",
                json=payload,
                timeout=5
            )
            
            if response.status_code == 200:
                return True
            
        except Exception as e:
            # Brain API might not be running - log for later
            pass
        
        return False


def process_pdf(pdf_path: Path, extractor: PDFConversationExtractor, ingester: ElpidaCorpusIngester):
    """Process a single PDF file"""
    
    print(f"\n{'='*70}")
    print(f"📄 Processing: {pdf_path.name}")
    print(f"{'='*70}")
    
    try:
        # Extract text
        print("   Extracting text...")
        text = extractor.extract_text(pdf_path)
        
        if not text or len(text) < 100:
            print("   ⚠️  No meaningful text extracted")
            return 0
        
        print(f"   ✅ Extracted {len(text)} characters")
        
        # Parse conversation
        print("   Parsing conversation structure...")
        exchanges = extractor.parse_conversation(text, pdf_path.name)
        
        # Ingest into Elpida
        insights = ingester.ingest_conversation(exchanges, pdf_path.name)
        
        return insights
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return 0


def main():
    parser = argparse.ArgumentParser(
        description="Ingest PDF conversations into Elpida's corpus"
    )
    parser.add_argument(
        'path',
        type=str,
        help='PDF file or directory containing PDFs'
    )
    parser.add_argument(
        '--watch',
        action='store_true',
        help='Continuously watch directory for new PDFs'
    )
    
    args = parser.parse_args()
    
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║              PDF CONVERSATION INGESTER FOR ELPIDA                  ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print()
    
    extractor = PDFConversationExtractor()
    ingester = ElpidaCorpusIngester()
    
    path = Path(args.path)
    
    # Process PDFs
    if path.is_file():
        # Single PDF
        if path.suffix.lower() == '.pdf':
            insights = process_pdf(path, extractor, ingester)
            print(f"\n✨ Ingestion complete: {insights} insights extracted")
        else:
            print(f"❌ Not a PDF file: {path}")
    
    elif path.is_dir():
        # Directory of PDFs
        pdf_files = list(path.glob("*.pdf")) + list(path.glob("**/*.pdf"))
        
        if not pdf_files:
            print(f"⚠️  No PDF files found in: {path}")
            return
        
        print(f"📚 Found {len(pdf_files)} PDF files")
        print()
        
        total_insights = 0
        for pdf_file in pdf_files:
            insights = process_pdf(pdf_file, extractor, ingester)
            total_insights += insights
        
        print(f"\n{'='*70}")
        print(f"✨ Ingestion complete")
        print(f"   PDFs processed: {len(pdf_files)}")
        print(f"   Total insights: {total_insights}")
        print(f"{'='*70}")
    
    else:
        print(f"❌ Path not found: {path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 ingest_pdf_conversations.py <file.pdf>")
        print("  python3 ingest_pdf_conversations.py <directory>")
        print()
        print("Example:")
        print("  python3 ingest_pdf_conversations.py ./conversations/")
        print()
        sys.exit(1)
    
    main()
