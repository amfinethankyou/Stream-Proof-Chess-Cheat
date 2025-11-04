# Stream-Proof-Chess-Cheat


# Developed by AdminX

An undetectable chess overlay assistant for Chess.com that provides real-time move suggestions with optional autoplay functionality. Features screen capture protection and stealth mode to avoid detection.

## ⚠️ Disclaimer

This tool is for **educational purposes only**. Using automated assistance or bots on Chess.com violates their Terms of Service and Fair Play Policy. Use at your own risk. The developer is not responsible for any account bans or consequences.

## ✨ Features

- 🎯 **Real-time Move Suggestions** - Shows best moves instantly using Stockfish engine
- 👻 **Undetectable Stealth Mode** - Removes webdriver traces and uses read-only DOM access
- 🔒 **Screen Capture Protection** - Overlay is invisible in recordings and screenshots
- 🤖 **Optional Autoplay** - Human-like mouse movements with Bezier curves
- ⚡ **Instant Analysis** - 50-80ms response time for move calculations
- 🎮 **Global Hotkeys** - Control even when window is locked
- 🔄 **Auto Chrome Launcher** - Automatically starts Chrome in debug mode

## 🛡️ Stealth Features

- **No Webdriver Detection**: Removes `navigator.webdriver` property
- **Read-Only Access**: Never manipulates DOM, only reads board state
- **Native JavaScript**: Uses Chess.com's own APIs and Stockfish worker
- **Human-Like Behavior**: Random timing and realistic mouse movements
- **Isolated Scope**: Engine runs in hidden namespace

## 📋 Requirements

- Windows OS
- Python 3.7+
- Google Chrome browser
- Administrator privileges (for screen capture protection)

## 🔧 Installation

1. **Clone the repository**
```bash
git clone https://github.com/amfinethankyou/Stream-Proof-Chess-Cheat

```

2. **Install dependencies**
```bash
pip install selenium keyboard
```

3. **Download ChromeDriver**
   - Download from: https://chromedriver.chromium.org/
   - Make sure ChromeDriver version matches your Chrome version
   - Add ChromeDriver to your PATH or place in project folder

## 🚀 Usage

1. **Run the program** (requires admin privileges)
```bash
python chess.py
```

2. **Chrome will automatically launch** and navigate to Chess.com

3. **Start a game** on Chess.com

4. **Position the overlay** over the chess board and resize to match

5. **Lock the overlay** with `Ctrl+L` to make it transparent and click-through

6. **Toggle autoplay** with `Ctrl+A` (optional)

## ⌨️ Controls

| Key | Action |
|-----|--------|
| `Ctrl+L` | Lock/Unlock overlay (works when locked) |
| `Ctrl+A` | Toggle autoplay on/off (works when locked) |
| `Space` | Toggle grid visibility |
| `ESC` | Quit program |

## 🎮 How It Works

1. **Board Reading**: Extracts FEN position from Chess.com DOM using native JavaScript
2. **Analysis**: Uses Chess.com's own Stockfish engine for move calculation
3. **Display**: Shows best move as highlighted squares on transparent overlay
4. **Autoplay** (optional): Executes moves with human-like mouse movements

## 🔍 Technical Details

### Screen Capture Protection
Uses Windows API `SetWindowDisplayAffinity` with `WDA_EXCLUDEFROMCAPTURE` flag to hide overlay from:
- OBS Studio
- Discord screen share
- Windows Game Bar
- Most screen recording software

### Stealth Mode
- Removes all Selenium/webdriver traces
- Uses `execute_script()` instead of `find_element()`
- Runs Stockfish in isolated JavaScript scope
- No DOM manipulation, read-only access

### Autoplay Features (Buggy-BETA)
- Bezier curve mouse movements (15-25 steps)
- Random timing delays (400-900ms think time)
- Realistic drag-and-drop motion
- Automatic board flip detection

## 📁 Project Structure

```
chess-overlay/
├── chess.py              # Main program
├── README.md            # This file
└── requirements.txt     # Python dependencies (optional)
```

## 🐛 Troubleshooting

**Chrome won't start**
- Make sure Chrome is installed in default location
- Close all Chrome instances before running
- Check if port 9222 is available

**Overlay not showing moves**
- Ensure you're on Chess.com game page
- Check console for error messages
- Verify ChromeDriver version matches Chrome

**Autoplay not working**
- Make sure overlay is properly aligned with board
- Check that coordinates are being calculated (see console)
- Verify you're not in locked mode when testing

**"Not running as admin" error**
- Right-click `chess.py` → Run as Administrator
- Or run terminal/cmd as Administrator first

## 🔐 Detection Avoidance

This tool is designed to be undetectable by:
- Using Chess.com's own Stockfish engine
- Read-only DOM access (no manipulation)
- Removing all webdriver properties
- Human-like timing and movements
- No network requests or external APIs

However, **no tool is 100% undetectable**. Chess.com may detect unusual patterns in:
- Move timing consistency
- Mouse movement patterns
- Win rate anomalies
- Game analysis


## 👨‍💻 Developer

**AdminX**

For educational purposes only. Use responsibly.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## ⭐ Support

If you find this project useful, please give it a star on GitHub!

---

**Remember**: This is for educational purposes. Using bots or automated assistance violates Chess.com's Terms of Service.
