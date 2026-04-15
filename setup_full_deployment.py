#!/usr/bin/env python3
"""
ELPIDA FULL SETUP SCRIPT
=========================
Run this ONCE from any machine where huggingface.co is reachable.
(NOT from GitHub Codespaces — HF blocks Codespace IPs.)

What it does:
1. Creates the elpida-api HF Space
2. Sets ALL secrets on both HF Spaces (API + UI)
3. Sets HF_TOKEN in GitHub repo secrets (for auto-deploy)
4. Pushes code to the API Space
5. Verifies everything is live

Requirements:
    pip install huggingface_hub PyGithub

Usage:
    python setup_full_deployment.py
"""

import os
import sys
import json
import time
import subprocess
import tempfile
import shutil
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════
# CONFIGURATION — all values from the codespace .env
# ═══════════════════════════════════════════════════════════════════

HF_TOKEN = "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"
HF_USERNAME = "z65nik"

# HF Space names
UI_SPACE = f"{HF_USERNAME}/elpida-governance-layer"   # already exists
API_SPACE = f"{HF_USERNAME}/elpida-api"                # will be created

# GitHub repo
GITHUB_REPO = "XOF-ops/python-elpida_core.py"

# Generated API keys for the /v1/audit endpoint
ELPIDA_API_KEYS = ",".join([
    "free_demo_7065622a45d8c8a4575a1fb7",
    "pro_launch_fcb69bcaa69101e865f395335003c4a3",
    "team_internal_ea1d4e14df60572bdc19cf5be8377f06",
])

ELPIDA_ADMIN_KEY = "a14588256c3d3aac31dbe3a280d549e46e0f5781"

# LLM provider keys (from .env)
LLM_SECRETS = {
    "OPENROUTER_API_KEY":    "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",
    "PERPLEXITY_API_KEY":    "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",
    "GEMINI_API_KEY":        "AIzaSyBkI2ocCMmkl93WkWVZFntBDFYjX_QeiqA",
    "MISTRAL_API_KEY":       "MxwbkyFIQ6xXPpE0DKlZqAH0CKakoJLb",
    "COHERE_API_KEY":        "nF5X9oX4805EbORoj0FHJAmFPDANFtgsFSaMGBZP",
    "ANTHROPIC_API_KEY":     "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",
    "XAI_API_KEY":           "xai-e5djkVXxAWYDHJzNVW3A5CJny6UmH166qX19yCzO5fvHNPXQ8nm1deWEbzcUy2x0eV6URTubNF7piRqI",
    "OPENAI_API_KEY":        "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",
    "GROQ_API_KEY":          "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",
    "HUGGINGFACE_API_KEY":   "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",
    "AWS_ACCESS_KEY_ID":     "AKIAXK7SYMRFTHRYHTO2",
    "AWS_SECRET_ACCESS_KEY": "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",
}

# ═══════════════════════════════════════════════════════════════════
# STEP 0: Check dependencies
# ═══════════════════════════════════════════════════════════════════

