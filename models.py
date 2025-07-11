"""
Model configuration and provider management for WordPress Plugin Generator.
Supports OpenAI models directly and any LiteLLM-supported model via flexible prefixes.
"""

import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
from loguru import logger

# Try to import agents components
try:
    from agents import (
        ModelSettings, 
        AsyncOpenAI,
        OpenAIResponsesModel,
        OpenAIChatCompletionsModel,
        set_default_openai_client,
        set_tracing_disabled,
        set_default_openai_api
    )
    AGENTS_AVAILABLE = True
except ImportError:
    logger.warning("OpenAI Agents SDK not fully available")
    AGENTS_AVAILABLE = False

# Try to import LiteLLM support
try:
    from agents.extensions.models.litellm_model import LitellmModel
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False
    logger.debug("LiteLLM extension not available. Install with: pip install 'openai-agents[litellm]'")


class ModelProvider(Enum):
    """Model provider types."""
    OPENAI = "openai"
    LITELLM = "litellm"
    CUSTOM = "custom"


@dataclass
class ModelConfig:
    """Configuration for a model type."""
    provider: ModelProvider
    supports_responses_api: bool = True
    supports_structured_outputs: bool = True
    supports_multimodal: bool = True
    supports_tools: bool = True
    default_temperature: float = 0.7
    api_key_env_var: Optional[str] = None
    notes: Optional[str] = None


# Provider configurations (not specific models, but provider capabilities)
PROVIDER_CONFIGS: Dict[str, ModelConfig] = {
    "openai": ModelConfig(
        provider=ModelProvider.OPENAI,
        supports_responses_api=True,
        supports_structured_outputs=True,
        supports_multimodal=True,
        supports_tools=True,
        default_temperature=0.7,
        api_key_env_var="OPENAI_API_KEY",
        notes="OpenAI models with full feature support"
    ),
    "anthropic": ModelConfig(
        provider=ModelProvider.LITELLM,
        supports_responses_api=False,
        supports_structured_outputs=False,  # Limited JSON schema support
        supports_multimodal=True,
        supports_tools=True,
        default_temperature=0.7,
        api_key_env_var="ANTHROPIC_API_KEY",
        notes="Anthropic Claude models via LiteLLM"
    ),
    "google": ModelConfig(
        provider=ModelProvider.LITELLM,
        supports_responses_api=False,
        supports_structured_outputs=False,  # Limited JSON schema support
        supports_multimodal=True,
        supports_tools=True,
        default_temperature=0.7,
        api_key_env_var="GOOGLE_API_KEY",
        notes="Google Gemini models via LiteLLM"
    ),
    "groq": ModelConfig(
        provider=ModelProvider.LITELLM,
        supports_responses_api=False,
        supports_structured_outputs=False,
        supports_multimodal=False,
        supports_tools=True,
        default_temperature=0.7,
        api_key_env_var="GROQ_API_KEY",
        notes="Groq models via LiteLLM"
    ),
    "cohere": ModelConfig(
        provider=ModelProvider.LITELLM,
        supports_responses_api=False,
        supports_structured_outputs=False,
        supports_multimodal=False,
        supports_tools=True,
        default_temperature=0.7,
        api_key_env_var="COHERE_API_KEY",
        notes="Cohere models via LiteLLM"
    ),
    "ollama": ModelConfig(
        provider=ModelProvider.LITELLM,
        supports_responses_api=False,
        supports_structured_outputs=True,  # Supports JSON mode
        supports_multimodal=True,  # Some models support vision
        supports_tools=True,  # Supports function calling
        default_temperature=0.7,
        api_key_env_var=None,  # No API key needed for local Ollama
        notes="Local Ollama models (requires Ollama server running)"
    ),
}

# Convenient shortcuts for common models
# No hardcoded shortcuts - users should use the flexible LiteLLM format:
# - OpenAI models: gpt-4o, gpt-4o-mini, o1-preview, etc.
# - LiteLLM format: litellm/provider/model-name
# - Direct provider format: ollama/model-name, anthropic/model-name (if supported)
# 
# Examples:
# - gpt-4o
# - litellm/anthropic/claude-3-5-sonnet-20241022
# - litellm/groq/llama-3.1-70b-versatile  
# - ollama/llama3.2:latest
MODEL_SHORTCUTS = {}


