"""
API KEY MANAGER v1.0
--------------------
Securely manages API keys for multi-AI harvesting.

IMPORTANT: All keys MUST be set via environment variables or a secrets manager.
Never hardcode key values in this file — it is committed to git.
Use a local .env file (gitignored) or platform secrets (HF Spaces, Vercel, etc.).
"""

import os

class APIKeyVault:
    """Secure storage for API keys — reads exclusively from environment variables."""

    def __init__(self):
        # All keys loaded from environment ONLY — no hardcoded fallbacks.
        self.keys = {
            # Google Gemini
            "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"),

            # Groq — fast inference
            "GROQ_API_KEY": os.getenv("GROQ_API_KEY"),

            # HuggingFace
            "HUGGINGFACE_API_KEY": os.getenv("HUGGINGFACE_API_KEY"),

            # Cohere
            "COHERE_API_KEY": os.getenv("COHERE_API_KEY"),

            # Perplexity
            "PERPLEXITY_API_KEY": os.getenv("PERPLEXITY_API_KEY"),

            # OpenRouter
            "OPENROUTER_API_KEY": os.getenv("OPENROUTER_API_KEY"),

            # GitHub
            "GITHUB_TOKEN": os.getenv("GITHUB_TOKEN"),
        }
        
        # Note: keys that are None (not set in env) are intentionally left unset.
    
    def get(self, key_name):
        """Get an API key."""
        return self.keys.get(key_name)
    
    def has_key(self, key_name):
        """Check if a key is available."""
        return key_name in self.keys and self.keys[key_name]
    
    def get_available_services(self):
        """List all available API services."""
        return {k: ("✅" if v else "❌") for k, v in self.keys.items()}

# Global vault instance
vault = APIKeyVault()

def get_api_key(service_name):
    """Helper function to get API key."""
    return vault.get(service_name)

def is_service_available(service_name):
    """Check if service is available."""
    return vault.has_key(service_name)

if __name__ == "__main__":
    print("API Key Vault Status:")
    print("-" * 50)
    for service, status in vault.get_available_services().items():
        print(f"{status} {service}")
