# llama.cpp & LM Studio Integration - Testing Guide

## Implementation Summary

This branch adds support for **llama.cpp** and **LM Studio** as local AI providers through their OpenAI-compatible APIs.

## Features Implemented

### Backend (LiteLLMProvider)
✅ Added `llamacpp` and `lmstudio` provider configurations
✅ Implemented `custom_base_url` parameter support
✅ Added `_set_base_url()` and `get_base_url()` methods
✅ Modified API completion calls to use custom base URLs
✅ Updated API key handling (dummy keys for local providers)
✅ Enhanced provider switching with base URL support

### Frontend (UI)
✅ Added "llama.cpp" and "LM Studio" to provider dropdown
✅ Created custom base URL input field with dynamic visibility
✅ Updated all provider initialization functions to handle base URLs
✅ Modified configuration save/load to persist custom URLs
✅ Enhanced AI configuration panel with setup notes

### Documentation
✅ Comprehensive README updates with all provider options
✅ Detailed USAGE_GUIDE with step-by-step setup for each provider
✅ Installation instructions for llama.cpp (binary + source)
✅ LM Studio GUI usage guide
✅ Configuration examples for each provider

## Testing Checklist

### Unit Testing (Code Level)
✅ No linting errors in modified files
✅ Type hints properly added for new parameters
✅ Error handling implemented for connection failures
✅ Default values set for all new parameters

### Integration Testing (To Be Performed by User)

#### Test 1: llama.cpp Integration
1. Install llama.cpp server
2. Download a GGUF model (e.g., Llama-2-7B-Chat)
3. Start server: `./server -m model.gguf --host 0.0.0.0 --port 8080`
4. In Resume Helper:
   - Select "llama.cpp" provider
   - Enter base URL: `http://localhost:8080/v1`
   - Leave API key empty
   - Click "Set"
5. Expected: ✅ Connection successful message
6. Test job analysis with a sample job description
7. Expected: AI-generated analysis appears

#### Test 2: LM Studio Integration
1. Install LM Studio
2. Download a model through LM Studio GUI
3. Start local server (default: `http://localhost:1234`)
4. In Resume Helper:
   - Select "LM Studio" provider
   - Enter base URL: `http://localhost:1234/v1`
   - Leave API key empty
   - Click "Set"
5. Expected: ✅ Connection successful message
6. Test resume tailoring with sample data
7. Expected: AI-tailored resume generated

#### Test 3: Settings Persistence
1. Configure llama.cpp or LM Studio
2. Close Resume Helper
3. Reopen Resume Helper
4. Expected: Provider, model, and base URL settings are restored
5. Check `.env` file contains:
   - `RESUME_HELPER_LAST_PROVIDER=llama.cpp` (or LM Studio)
   - `CUSTOM_BASE_URL=http://localhost:xxxx/v1`

#### Test 4: Error Handling
1. Select llama.cpp without running server
2. Click "Set"
3. Expected: ❌ Error message about connection failure
4. Start llama.cpp server
5. Click "Set" again
6. Expected: ✅ Connection successful

#### Test 5: Provider Switching
1. Start with llama.cpp configured
2. Switch to LM Studio
3. Expected: Base URL field updates to LM Studio default
4. Switch to OpenAI
5. Expected: Base URL field hidden, API key field shown
6. Switch back to llama.cpp
7. Expected: Previous base URL restored

## Known Limitations

1. **Model Discovery**: Unlike Ollama, llama.cpp and LM Studio don't expose model lists via API, so we use a generic "openai/local-model" placeholder
2. **Response Format**: Some older models may not support structured JSON output - handled by removing `response_format` parameter
3. **Base URL Validation**: Currently no client-side validation of URL format (to allow flexibility)

## Configuration Examples

### llama.cpp Default Setup
```
Provider: llama.cpp
Base URL: http://localhost:8080/v1
API Key: (leave empty)
Model: openai/local-model
```

### LM Studio Default Setup
```
Provider: LM Studio
Base URL: http://localhost:1234/v1
API Key: (leave empty)
Model: openai/local-model
```

### Custom Port Examples
```
llama.cpp on custom port:
Base URL: http://localhost:9000/v1

LM Studio on custom port:
Base URL: http://localhost:5000/v1

Remote server:
Base URL: http://192.168.1.100:8080/v1
```

## Environment Variables

The following variables are saved to `.env`:

```bash
# Last selected provider (UI display name)
RESUME_HELPER_LAST_PROVIDER=llama.cpp

# Last selected model
RESUME_HELPER_LAST_MODEL=openai/local-model

# Custom base URL for OpenAI-compatible endpoints
CUSTOM_BASE_URL=http://localhost:8080/v1

# API keys (dummy for local providers)
LLAMACPP_API_KEY=sk-no-key-required
LMSTUDIO_API_KEY=sk-no-key-required
```

## Troubleshooting

### Issue: "Connection failed"
- Verify the server is running: `curl http://localhost:8080/v1/models`
- Check firewall settings
- Ensure correct port number in base URL
- Verify server is bound to `0.0.0.0` not just `127.0.0.1`

### Issue: "Empty response"
- Model may not support the requested format
- Check llama.cpp server logs for errors
- Try a different model with better instruction following

### Issue: "Base URL field not showing"
- Refresh the page
- Verify provider is set to "llama.cpp" or "LM Studio"
- Check browser console for JavaScript errors

## Next Steps

1. User should test with actual llama.cpp/LM Studio installations
2. Collect feedback on UX and error messages
3. Consider adding:
   - URL validation with visual feedback
   - Connection status indicator (red/green)
   - Model discovery for LM Studio (if API supports it)
   - Performance metrics (tokens/sec, latency)

## Commit Details

**Branch**: `4-support-llamacpplm-studio-through-openai-api`
**Commit Hash**: `ad1bd16`
**Files Modified**: 5
**Lines Changed**: +277, -43

## Ready for Review

This implementation is complete and ready for:
1. Code review
2. User acceptance testing
3. Merge to main branch (after testing)

---

*Generated: January 9, 2026*
