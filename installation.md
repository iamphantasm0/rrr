# Installation Guide - FFmpeg & LibRAW Setup

This guide will help you install the system dependencies for optimal performance.

## Quick Start

**Choose your setup:**
1. **Recommended**: ffmpeg + libraw (best performance + quality)
2. **Fallback**: Python libraries only (easier setup, slower)

---

## Option 1: FFmpeg + LibRAW (Recommended)

### Windows

**Method 1: Using winget (Windows 10/11)**
```powershell
# Install ffmpeg
winget install ffmpeg

# Install libraw (for dcraw_emu)
# Download from: https://www.libraw.org/download
# Extract and add to PATH
```

**Method 2: Manual Installation**
1. **FFmpeg:**
   - Download from: https://ffmpeg.org/download.html#build-windows
   - Extract to `C:\ffmpeg`
   - Add `C:\ffmpeg\bin` to system PATH

2. **LibRAW:**
   - Download from: https://www.libraw.org/download
   - Extract and add `bin` folder to PATH
   - Verify: `dcraw_emu` command should work in terminal

**Verify Installation:**
```powershell
ffmpeg -version
dcraw_emu
```

### Linux (Ubuntu/Debian)

```bash
# Install ffmpeg
sudo apt update
sudo apt install ffmpeg

# Install libraw (includes dcraw_emu)
sudo apt install libraw-bin

# Verify
ffmpeg -version
dcraw_emu
```

### macOS

```bash
# Using Homebrew
brew install ffmpeg
brew install libraw

# Verify
ffmpeg -version
dcraw_emu
```

---

## Option 2: Python Libraries Fallback

If you can't install ffmpeg/libraw, the script automatically falls back to Python libraries.

**Install fallback dependencies:**
```bash
pip install Pillow rawpy imageio
```

**Note:** This is slower but works without system dependencies.

---

## Performance Comparison

| Method | Speed | RAW Quality | Setup Complexity |
|--------|-------|-------------|------------------|
| **ffmpeg + libraw** | ⚡⚡⚡ Fast | ⭐⭐⭐ Excellent | Medium |
| **Python libs** | 🐌 Slow | ⭐⭐ Good | Easy |

### Real-world example (100 images):
- **ffmpeg + libraw**: ~30 seconds
- **Python libraries**: ~3-5 minutes

---

## Testing Your Setup

Run this in your terminal:

```bash
python -c "from image_processing import check_dependencies; print(check_dependencies())"
```

**Expected output:**
```
{'ffmpeg': True, 'dcraw_emu': True}
```

---

## Troubleshooting

### "ffmpeg not found"
- **Windows**: Check PATH environment variable includes ffmpeg/bin
- **Linux/Mac**: Try `which ffmpeg` to verify installation

### "dcraw_emu not found"
- Install libraw package for your OS
- On Linux: `sudo apt install libraw-bin`
- On macOS: `brew install libraw`

### Script still uses Python libraries
- Restart terminal after installing ffmpeg
- Verify with: `ffmpeg -version` and `dcraw_emu`

---

## What the Script Does

### With ffmpeg + libraw:
```
RAW files (CR2, NEF, etc.)
  → dcraw_emu (camera white balance, no auto-brightness)
  → TIFF (intermediate)
  → ffmpeg (JPEG quality 95)
  → Final JPG

Standard files (PNG, WEBP, etc.)
  → ffmpeg (JPEG quality 95)
  → Final JPG
```

### Fallback (Python libraries):
```
RAW files → rawpy → JPG
Standard files → Pillow → JPG
```

---

## Recommended Setup

For production use on the server hosting lasacoassurance.com:

1. Install ffmpeg and libraw on the server
2. Keep Python libraries as backup
3. Script automatically chooses best available method

This ensures maximum performance while maintaining reliability.