class ModelManager:
    """Manages model configuration and selection with flexible LiteLLM support."""
    
    def __init__(self):
        self.current_model = os.getenv("DEFAULT_MODEL", "gpt-4o")
        self._setup_environment()
    
    def _setup_environment(self):
        """Setup environment based on configuration."""
        # Disable tracing if specified
        if os.getenv("DISABLE_TRACING", "false").lower() == "true":
            if AGENTS_AVAILABLE:
                set_tracing_disabled(True)
                logger.info("Tracing disabled")
        
        # Set default API if using chat completions
        if os.getenv("USE_CHAT_COMPLETIONS_API", "false").lower() == "true":
            if AGENTS_AVAILABLE:
                set_default_openai_api("chat_completions")
                logger.info("Using Chat Completions API by default")
    
    def resolve_model_name(self, model_name: Optional[str] = None) -> str:
        """Return model name as-is - no shortcuts, full flexibility."""
        return model_name or self.current_model
    
    def get_provider_from_model(self, model_name: str) -> str:
        """Extract provider name from model string."""
        resolved_name = self.resolve_model_name(model_name)
        
        # Check if it's a litellm/ prefixed model
        if resolved_name.startswith("litellm/"):
            # Extract provider from litellm/provider/model format
            parts = resolved_name.split("/")
            if len(parts) >= 2:
                provider = parts[1]  # Return the provider part
                
                # Map some provider names to our internal names
                provider_mapping = {
                    "gemini": "google",  # Map gemini to google
                    "anthropic": "anthropic",
                    "groq": "groq", 
                    "cohere": "cohere",
                    "ollama": "ollama",  # Map ollama to ollama
                    "ollama_chat": "ollama",  # Map ollama_chat to ollama
                }
                return provider_mapping.get(provider, provider)
            return "litellm"
        
        # Check if it's a direct ollama/ model
        if resolved_name.startswith("ollama/"):
            return "ollama"
        
        # Check if it's a Claude model (Anthropic)
        if resolved_name.startswith("claude-"):
            return "anthropic"
        
        # Check if it's a known OpenAI model pattern
        openai_models = ["gpt-", "o1-", "text-", "davinci", "curie", "babbage", "ada"]
        if any(resolved_name.startswith(prefix) for prefix in openai_models):
            return "openai"
        
        # Default to OpenAI for unknown models
        return "openai"
    
    def get_model_config(self, model_name: Optional[str] = None) -> ModelConfig:
        """Get configuration for a model based on its provider."""
        resolved_name = self.resolve_model_name(model_name)
        provider = self.get_provider_from_model(resolved_name)
        
        # Get provider config or default to OpenAI
        if provider in PROVIDER_CONFIGS:
            config = PROVIDER_CONFIGS[provider]
        else:
            logger.warning(f"Unknown provider '{provider}', defaulting to OpenAI configuration")
            config = PROVIDER_CONFIGS["openai"]
        
        return config
    
    def create_model_instance(self, model_name: Optional[str] = None, 
                            temperature: Optional[float] = None,
                            api_key: Optional[str] = None):
        """Create a model instance for use with agents."""
        resolved_name = self.resolve_model_name(model_name)
        config = self.get_model_config(resolved_name)
        provider = self.get_provider_from_model(resolved_name)
        
        # Use provided temperature or model's default
        temp = temperature if temperature is not None else config.default_temperature
        
        # For LiteLLM models (including direct ollama/ format and Claude models)
        if (resolved_name.startswith("litellm/") or 
            resolved_name.startswith("ollama/") or 
            provider != "openai"):
            
            if not LITELLM_AVAILABLE:
                raise ImportError(
                    "LiteLLM extension not available. Install with: pip install 'openai-agents[litellm]'"
                )
            
            # Get API key from parameter or environment (if required)
            if not api_key and config.api_key_env_var:
                api_key = os.getenv(config.api_key_env_var)
            
            # Check if API key is required for this provider
            if config.api_key_env_var and not api_key:
                raise ValueError(
                    f"API key required for {provider}. Set {config.api_key_env_var} "
                    f"environment variable or pass api_key parameter."
                )
            
            # For Ollama, we don't need an API key, just pass a dummy one
            if provider == "ollama":
                api_key = "dummy-key"  # Ollama doesn't use API keys
            
            # Return LitellmModel instance
            return LitellmModel(model=resolved_name, api_key=api_key)
        
        # For OpenAI models, just return the model name
        return resolved_name
    
    def get_model_settings(self, temperature: Optional[float] = None,
                         model_name: Optional[str] = None) -> Optional[ModelSettings]:
        """Get ModelSettings for a specific model."""
        if not AGENTS_AVAILABLE:
            return None
            
        resolved_name = self.resolve_model_name(model_name)
        config = self.get_model_config(resolved_name)
        temp = temperature if temperature is not None else config.default_temperature
        
        # For o1 models, temperature is fixed
        if resolved_name.startswith("o1"):
            return ModelSettings(temperature=1.0)
        
        return ModelSettings(temperature=temp)
    
    def list_available_models(self) -> List[Dict[str, Any]]:
        """List supported providers with example model names."""
        examples = []
        
        # Add provider examples
        provider_examples = {
            "openai": ["gpt-4o", "gpt-4o-mini", "o1-preview", "o1-mini"],
            "anthropic": [
                "litellm/anthropic/claude-3-5-sonnet-20241022",
                "litellm/anthropic/claude-3-5-haiku-20241022",
                "litellm/anthropic/claude-3-opus-20240229"
            ],
            "google": [
                "litellm/gemini/gemini-2.0-flash-exp",
                "litellm/gemini/gemini-1.5-pro",
                "litellm/gemini/gemini-1.5-flash"
            ],
            "groq": [
                "litellm/groq/llama-3.1-70b-versatile",
                "litellm/groq/mixtral-8x7b-32768"
            ],
            "ollama": [
                "ollama/llama3.2:latest",
                "ollama/llama3.1:latest",
                "ollama/codellama:latest"
            ]
        }
        
        for provider, model_list in provider_examples.items():
            config = PROVIDER_CONFIGS.get(provider, PROVIDER_CONFIGS["openai"])
            
            for model_name in model_list:
                examples.append({
                    "provider": provider,
                    "example_model": model_name,
                    "supports_responses_api": config.supports_responses_api,
                    "supports_structured_outputs": config.supports_structured_outputs,
                    "supports_multimodal": config.supports_multimodal,
                    "supports_tools": config.supports_tools,
                    "notes": config.notes or ""
                })
        
        return sorted(examples, key=lambda x: (x["provider"], x["example_model"]))
    
    def get_supported_providers(self) -> List[Dict[str, Any]]:
        """Get list of supported providers with their capabilities."""
        providers = []
        
        for provider_name, config in PROVIDER_CONFIGS.items():
            providers.append({
                "name": provider_name,
                "api_key_env_var": config.api_key_env_var,
                "supports_responses_api": config.supports_responses_api,
                "supports_structured_outputs": config.supports_structured_outputs,
                "supports_multimodal": config.supports_multimodal,
                "supports_tools": config.supports_tools,
                "notes": config.notes or ""
            })
        
        return sorted(providers, key=lambda x: x["name"])
    
    def validate_api_keys(self) -> Dict[str, bool]:
        """Check which API keys are available."""
        results = {}
        
        for provider_name, config in PROVIDER_CONFIGS.items():
            if config.api_key_env_var:
                results[provider_name] = bool(os.getenv(config.api_key_env_var))
            else:
                results[provider_name] = True  # No API key required
        
        return results
    
    def suggest_models_for_provider(self, provider: str) -> List[str]:
        """Suggest example model names for a given provider."""
        suggestions = {
            "anthropic": [
                "litellm/anthropic/claude-3-5-sonnet-20241022",
                "litellm/anthropic/claude-3-5-haiku-20241022", 
                "litellm/anthropic/claude-3-opus-20240229"
            ],
            "google": [
                "litellm/gemini/gemini-2.0-flash-exp",
                "litellm/gemini/gemini-1.5-pro",
                "litellm/gemini/gemini-1.5-flash"
            ],
            "openai": [
                "gpt-4o",
                "gpt-4o-mini",
                "o1-preview",
                "o1-mini"
            ],
            "groq": [
                "litellm/groq/llama-3.1-70b-versatile",
                "litellm/groq/mixtral-8x7b-32768"
            ],
            "ollama": [
                "ollama/llama3.2:latest",
                "ollama/llama3.1:latest",
                "ollama/codellama:latest"
            ]
        }
        
        return suggestions.get(provider, [])


# Global model manager instance
model_manager = ModelManager() 