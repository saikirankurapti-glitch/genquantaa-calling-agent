# GenQuantaa Calling Agent — LLM Integration Architecture

**Document Version:** 1.0.0  
**Date:** August 19, 2026  
**Status:** Approved Provider Specification  

---

## 1. Supported LLM Providers

| LLM Provider | Service Class | Default Models | Streaming | Tool Calling | Local Test Status |
| :--- | :--- | :--- | :---: | :---: | :---: |
| **OpenAI** | `OpenAILLMService` | `gpt-4o`, `gpt-4o-mini` | YES | YES | TESTED & READY |
| **Anthropic** | `AnthropicLLMService` | `claude-3-5-sonnet`, `claude-3-haiku` | YES | YES | Supported |
| **Google Gemini**| `GeminiLLMService` | `gemini-2.5-flash`, `gemini-1.5-flash` | YES | YES | Supported |
| **Groq** | `GroqLLMService` | `llama-3.3-70b-versatile` | YES | YES | Supported |
| **OpenRouter** | `OpenRouterLLMService` | Custom OpenRouter IDs | YES | YES | Supported |
