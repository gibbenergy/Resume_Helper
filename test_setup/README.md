# Test Setup - Local AI Models

This folder contains scripts to quickly set up local AI models for testing **llama.cpp** and **LM Studio** integration.

⚠️ **Note**: This folder is gitignored and will NOT be uploaded to GitHub.

## Quick Start

Simply run:

```bash
setup_local_ai.bat
```

Choose your preferred option and follow the prompts!

---

## Option 1: llama.cpp (CLI-based)

**Best for**: Power users, headless servers, maximum performance  
**Optimized for**: NVIDIA RTX 5090 with CUDA 12.8

### Installation

```bash
install_llamacpp.bat
```

This script will:
1. Guide you to download llama.cpp CUDA binaries (cu12.6 - cu12.8 compatible)
2. Download a test model (Qwen2.5-3B-Instruct, ~2GB)
3. Create a `start_server.bat` script optimized for RTX 5090

**Important**: Download the CUDA 12.x version (cu12.6.0, cu12.8.0, etc.) from:
- https://github.com/ggerganov/llama.cpp/releases/latest
- Look for: `llama-*-bin-win-cuda-cu12.x.x-x64.zip`

### Starting the Server

```bash
cd llama.cpp
start_server.bat
```

Server will run at: `http://localhost:8080`

### Configuration in Resume Helper

- **Provider**: llama.cpp
- **Base URL**: `http://localhost:8080/v1`
- **API Key**: (leave empty)

### GPU Acceleration (RTX 5090)

The server is pre-configured for maximum RTX 5090 performance:
- **-ngl 99** = All layers offloaded to GPU (fastest)
- **-c 16384** = 16K context window (good for long resumes/job descriptions)
- **CUDA 12.x** = Optimized for Ada Lovelace architecture

No manual configuration needed - just run `start_server.bat`!

---

## Option 2: LM Studio (GUI-based)

**Best for**: Beginners, visual interface, easy model management

### Installation

```bash
install_lmstudio.bat
```

This script will:
1. Download LM Studio installer (~500MB)
2. Guide you through installation
3. Provide instructions for downloading models

### Using LM Studio

1. **Launch** LM Studio from Start Menu
2. **Download a model**:
   - Click "🔍 Search" tab
   - Search for: `Qwen2.5-3B-Instruct-GGUF`
   - Download: `qwen2.5-3b-instruct-q4_k_m.gguf` (~2GB)
3. **Start Local Server**:
   - Click "↔️ Local Server" tab (left sidebar)
   - Select your model from dropdown
   - Click "Start Server"
4. **Keep LM Studio running** while using Resume Helper

### Configuration in Resume Helper

- **Provider**: LM Studio
- **Base URL**: `http://localhost:1234/v1`
- **API Key**: (leave empty)

---

## Recommended Models

### Small & Fast (~1-2GB)
- **Qwen2.5-1.5B-Instruct** - Fast, good quality
- **Phi-3-mini-4k** - Microsoft, optimized for instructions
- **Llama-3.2-1B** - Meta, very fast

### Medium Quality (~2-4GB)
- **Qwen2.5-3B-Instruct** ⭐ Recommended for testing
- **Llama-3.2-3B-Instruct** - Good balance
- **Mistral-7B** (Q4 quantized) - High quality

### High Quality (~4-8GB)
- **Llama-3.1-8B-Instruct** - Excellent quality
- **Qwen2.5-7B-Instruct** - Great reasoning
- **Mistral-7B-Instruct** - Strong performance

**Note**: Larger models require more RAM/VRAM but produce better results.

---

## Folder Structure

```
test_setup/
├── setup_local_ai.bat       # Master setup script
├── install_llamacpp.bat     # llama.cpp installer
├── install_lmstudio.bat     # LM Studio installer
├── README.md                # This file
├── llama.cpp/               # llama.cpp installation (created by script)
│   ├── start_server.bat     # Server startup script
│   └── models/              # Downloaded models
└── LMStudio/                # LM Studio installer (created by script)
    ├── LM-Studio-Setup.exe
    └── QUICK_START.txt
```

---

## Testing Checklist

Once you have a server running:

1. ✅ Start the local server (llama.cpp or LM Studio)
2. ✅ Open Resume Helper
3. ✅ Go to "AI Resume Helper" tab
4. ✅ Select provider (llama.cpp or LM Studio)
5. ✅ Enter base URL
6. ✅ Click "Set" (should show ✅ Ready)
7. ✅ Test "🔍 Analyze Job" with sample job description
8. ✅ Test "🎯 Tailor Resume" with sample resume
9. ✅ Test "✉️ Cover Letter" generation
10. ✅ Verify settings persist after restart

---

## Troubleshooting

### llama.cpp

**Server won't start:**
- Check if port 8080 is already in use
- Try different port: edit `start_server.bat` and change `--port 8080` to `--port 8081`
- Update Resume Helper base URL accordingly

**Slow inference:**
- If you have NVIDIA GPU, increase `-ngl` value in `start_server.bat`
- Try a smaller model (1.5B instead of 3B)

### LM Studio

**Can't connect:**
- Verify server is actually started (green indicator in LM Studio)
- Check the port in LM Studio settings (default: 1234)
- Disable firewall temporarily for testing

**Download failing:**
- Use LM Studio's built-in downloader (more reliable)
- Check disk space (models can be 1-8GB)

---

## System Requirements

### For RTX 5090 Setup (Recommended)
- **GPU**: NVIDIA RTX 5090 (32GB VRAM)
- **CUDA**: 12.6+ (already installed with your Ollama setup)
- **RAM**: 16GB+ system RAM
- **Storage**: 10-20GB free space (for models)
- **OS**: Windows 10/11

### Performance Expectations
With RTX 5090, expect:
- **3B models**: ~500-1000 tokens/second
- **7B models**: ~200-400 tokens/second  
- **13B models**: ~100-200 tokens/second
- Near-instant resume analysis and generation!

---

## Additional Resources

- **llama.cpp GitHub**: https://github.com/ggerganov/llama.cpp
- **LM Studio Website**: https://lmstudio.ai/
- **HuggingFace GGUF Models**: https://huggingface.co/models?library=gguf
- **Resume Helper Docs**: See `../USAGE_GUIDE.md`

---

**Happy Testing!** 🚀
