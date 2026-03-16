# 🖱️ Air Mouse — Touchless Gesture Control System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10+-00BFA5?style=for-the-badge&logo=google&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge)

**Control your entire computer with just your hands. No mouse. No keyboard. No touch.**

*Real-time hand tracking · Virtual keyboard · Air scrolling · Gesture clicks*

</div>

---

## 📸 Demo

> 🎥 *Demo video / GIF coming soon — record with OBS and drop it here*

---

## ✨ What Is This?

**Air Mouse** is a computer vision project that replaces your physical mouse and keyboard with hand gestures, tracked live through a webcam. Using **MediaPipe** for 21-point hand landmark detection and **OpenCV** for video processing, it maps your hand movements directly to system-level cursor control, scrolling, and typing — all in real time.

Built as part of a larger **Jarvis-like AI assistant** project focused on accessibility and touchless interaction.

---

## 🎯 Features

| Feature | Description |
|---|---|
| 🖱️ **Air Mouse** | Right hand controls cursor movement across the screen |
| 👆 **Gesture Click** | Pinch (thumb + index finger) to left-click |
| 📜 **Air Scroll** | Left hand controls scroll up / down |
| ⌨️ **Virtual Keyboard** | On-screen 60% QWERTY keyboard for touchless typing |
| ⚡ **Real-Time** | Sub-100ms latency on standard webcam input |
| 🎥 **Standard Hardware** | Works with any 720p+ webcam, no special sensors |

---

## 🧠 How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                        AIR MOUSE PIPELINE                       │
└─────────────────────────────────────────────────────────────────┘

  📷 Webcam Feed
       │
       ▼
  ┌──────────────┐
  │  OpenCV      │  ← Captures live 720p video frames
  │  VideoCapture│
  └──────┬───────┘
         │
         ▼
  ┌──────────────┐
  │  MediaPipe   │  ← Detects 21 hand landmarks per hand
  │  Hands Model │     (x, y, z coordinates per point)
  └──────┬───────┘
         │
         ▼
  ┌──────────────────────────────────────────┐
  │            GESTURE CLASSIFIER            │
  │                                          │
  │   Right Hand?          Left Hand?        │
  │   ┌──────────┐         ┌──────────┐      │
  │   │ Cursor   │         │ Scroll   │      │
  │   │ Movement │         │ Up/Down  │      │
  │   └──────────┘         └──────────┘      │
  │        │                                 │
  │   Pinch detected?                        │
  │   ┌──────────┐                           │
  │   │  Click   │                           │
  │   └──────────┘                           │
  │        │                                 │
  │   K gesture?                             │
  │   ┌──────────┐                           │
  │   │ Virtual  │                           │
  │   │ Keyboard │                           │
  │   └──────────┘                           │
  └──────────────────┬───────────────────────┘
                     │
                     ▼
             ┌──────────────┐
             │  PyAutoGUI   │  ← Sends system-level
             │  / pynput    │    mouse & keyboard events
             └──────────────┘
```

---

## 🤚 Hand Landmark Map

```
                    8   12  16  20
                    |   |   |   |
                    7   11  15  19
              4     |   |   |   |
              |     6   10  14  18
              3     |   |   |   |
              |     5   9   13  17
              2      \  |  /  /
               \      \ | / /
                1-------0
                      WRIST
