"""
API KEY MANAGER v1.0
--------------------
Securely manages API keys for multi-AI harvesting.

IMPORTANT: In production, use environment variables or secrets manager.
This file should be in .gitignore to prevent key leakage.
"""

import os

class APIKeyVault:
    """Secure storage for API keys."""
    
    def __init__(self):
        # Initialize keys (will load from env or use provided defaults)
        self.keys = {
            # Google Gemini - Free tier, good for reasoning
            "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY", "AIzaSyDnEkRLUXMiz81njBNyhxxzqlqX6c4xbAA"),
            
            # Groq - Fast inference, good for quick synthesis
            "GROQ_API_KEY": os.getenv("GROQ_API_KEY", "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"),
            
            # Mistral via HuggingFace - Good for embeddings and analysis
            "HUGGINGFACE_API_KEY": os.getenv("HUGGINGFACE_API_KEY", "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"),
            
            # Cohere - Excellent for embeddings and classification
            "COHERE_API_KEY": os.getenv("COHERE_API_KEY", "IrsCSJx06RXBOXNVSc8zvlliWqovJP4v1B1f7Crn"),
            
            # Perplexity - Real-time web search and reasoning
            "PERPLEXITY_API_KEY": os.getenv("PERPLEXITY_API_KEY", "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"),
            
            # OpenRouter - Access to multiple models
            "OPENROUTER_API_KEY": os.getenv("OPENROUTER_API_KEY", "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"),
            
            # GitHub - For potential code analysis
            "GITHUB_TOKEN": os.getenv("GITHUB_TOKEN", "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")
        }
        
        # Set environment variables if not already set
        for key, value in self.keys.items():
            if not os.getenv(key):
                os.environ[key] = value
    
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