def check_deps():
    print("=" * 60)
    print("STEP 0: Checking dependencies...")
    try:
        from huggingface_hub import HfApi
        print("  ✓ huggingface_hub installed")
    except ImportError:
        print("  ✗ Installing huggingface_hub...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "huggingface_hub"])
        from huggingface_hub import HfApi
    
    # Verify HF token works
    api = HfApi(token=HF_TOKEN)
    try:
        info = api.whoami()
        print(f"  ✓ HF authenticated as: {info['name']}")
    except Exception as e:
        print(f"  ✗ HF token failed: {e}")
        print("    → Go to https://huggingface.co/settings/tokens")
        print("    → Create a WRITE token and update HF_TOKEN in this script")
        sys.exit(1)
    
    return api


# ═══════════════════════════════════════════════════════════════════
# STEP 1: Create API Space
# ═══════════════════════════════════════════════════════════════════

def create_api_space(api):
    print("\n" + "=" * 60)
    print("STEP 1: Creating API Space...")
    
    try:
        space_info = api.space_info(API_SPACE)
        print(f"  ✓ Space {API_SPACE} already exists")
        return True
    except Exception:
        pass
    
    try:
        api.create_repo(
            repo_id=API_SPACE,
            repo_type="space",
            space_sdk="docker",
            private=False,
        )
        print(f"  ✓ Created Space: {API_SPACE}")
        return True
    except Exception as e:
        if "already" in str(e).lower():
            print(f"  ✓ Space {API_SPACE} already exists")
            return True
        print(f"  ✗ Failed to create Space: {e}")
        return False


# ═══════════════════════════════════════════════════════════════════
# STEP 2: Set secrets on both Spaces
# ═══════════════════════════════════════════════════════════════════

def set_hf_secrets(api):
    print("\n" + "=" * 60)
    print("STEP 2: Setting secrets on HF Spaces...")
    
    for space_name in [UI_SPACE, API_SPACE]:
        print(f"\n  --- {space_name} ---")
        
        # Elpida-specific secrets
        elpida_secrets = {
            "ELPIDA_API_KEYS": ELPIDA_API_KEYS,
            "ELPIDA_ADMIN_KEY": ELPIDA_ADMIN_KEY,
        }
        
        # All secrets = Elpida + LLM + AWS
        all_secrets = {**elpida_secrets, **LLM_SECRETS}
        
        for key, value in all_secrets.items():
            try:
                api.add_space_secret(space_name, key, value)
                print(f"    ✓ {key}")
            except Exception as e:
                print(f"    ✗ {key}: {e}")
    
    print("\n  ✓ All secrets set")


# ═══════════════════════════════════════════════════════════════════
# STEP 3: Set HF_TOKEN in GitHub repo secrets
# ═══════════════════════════════════════════════════════════════════

def set_github_secret():
    print("\n" + "=" * 60)
    print("STEP 3: Setting HF_TOKEN in GitHub repo secrets...")
    
    try:
        # Try using gh CLI if available
        result = subprocess.run(
            ["gh", "secret", "set", "HF_TOKEN",
             "--repo", GITHUB_REPO,
             "--body", HF_TOKEN],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            print(f"  ✓ HF_TOKEN set in {GITHUB_REPO} GitHub secrets")
            return True
        else:
            print(f"  ✗ gh CLI failed: {result.stderr.strip()}")
    except FileNotFoundError:
        print("  ✗ gh CLI not found")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    # Fallback: try PyGithub
    try:
        from github import Github
        g = Github(os.environ.get("GITHUB_TOKEN", ""))
        repo = g.get_repo(GITHUB_REPO)
        repo.create_secret("HF_TOKEN", HF_TOKEN)
        print(f"  ✓ HF_TOKEN set via PyGithub")
        return True
    except ImportError:
        print("  ⚠ PyGithub not installed. Install with: pip install PyGithub")
    except Exception as e:
        print(f"  ✗ PyGithub failed: {e}")
    
    print("\n  ⚠ MANUAL STEP NEEDED:")
    print(f"    Go to: https://github.com/{GITHUB_REPO}/settings/secrets/actions")
    print(f"    Add secret: HF_TOKEN = {HF_TOKEN[:10]}...")
    return False


# ═══════════════════════════════════════════════════════════════════
# STEP 4: Push code to API Space
# ═══════════════════════════════════════════════════════════════════

def push_api_space_code():
    print("\n" + "=" * 60)
    print("STEP 4: Pushing code to API Space...")
    
    # Find repo root
    script_dir = Path(__file__).resolve().parent
    # Look for hf_deployment relative to script
    candidates = [
        script_dir / "hf_deployment",
        script_dir.parent / "hf_deployment",
        Path.cwd() / "hf_deployment",
    ]
    
    hf_deploy_dir = None
    for c in candidates:
        if c.exists():
            hf_deploy_dir = c
            break
    
    if not hf_deploy_dir:
        print("  ✗ hf_deployment/ directory not found")
        print("    Run this script from the repo root.")
        return False
    
    api_space_dir = hf_deploy_dir.parent / "hf_api_space"
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Copy hf_deployment content
        shutil.copytree(hf_deploy_dir, tmpdir / "deploy", 
                       dirs_exist_ok=True,
                       ignore=shutil.ignore_patterns('.git', '__pycache__', 'cache'))
        
        # Overwrite Dockerfile and README with API-specific versions
        if api_space_dir.exists():
            for f in ["Dockerfile", "README.md"]:
                src = api_space_dir / f
                if src.exists():
                    shutil.copy2(src, tmpdir / "deploy" / f)
        
        deploy_path = tmpdir / "deploy"
        
        # Init git and push
        hf_url = f"https://{HF_USERNAME}:{HF_TOKEN}@huggingface.co/spaces/{API_SPACE}"
        
        cmds = [
            ["git", "init"],
            ["git", "config", "user.email", "elpida-deploy@setup"],
            ["git", "config", "user.name", "Elpida Setup"],
            ["git", "add", "-A"],
            ["git", "commit", "-m", "Initial API Space deployment"],
            ["git", "remote", "add", "origin", hf_url],
            ["git", "push", "origin", "main", "--force"],
        ]
        
        for cmd in cmds:
            result = subprocess.run(cmd, cwd=str(deploy_path),
                                   capture_output=True, text=True)
            if result.returncode != 0 and "commit" not in cmd[1]:
                print(f"  ✗ {' '.join(cmd[:3])}: {result.stderr.strip()[:200]}")
                return False
        
        print(f"  ✓ Code pushed to {API_SPACE}")
        return True


# ═══════════════════════════════════════════════════════════════════
# STEP 5: Verify
# ═══════════════════════════════════════════════════════════════════

def verify():
    print("\n" + "=" * 60)
    print("STEP 5: Verification...")
    print("  HF Spaces take 2-5 minutes to build after push.")
    print(f"\n  UI Space:  https://huggingface.co/spaces/{UI_SPACE}")
    print(f"  API Space: https://huggingface.co/spaces/{API_SPACE}")
    print(f"  API Docs:  https://{HF_USERNAME}-elpida-api.hf.space/docs")
    print(f"  API Health: https://{HF_USERNAME}-elpida-api.hf.space/health")
    
    import urllib.request
    
    print("\n  Checking API Space health (may take time to build)...")
    for attempt in range(3):
        try:
            url = f"https://{HF_USERNAME}-elpida-api.hf.space/health"
            req = urllib.request.Request(url, headers={"User-Agent": "elpida-setup/1.0"})
            resp = urllib.request.urlopen(req, timeout=30)
            data = json.loads(resp.read())
            print(f"  ✓ API is LIVE: {json.dumps(data, indent=2)[:200]}")
            return True
        except Exception as e:
            print(f"  ... attempt {attempt+1}/3: {str(e)[:80]}")
            if attempt < 2:
                print("  ... waiting 60s for Space to build...")
                time.sleep(60)
    
    print("  ⚠ API not reachable yet — likely still building.")
    print("    Check manually in a few minutes.")
    return False


# ═══════════════════════════════════════════════════════════════════
# STEP 6: Print summary
# ═══════════════════════════════════════════════════════════════════

def print_summary():
    print("\n" + "=" * 60)
    print("SETUP COMPLETE — SUMMARY")
    print("=" * 60)
    
    print(f"""
INFRASTRUCTURE:
  UI:     https://{HF_USERNAME}-elpida-governance-layer.hf.space
  API:    https://{HF_USERNAME}-elpida-api.hf.space
  Docs:   https://{HF_USERNAME}-elpida-api.hf.space/docs
  GitHub: https://github.com/{GITHUB_REPO}

API KEYS (store these securely):
  Free:  free_demo_7065622a45d8c8a4575a1fb7
  Pro:   pro_launch_fcb69bcaa69101e865f395335003c4a3
  Team:  team_internal_ea1d4e14df60572bdc19cf5be8377f06

ADMIN ACCESS:
  System tab: https://{HF_USERNAME}-elpida-governance-layer.hf.space/?admin={ELPIDA_ADMIN_KEY}

TEST THE API:
  curl -X POST https://{HF_USERNAME}-elpida-api.hf.space/v1/audit \\
    -H "X-API-Key: free_demo_7065622a45d8c8a4575a1fb7" \\
    -H "Content-Type: application/json" \\
    -d '{{"action": "Deploy AI without human oversight", "depth": "quick"}}'

REMAINING MANUAL STEPS:
  1. Create LemonSqueezy account → https://lemonsqueezy.com
  2. Create products: Free ($0), Pro ($29/mo), Team ($99/mo)
  3. Update checkout URLs in ui.py and hf_api_space/README.md
  4. Announce on Twitter, HN, Reddit
""")


# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

def main():
    print("╔══════════════════════════════════════════════════════════╗")
    print("║  ELPIDA FULL DEPLOYMENT SETUP                          ║")
    print("║  Creates Spaces, sets secrets, deploys code            ║")
    print("╚══════════════════════════════════════════════════════════╝\n")
    
    api = check_deps()
    create_api_space(api)
    set_hf_secrets(api)
    set_github_secret()
    push_api_space_code()
    verify()
    print_summary()


if __name__ == "__main__":
    main()