```

> MediaPipe tracks **21 landmarks** per hand. Key points used:
> - `4` = Thumb tip → pinch detection
> - `8` = Index tip → cursor anchor + click
> - `12` = Middle tip → scroll anchor
> - `0` = Wrist → hand orientation

---

## 🕹️ Gesture Controls

```
┌─────────────────────────────────────────────────────────┐
│                   GESTURE CHEAT SHEET                   │
├──────────────────┬──────────────────┬───────────────────┤
│   GESTURE        │   HAND           │   ACTION          │
├──────────────────┼──────────────────┼───────────────────┤
│ ☝️  Index up     │ Right            │ Move cursor       │
│ 🤏 Pinch        │ Right            │ Left click        │
│ ✌️  Two fingers  │ Right            │ Right click       │
│ ☝️  Index up     │ Left             │ Scroll up         │
│ 👇 Index down   │ Left             │ Scroll down       │
│ 🤙 K gesture    │ Either           │ Toggle keyboard   │
└──────────────────┴──────────────────┴───────────────────┘
```

---

## 🗂️ Project Structure

```
air-mouse-/
│
├── 📄 airmouse2.0.py       ← Core air mouse engine (v2, main logic)
├── 📄 main.py              ← Entry point / launcher
├── 📄 keyboard.py          ← Virtual on-screen keyboard module
├── 📄 version2.py          ← Experimental alternate build
│
├── 🧪 testcase44.py        ← Test scripts
├── 🧪 testfile.py          ← Test scripts
│
├── 🎮 game.py              ← Gesture-controlled game demo
├── 🧙 harrypotter.py       ← Fun gesture demo (magic wand mode)
│
├── 💰 finanace.py          ← Side script: finance tracker
├── 📝 budget.txt           ← Budget notes
│
├── 📁 build/keyboard/      ← PyInstaller build artifacts
├── 📁 dist/keyboard/       ← PyInstaller distribution output
├── 📁 .idea/               ← IDE config (PyCharm)
└── 📁 __pycache__/         ← Python bytecode cache
```

---

## 🛠️ Tech Stack

```
┌────────────────┬────────────────────────────────────────────────┐
│  Library       │  Role                                          │
├────────────────┼────────────────────────────────────────────────┤
│  OpenCV        │  Webcam capture, frame display, image ops      │
│  MediaPipe     │  21-point hand landmark detection & tracking   │
│  PyAutoGUI     │  System mouse movement, clicks, keyboard input │
│  pynput        │  Low-level keyboard & mouse event injection    │
│  NumPy         │  Coordinate math & interpolation               │
│  Tkinter       │  Virtual keyboard overlay UI                   │
└────────────────┴────────────────────────────────────────────────┘
```

---

## 🚀 Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/Shivmahlan/air-mouse-.git
cd air-mouse-
```

### 2. Install dependencies

```bash
pip install opencv-python mediapipe pyautogui pynput numpy
```

> ⚠️ **macOS users:** PyAutoGUI requires accessibility permissions.
> Go to `System Preferences → Privacy & Security → Accessibility` and add your terminal.

### 3. Run

```bash
python main.py
```

Or run the core module directly:

```bash
python airmouse2.0.py
```

---

## ⚙️ Requirements

| Requirement | Minimum |
|---|---|
| Python | 3.8+ |
| Webcam | 720p (1080p recommended) |
| Display | 1080p 14" or higher |
| RAM | 4GB+ |
| OS | Windows 10+ / macOS 11+ / Ubuntu 20.04+ |

---

## 🔧 Configuration

Key parameters you can tune inside `airmouse2.0.py`:

```python
# Sensitivity — how much hand movement maps to cursor movement
SENSITIVITY = 3.0

# Smoothing — reduces jitter (higher = smoother but slower)
SMOOTH_FACTOR = 5

# Pinch threshold — distance between thumb & index to register a click
CLICK_THRESHOLD = 30

# Webcam index — change if you have multiple cameras
CAM_INDEX = 0

# Screen resolution
SCREEN_W, SCREEN_H = 1920, 1080
```

---

## 🗺️ Roadmap

- [x] Right hand cursor control
- [x] Pinch-to-click
- [x] Left hand scrolling
- [x] Virtual keyboard overlay
- [ ] Right-click gesture
- [ ] Drag & drop support
- [ ] Multi-hand combined gestures
- [ ] Sign language recognition module
- [ ] Voice + gesture fusion (Jarvis integration)
- [ ] Accessibility mode (reduced motion sensitivity)

---

## 🤝 Contributing

Pull requests are welcome! For major changes, open an issue first to discuss what you'd like to change.

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -m 'Add your feature'`
4. Push: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 👨‍💻 Author

**Shiv Mahlan**
B.Tech CSE (Data Science) · Ch. Devi Lal University 

[![GitHub](https://img.shields.io/badge/GitHub-Shivmahlan-181717?style=flat-square&logo=github)](https://github.com/Shivmahlan)

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgements

- [MediaPipe](https://developers.google.com/mediapipe) by Google — hand landmark detection
- [OpenCV](https://opencv.org/) — computer vision backbone
- [PyAutoGUI](https://pyautogui.readthedocs.io/) — system-level input control

---

<div align="center">

*Built with 👐 and no mouse*

⭐ Star this repo if you found it useful!

</div>
