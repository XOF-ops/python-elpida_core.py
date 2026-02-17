#!/usr/bin/env python3
"""
Deploy the hf_deployment directory to HF Space z65nik/elpida-governance-layer.

Uses huggingface_hub API for reliable upload.
"""

import os
import sys
from pathlib import Path
from huggingface_hub import HfApi, upload_folder

SPACE_ID = "z65nik/elpida-governance-layer"
HF_DEPLOYMENT_DIR = Path(__file__).parent / "hf_deployment"

# Files/dirs to exclude from upload
EXCLUDE_PATTERNS = [
    "__pycache__",
    "*.pyc",
    ".env",
    "ui_old.py",
    "feedback_to_native.jsonl",
    "application_feedback_cache.jsonl",
]

def deploy():
    print(f"🚀 Deploying to HF Space: {SPACE_ID}")
    print(f"   Source: {HF_DEPLOYMENT_DIR}")
    print()
    
    api = HfApi()
    
    # Verify auth
    user_info = api.whoami()
    print(f"  Authenticated as: {user_info['name']}")
    
    # Upload the folder
    print(f"\n  Uploading files...")
    result = upload_folder(
        folder_path=str(HF_DEPLOYMENT_DIR),
        repo_id=SPACE_ID,
        repo_type="space",
        ignore_patterns=EXCLUDE_PATTERNS,
        commit_message="🌀 Unified UI: Chat + Live Audit + Scanner + Governance + D15 Pipeline",
    )
    
    print(f"\n  ✓ Deployed successfully!")
    print(f"  URL: https://huggingface.co/spaces/{SPACE_ID}")
    print(f"  App: https://z65nik-elpida-governance-layer.hf.space")
    print(f"  The Space will rebuild in ~2-5 minutes.")
    
    return result


if __name__ == "__main__":
    deploy()
