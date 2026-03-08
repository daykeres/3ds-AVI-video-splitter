# 3ds-AVI-video-splitter
Python program to separate video channels from AVI videos recorded with a Nintendo 3DS

# Dual-Channel AVI Manager

A powerful Python tool designed to manage, preview, and split multi-stream AVI files (common in CCTV, Dashcams, and specialized recording equipment). It allows for high-performance dual-channel synchronized preview and lossless batch exporting.

- **Batch Processing:** Load multiple AVI files at once.
- **Visual Sidebar:** Browse your files with automatically generated thumbnails.
- **Lossless Export:** Splits channels using `ffmpeg -c copy`. This ensures **Resolution, Bitrate, and FPS** remain exactly the same as the original.
- **Automatic Audio Mapping:** Keeps the original audio track in both exported files.

## Requirements

1. **Python 3.x**
2. **FFmpeg:** Must be installed and added to your system **PATH**.
   - [Download FFmpeg here](https://ffmpeg.org/download.html)
3. **Pillow Library:** For UI image handling.
   ```bash
   pip install Pillow
