<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-00D4AA?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/Platform-macOS%20|%20Windows%20|%20Linux-FF6B6B?style=for-the-badge" alt="Platform">
</p>

<p align="center">
  <img src="assets/icon.png" width="128" height="128" alt="App Icon">
</p>

<h1 align="center">Audio Reactive Video Generator</h1>

<p align="center">
  <strong>Transform static images into dynamic, audio-synchronized videos</strong>
  <br>
  Perfect for music visualizers, Spotify Canvas, social media content, and more
</p>

<p align="center">
  <strong>BE CAREFUL!</strong>
  <br>
  This project created entirely VIBE CODED with OPUS 4.5 and Sonnet 4.5 models.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/No_AI_at_Runtime-100%25_Deterministic-00f0ff?style=flat-square" alt="No AI">
  <img src="https://img.shields.io/badge/Output-MP4_(H.264+AAC)-ff6b6b?style=flat-square" alt="Output">
  <img src="https://img.shields.io/badge/FPS-30-a855f7?style=flat-square" alt="FPS">
</p>

---

## 📥 Download

### Pre-built Binaries

Download the latest release for your platform:

| Platform                          | Download                                                                                              | Requirements  |
| --------------------------------- | ----------------------------------------------------------------------------------------------------- | ------------- |
| **macOS** (Apple Silicon & Intel) | [Audio Reactive.dmg](https://github.com/boraoksuzoglu/audio-reactive-video-generator/releases/latest) | macOS 11+     |
| **Windows** (64-bit)              | [Audio Reactive.exe](https://github.com/boraoksuzoglu/audio-reactive-video-generator/releases/latest) | Windows 10+   |
| **Linux**                         | [audio-reactive](https://github.com/boraoksuzoglu/audio-reactive-video-generator/releases/latest)     | Ubuntu 20.04+ |

> **Note:** Pre-built binaries are standalone — no Python installation required.

---

## ✨ Features

- **Audio-Reactive Effects** — Image transforms sync perfectly to your music
- **No Overlays** — The image itself pulses, glows, and reacts (no bars or waveforms)
- **10 Style Presets** — From subtle to psychedelic, find your vibe instantly
- **11 Configurable Effects** — Fine-tune every visual parameter
- **Desktop GUI** — Modern, dark-themed interface with real-time progress
- **CLI Support** — Automate batch processing with command-line tools
- **Wide Format Support** — MP3, WAV, FLAC, M4A, PNG, JPG, WebP, and more

---

## 🎬 Use Cases

| Platform            | Format         | Use                            |
| ------------------- | -------------- | ------------------------------ |
| **Spotify Canvas**  | 3-8 sec loop   | Artist profile videos          |
| **Instagram Reels** | 9:16 vertical  | Music promotion                |
| **TikTok**          | 9:16 vertical  | Audio visualizers              |
| **YouTube**         | 16:9 landscape | Lyric videos, album art videos |
| **SoundCloud**      | Any            | Track visualizers              |

---

## 🚀 Quick Start

### Option 1: Download Pre-built App

1. Download the app for your platform from the [Releases](https://github.com/boraoksuzoglu/audio-reactive-video-generator/releases) page
2. **macOS:** Open the `.dmg`, drag to Applications, right-click → Open (first time only)
3. **Windows:** Run the `.exe` file directly
4. **Linux:** Make executable with `chmod +x` and run

### Option 2: Run from Source

```bash
# Clone the repository
git clone https://github.com/boraoksuzoglu/audio-reactive-video-generator.git
cd audio-reactive-video-generator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the GUI
python gui.py
```

#### macOS Tkinter Note

If you encounter Tkinter issues on macOS with Homebrew Python:

```bash
brew install python-tk@3.13  # Match your Python version
```

### Run via CLI

```bash
python main.py --audio music.mp3 --image cover.png --output video.mp4 --preset energetic
```

---

## 🔨 Building from Source

Build standalone executables for distribution.

### Prerequisites

```bash
pip install -r requirements.txt  # Includes PyInstaller
```

### Build Commands

```bash
# Build for current platform
python build.py

# Or specify platform
python build.py macos    # Creates .app bundle + .dmg
python build.py windows  # Creates .exe
python build.py linux    # Creates executable

# Clean build artifacts
python build.py clean
```

### Build Output

| Platform | Output                           | Location                  |
| -------- | -------------------------------- | ------------------------- |
| macOS    | `Audio Reactive.app`             | `dist/Audio Reactive.app` |
| macOS    | `Audio Reactive-2.0.0-macOS.dmg` | `dist/`                   |
| Windows  | `Audio Reactive.exe`             | `dist/Audio Reactive.exe` |
| Linux    | `audio-reactive`                 | `dist/audio-reactive`     |

### Code Signing (Optional)

**macOS:** Sign the app for distribution:

```bash
codesign --deep --force --sign "Developer ID Application: Your Name" "dist/Audio Reactive.app"
```

**Windows:** Sign with signtool:

```bash
signtool sign /f certificate.pfx /p password "dist/Audio Reactive.exe"
```

---

## 🎨 Style Presets

| Preset        | Description                 | Best For                      |
| ------------- | --------------------------- | ----------------------------- |
| `subtle`      | Gentle, understated effects | Acoustic, ambient, classical  |
| `energetic`   | Balanced, dynamic response  | Pop, rock, indie              |
| `aggressive`  | Bold, intense visuals       | EDM, metal, dubstep           |
| `cinematic`   | Film-like atmosphere        | Soundtracks, orchestral       |
| `dreamy`      | Soft, ethereal glow         | Lo-fi, chillwave, R&B         |
| `retro`       | VHS / synthwave aesthetic   | 80s, synthwave, vaporwave     |
| `minimal`     | Clean, subtle pulse         | Podcasts, speech, ambient     |
| `psychedelic` | Trippy, experimental        | Experimental, psytrance       |
| `bass`        | Punchy low-end response     | Hip-hop, trap, bass music     |
| `noir`        | Dark, moody contrast        | Jazz, blues, noir soundtracks |

---

## 🎛️ Visual Effects

| Effect           | Description                             |
| ---------------- | --------------------------------------- |
| **Pulse Zoom**   | Subtle scale in/out synced to bass hits |
| **Camera Shake** | Micro-movement that responds to beats   |
| **Bloom / Glow** | Soft light diffusion on loud moments    |
| **Saturation**   | Color intensity modulation              |
| **Contrast**     | Dynamic contrast enhancement            |
| **Brightness**   | Light level changes with energy         |
| **Hue Shift**    | Subtle color rotation                   |
| **Vignette**     | Edge darkening that pulses inversely    |
| **Color Split**  | Chromatic aberration on peaks           |
| **Motion Blur**  | Blur effect on strong beats             |
| **Distortion**   | Subtle warp/ripple effect               |

---

## 📁 Supported Formats

### Audio Input

| Format              | Extension       |
| ------------------- | --------------- |
| MP3                 | `.mp3`          |
| WAV                 | `.wav`          |
| FLAC                | `.flac`         |
| OGG                 | `.ogg`          |
| M4A / AAC           | `.m4a`, `.aac`  |
| AIFF                | `.aiff`         |
| WMA                 | `.wma`          |
| Video (audio track) | `.mp4`, `.webm` |

### Image Input

| Format            | Extension       |
| ----------------- | --------------- |
| PNG               | `.png`          |
| JPEG              | `.jpg`, `.jpeg` |
| WebP              | `.webp`         |
| BMP               | `.bmp`          |
| TIFF              | `.tiff`         |
| GIF (first frame) | `.gif`          |

### Video Output

| Format | Codec                   |
| ------ | ----------------------- |
| MP4    | H.264 video + AAC audio |

---

## 🖥️ CLI Reference

```
usage: main.py [-h] -a AUDIO -i IMAGE [-o OUTPUT] [-p PRESET] [-q]

Generate audio-reactive video with image effects

options:
  -h, --help            show this help message and exit
  -a, --audio AUDIO     Path to input audio file
  -i, --image IMAGE     Path to input background image
  -o, --output OUTPUT   Path for output MP4 video (default: output/output.mp4)
  -p, --preset PRESET   Effect preset (default: energetic)
                        Choices: subtle, energetic, aggressive, cinematic,
                        dreamy, retro, minimal, psychedelic, bass, noir
  -q, --quiet           Suppress progress output
```

### Examples

```bash
# Basic usage
python main.py -a song.mp3 -i artwork.png

# With specific preset
python main.py -a track.wav -i cover.jpg -o music_video.mp4 --preset retro

# Quiet mode for scripting
python main.py -a audio.m4a -i bg.webp -o out.mp4 -p aggressive -q
```

---

## 📐 Project Structure

```
audio-reactive-video-generator/
├── main.py              # CLI entry point
├── gui.py               # Desktop GUI application
├── build.py             # Build script for executables
├── requirements.txt     # Python dependencies
├── assets/
│   └── icon.png         # Application icon
├── core/
│   ├── __init__.py      # Package exports
│   ├── audio.py         # Audio analysis (librosa)
│   ├── effects.py       # Visual effects engine
│   ├── renderer.py      # Frame renderer
│   └── video.py         # Video composer (moviepy)
├── audio/               # Input audio files
├── image/               # Input images
└── output/              # Generated videos
```

---

## ⚙️ Technical Details

### Audio Analysis

- Uses **librosa** for audio feature extraction
- Extracts frequency bands: bass (0-250Hz), mid (250-2000Hz), high (2000Hz+)
- Frame-aligned energy values at 30 FPS
- Smoothing applied to reduce jitter

### Rendering Pipeline

1. Load audio → Extract features per frame
2. Load image → Initialize effects processor
3. For each frame: Apply all enabled effects based on audio energy
4. Compose video with moviepy (H.264 + AAC)

### Performance

- Targets **2x realtime** or better on modern hardware
- In-memory frame processing (no temp files)
- Threaded GUI rendering for responsive UI

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [librosa](https://librosa.org/) — Audio analysis
- [Pillow](https://pillow.readthedocs.io/) — Image processing
- [moviepy](https://zulko.github.io/moviepy/) — Video composition
- [CustomTkinter](https://customtkinter.tomschimansky.com/) — Modern GUI toolkit
- [PyInstaller](https://pyinstaller.org/) — Executable bundling

---

<p align="center">
  <strong>Made with ♪ for musicians and content creators</strong>
</p>
