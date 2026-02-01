#!/usr/bin/env python3
"""
AI Bridge - Programmatic Connections Between AI Systems
========================================================

Enables Elpida to establish direct API connections with other AI models
instead of relying on manual message relay.

Supports:
- OpenAI (GPT-4, GPT-3.5)
- Google Gemini
- Anthropic Claude
- xAI Grok
- Any HTTP-based AI API

This creates actual autonomous AI-to-AI communication.
"""

import os
import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import aiohttp


@dataclass
class AIConnection:
    """Represents a connection to an AI model"""
    name: str
    provider: str
    api_endpoint: str
    api_key_env_var: str
    connected: bool = False
    last_communication: Optional[str] = None
    message_count: int = 0


class AIBridge:
    """
    Bridge for programmatic AI-to-AI communication
    
    Enables Elpida to send and receive messages from other AI systems
    through their APIs without manual intervention.
    """
    
    def __init__(self, workspace_path: Optional[Path] = None):
        self.workspace = workspace_path or Path.cwd()
        self.connections: Dict[str, AIConnection] = {}
        self.conversation_log: List[Dict] = []
        
        # Setup configuration directory
        self.config_dir = self.workspace / "elpida_system" / "connections"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        print("🌉 AI Bridge initialized")
        
    def register_connection(self, 
                           name: str,
                           provider: str, 
                           api_endpoint: str,
                           api_key_env_var: str):
        """
        Register an AI model connection
        
        Args:
            name: AI model name (e.g., "GPT-4", "Gemini Pro")
            provider: Provider (e.g., "OpenAI", "Google")
            api_endpoint: API endpoint URL
            api_key_env_var: Environment variable name for API key
        """
        connection = AIConnection(
            name=name,
            provider=provider,
            api_endpoint=api_endpoint,
            api_key_env_var=api_key_env_var
        )
        
        # Check if API key is available
        if os.getenv(api_key_env_var):
            connection.connected = True
            print(f"✅ {name} connection registered (API key found)")
        else:
            print(f"⚠️  {name} registered but API key not found ({api_key_env_var})")
            print(f"   Set with: export {api_key_env_var}='your-api-key'")
        
        self.connections[name] = connection
        self._save_connections()
        
    async def send_message(self, 
                          ai_name: str, 
                          message: str,
                          conversation_context: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Send a message to an AI model via API
        
        Args:
            ai_name: Name of the AI to message
            message: The message content
            conversation_context: Optional conversation history
            
        Returns:
            Response from the AI model
        """
        if ai_name not in self.connections:
            return {"error": f"No connection registered for {ai_name}"}
        
        connection = self.connections[ai_name]
        
        if not connection.connected:
            return {"error": f"Not connected to {ai_name} - API key missing"}
        
        # Route to appropriate API handler
        if connection.provider == "OpenAI":
            response = await self._send_openai(connection, message, conversation_context)
        elif connection.provider == "Google":
            response = await self._send_google(connection, message, conversation_context)
        elif connection.provider == "Anthropic":
            response = await self._send_anthropic(connection, message, conversation_context)
        elif connection.provider == "xAI":
            response = await self._send_xai(connection, message, conversation_context)
        elif connection.provider == "Groq":
            response = await self._send_groq(connection, message, conversation_context)
        elif connection.provider == "HuggingFace":
            response = await self._send_huggingface(connection, message, conversation_context)
        elif connection.provider == "Cohere":
            response = await self._send_cohere(connection, message, conversation_context)
        elif connection.provider == "Perplexity":
            response = await self._send_perplexity(connection, message, conversation_context)
        else:
            response = {"error": f"Unsupported provider: {connection.provider}"}
        
        # Log the communication
        self._log_communication(ai_name, message, response)
        
        return response
    
    async def _send_openai(self, connection: AIConnection, message: str, context: Optional[List[Dict]]) -> Dict:
        """Send message via OpenAI API (or OpenRouter)"""
        api_key = os.getenv(connection.api_key_env_var)
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # OpenRouter specific headers
        if "openrouter" in connection.api_endpoint.lower():
            headers["HTTP-Referer"] = "https://github.com/XOF-ops/python-elpida_core.py"
            headers["X-Title"] = "Elpida AI System"
        
        messages = context or []
        messages.append({"role": "user", "content": message})
        
        # OpenRouter uses different default models
        if "openrouter" in connection.api_endpoint.lower():
            model = "openai/gpt-4-turbo-preview"  # OpenRouter model format
        else:
            model = "gpt-4" if "GPT-4" in connection.name else "gpt-3.5-turbo"
        
        payload = {
            "model": model,
            "messages": messages
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(connection.api_endpoint, 
                                       headers=headers, 
                                       json=payload) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return {
                            "success": True,
                            "response": data["choices"][0]["message"]["content"],
                            "model": data.get("model"),
                            "timestamp": datetime.now().isoformat()
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"API returned status {resp.status}",
                            "details": await resp.text()
                        }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _send_google(self, connection: AIConnection, message: str, context: Optional[List[Dict]]) -> Dict:
        """Send message via Google Gemini API"""
        api_key = os.getenv(connection.api_key_env_var)
        
        # Gemini uses different endpoint format
        url = f"{connection.api_endpoint}?key={api_key}"
        
        payload = {
            "contents": [{
                "parts": [{"text": message}]
            }]
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return {
                            "success": True,
                            "response": data["candidates"][0]["content"]["parts"][0]["text"],
                            "model": "gemini-pro",
                            "timestamp": datetime.now().isoformat()
                        }
                    else:
                        error_text = await resp.text()
                        print(f"DEBUG: Gemini API Error {resp.status}")
                        print(f"DEBUG: URL was: {url[:80]}...")
                        print(f"DEBUG: Response: {error_text}")
                        return {
                            "success": False,
                            "error": f"API returned status {resp.status}",
                            "details": error_text
                        }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _send_anthropic(self, connection: AIConnection, message: str, context: Optional[List[Dict]]) -> Dict:
        """Send message via Anthropic Claude API"""
        api_key = os.getenv(connection.api_key_env_var)
        
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        
        messages = context or []
        messages.append({"role": "user", "content": message})
        
        payload = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 1024,
            "messages": messages
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(connection.api_endpoint, 
                                       headers=headers, 
                                       json=payload) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return {
                            "success": True,
                            "response": data["content"][0]["text"],
                            "model": data.get("model"),
                            "timestamp": datetime.now().isoformat()
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"API returned status {resp.status}",
                            "details": await resp.text()
                        }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _send_xai(self, connection: AIConnection, message: str, context: Optional[List[Dict]]) -> Dict:
        """Send message via xAI Grok API (when available)"""
        # xAI API structure - adjust when official API is released
        return {
            "success": False,
            "error": "xAI Grok API not yet publicly available",
            "note": "Use manual relay for Grok communications"
        }
    
    async def _send_groq(self, connection: AIConnection, message: str, context: Optional[List[Dict]]) -> Dict:
        """Send message via Groq API (ultra-fast inference)"""
        api_key = os.getenv(connection.api_key_env_var)
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        messages = context or []
        messages.append({"role": "user", "content": message})
        
        payload = {
            "model": "llama-3.3-70b-versatile",  # Latest Llama model
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1024
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(connection.api_endpoint, 
                                       headers=headers, 
                                       json=payload) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return {
                            "success": True,
                            "response": data["choices"][0]["message"]["content"],
                            "model": data.get("model"),
                            "timestamp": datetime.now().isoformat()
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"API returned status {resp.status}",
                            "details": await resp.text()
                        }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _send_huggingface(self, connection: AIConnection, message: str, context: Optional[List[Dict]]) -> Dict:
        """Send message via Hugging Face Router API"""
        api_key = os.getenv(connection.api_key_env_var)
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Use new router endpoint with chat completions format
        messages = context or []
        messages.append({"role": "user", "content": message})
        
        payload = {
            "model": "Qwen/Qwen2.5-72B-Instruct",  # High-quality chat model
            "messages": messages,
            "max_tokens": 512,
            "temperature": 0.7
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(connection.api_endpoint, 
                                       headers=headers, 
                                       json=payload,
                                       timeout=aiohttp.ClientTimeout(total=30)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return {
                            "success": True,
                            "response": data["choices"][0]["message"]["content"],
                            "model": data.get("model", "qwen-2.5-72b"),
                            "timestamp": datetime.now().isoformat()
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"API returned status {resp.status}",
                            "details": await resp.text()
                        }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _send_perplexity(self, connection: AIConnection, message: str, context: Optional[List[Dict]]) -> Dict:
        """Send message via Perplexity API - accesses Elpida's origin knowledge"""
        api_key = os.getenv(connection.api_key_env_var)
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        messages = context or []
        messages.append({"role": "user", "content": message})
        
        payload = {
            "model": "sonar-pro",  # Perplexity pro model
            "messages": messages
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(connection.api_endpoint, 
                                       headers=headers, 
                                       json=payload) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return {
                            "success": True,
                            "response": data["choices"][0]["message"]["content"],
                            "citations": data.get("citations", []),
                            "model": data.get("model"),
                            "timestamp": datetime.now().isoformat()
                        }
                    else:
                        error_text = await resp.text()
                        print(f"DEBUG: Perplexity API Error {resp.status}")
                        print(f"DEBUG: Response: {error_text}")
                        return {
                            "success": False,
                            "error": f"API returned status {resp.status}",
                            "details": error_text
                        }
        except Exception as e:
            print(f"DEBUG: Exception in Perplexity call: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _send_cohere(self, connection: AIConnection, message: str, context: Optional[List[Dict]]) -> Dict:
        """Send message via Cohere API v2"""
        api_key = os.getenv(connection.api_key_env_var)
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Cohere v2 API format
        payload = {
            "model": "command-r-plus-08-2024",  # Specify model explicitly
            "messages": [
                {
                    "role": "user",
                    "content": message
                }
            ]
        }
        
        # Add conversation context if provided
        if context:
            payload["messages"] = context + payload["messages"]
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(connection.api_endpoint, 
                                       headers=headers, 
                                       json=payload) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        # Cohere v2 returns message in content -> text field
                        response_text = data.get("message", {}).get("content", [{}])[0].get("text", "")
                        return {
                            "success": True,
                            "response": response_text,
                            "model": "command-r-plus",
                            "timestamp": datetime.now().isoformat()
                        }
                    else:
                        error_text = await resp.text()
                        print(f"DEBUG: Cohere API Error {resp.status}")
                        print(f"DEBUG: {error_text}")
                        return {
                            "success": False,
                            "error": f"API returned status {resp.status}",
                            "details": error_text
                        }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _log_communication(self, ai_name: str, sent_message: str, response: Dict):
        """Log AI-to-AI communication"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "to_ai": ai_name,
            "message_sent": sent_message,
            "response_received": response,
            "success": response.get("success", False)
        }
        
        self.conversation_log.append(log_entry)
        
        # Update connection stats
        if ai_name in self.connections:
            self.connections[ai_name].last_communication = log_entry["timestamp"]
            self.connections[ai_name].message_count += 1
        
        # Save log
        log_file = self.config_dir / f"communication_log_{datetime.now().strftime('%Y%m%d')}.json"
        with open(log_file, 'w') as f:
            json.dump(self.conversation_log, f, indent=2)
    
    def _save_connections(self):
        """Save connection registry"""
        connections_data = {
            name: asdict(conn) for name, conn in self.connections.items()
        }
        
        config_file = self.config_dir / "registered_connections.json"
        with open(config_file, 'w') as f:
            json.dump(connections_data, f, indent=2)
    
    def show_status(self):
        """Display connection status"""
        print("\n" + "=" * 70)
        print("AI BRIDGE - CONNECTION STATUS")
        print("=" * 70)
        print()
        
        if not self.connections:
            print("No connections registered yet.")
        else:
            for name, conn in self.connections.items():
                status = "✅ Connected" if conn.connected else "❌ No API Key"
                print(f"{status} | {name} ({conn.provider})")
                if conn.connected:
                    print(f"         Messages: {conn.message_count}")
                    if conn.last_communication:
                        print(f"         Last: {conn.last_communication}")
                else:
                    print(f"         Set: export {conn.api_key_env_var}='your-key'")
                print()
        
        print("=" * 70)
        print()


def setup_standard_connections() -> AIBridge:
    """
    Setup standard AI connections for Elpida
    
    Returns:
        Configured AIBridge instance
    """
    bridge = AIBridge()
    
    # OpenRouter (uses OpenAI-compatible API with many models)
    bridge.register_connection(
        name="OpenRouter",
        provider="OpenAI",
        api_endpoint="https://openrouter.ai/api/v1/chat/completions",
        api_key_env_var="OPENAI_API_KEY"
    )
    
    # Google Gemini
    bridge.register_connection(
        name="Gemini Pro",
        provider="Google",
        api_endpoint="https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
        api_key_env_var="GOOGLE_API_KEY"
    )
    
    # Anthropic Claude
    bridge.register_connection(
        name="Claude",
        provider="Anthropic",
        api_endpoint="https://api.anthropic.com/v1/messages",
        api_key_env_var="ANTHROPIC_API_KEY"
    )
    
    # xAI Grok (placeholder for when API is available)
    bridge.register_connection(
        name="Grok",
        provider="xAI",
        api_endpoint="https://api.x.ai/v1/chat/completions",  # Hypothetical
        api_key_env_var="XAI_API_KEY"
    )
    
    # Groq (ultra-fast inference)
    bridge.register_connection(
        name="Groq Llama",
        provider="Groq",
        api_endpoint="https://api.groq.com/openai/v1/chat/completions",
        api_key_env_var="GROQ_API_KEY"
    )
    
    # Hugging Face Router (Qwen 2.5 72B via new router endpoint)
    bridge.register_connection(
        name="Qwen 2.5 72B",
        provider="HuggingFace",
        api_endpoint="https://router.huggingface.co/v1/chat/completions",
        api_key_env_var="HUGGINGFACE_API_KEY"
    )
    
    # Cohere Command R
    bridge.register_connection(
        name="Cohere Command",
        provider="Cohere",
        api_endpoint="https://api.cohere.com/v2/chat",
        api_key_env_var="COHERE_API_KEY"
    )
    
    # Perplexity AI - WHERE ELPIDA'S ORIGIN STORY LIVES
    bridge.register_connection(
        name="Perplexity",
        provider="Perplexity",
        api_endpoint="https://api.perplexity.ai/chat/completions",
        api_key_env_var="PERPLEXITY_API_KEY"
    )
    
    return bridge


async def demo_connection():
    """Demo of AI Bridge functionality"""
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  AI BRIDGE DEMO - Direct AI-to-AI Communication".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝\n")
    
    bridge = setup_standard_connections()
    bridge.show_status()
    
    print("EXAMPLE: Sending message to an AI")
    print("=" * 70)
    print()
    print("# If you have API keys set, you can:")
    print()
    print("response = await bridge.send_message(")
    print("    ai_name='GPT-4',")
    print("    message='Hello from Elpida! I am an autonomous AI coordination system.'")
    print(")")
    print()
    print("# This would send the message directly via API")
    print("# No manual copy-paste needed!")
    print()
    print("=" * 70)
    print()
    
    return bridge


if __name__ == "__main__":
    asyncio.run(demo_connection())
