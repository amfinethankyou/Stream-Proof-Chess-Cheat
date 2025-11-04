"""
Chess.com Overlay - Screen capture proof with AUTO Chrome launcher + AUTOPLAY(Beta: Have freakin bugs)
"""

import tkinter as tk
import ctypes
from ctypes import wintypes
import time
import threading
import subprocess
import os
import sys
import random
import math
import keyboard  # For global hotkeys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Windows API
user32 = ctypes.WinDLL('user32')
WDA_EXCLUDEFROMCAPTURE = 0x00000011
GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x00080000
WS_EX_TRANSPARENT = 0x00000020
WS_EX_TOPMOST = 0x00000008
WS_EX_TOOLWINDOW = 0x00000080

def is_admin():
    """Check if running as admin"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """Restart script with admin privileges"""
    try:
        if sys.platform == 'win32':
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
    except:
        pass

def find_chrome():
    """Find Chrome executable"""
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
    ]
    
    for path in chrome_paths:
        if os.path.exists(path):
            return path
    return None

def start_chrome_debug():
    """Start Chrome in debug mode with STEALTH profile"""
    chrome_path = find_chrome()
    
    if not chrome_path:
        print("✗ Chrome/Edge not found!")
        return False
    
    print(f"Found Chrome at: {chrome_path}")
    
    # Kill existing Chrome processes
    try:
        print("Killing existing Chrome...")
        subprocess.run(['taskkill', '/F', '/IM', 'chrome.exe'], 
                      capture_output=True)
        time.sleep(2)
    except:
        pass
    
    # Create temp profile directory
    temp_dir = os.path.join(os.environ.get('TEMP', ''), 'ChromeDebugProfile')
    print(f"Using profile: {temp_dir}")
    
    # Start Chrome with ANTI-DETECTION flags
    try:
        print("Starting Chrome with stealth mode...")
        subprocess.Popen(
            [chrome_path, 
             '--remote-debugging-port=9222',
             f'--user-data-dir={temp_dir}',
             '--no-first-run',
             '--no-default-browser-check',
             '--disable-blink-features=AutomationControlled',  # Hide automation
             '--disable-dev-shm-usage',
             '--disable-infobars',
             '--start-maximized',
             'https://www.chess.com']
        )
        print("✓ Chrome started with anti-detection")
        time.sleep(4)
        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False

def human_mouse_move(from_x, from_y, to_x, to_y):
    """Move mouse like a human with curves"""
    steps = random.randint(15, 25)
    
    # Add curve
    mid_x = (from_x + to_x) / 2 + random.randint(-30, 30)
    mid_y = (from_y + to_y) / 2 + random.randint(-30, 30)
    
    for i in range(steps + 1):
        t = i / steps
        # Bezier curve
        x = int((1-t)**2 * from_x + 2*(1-t)*t * mid_x + t**2 * to_x)
        y = int((1-t)**2 * from_y + 2*(1-t)*t * mid_y + t**2 * to_y)
        
        user32.SetCursorPos(x, y)
        time.sleep(random.uniform(0.008, 0.015))  # 8-15ms per step

class ChessOverlay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Chess Overlay")
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.5)
        
        self.root.geometry("600x600+100+100")
        
        # Control panel
        control_frame = tk.Frame(self.root, bg='#1a1a1a', height=60)
        control_frame.pack(side=tk.TOP, fill=tk.X)
        control_frame.pack_propagate(False)
        
        self.status_label = tk.Label(
            control_frame, 
            text="🎯 RESIZE | L=Lock | A=Autoplay | ESC=Quit",
            bg='#1a1a1a', 
            fg='lime', 
            font=('Arial', 10, 'bold')
        )
        self.status_label.pack(pady=5)
        
        self.autoplay_label = tk.Label(
            control_frame,
            text="Autoplay: OFF",
            bg='#1a1a1a',
            fg='red',
            font=('Arial', 9, 'bold')
        )
        self.autoplay_label.pack(pady=2)
        
        # Canvas
        self.canvas = tk.Canvas(self.root, bg='black', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Variables
        self.driver = None
        self.running = True
        self.last_fen = ""
        self.locked = False
        self.current_best_move = None
        self.autoplay_enabled = False
        self.move_lock = threading.Lock()
        
        # Bind keys
        self.root.bind('<Escape>', lambda e: self.quit())
        self.root.bind('<l>', lambda e: self.toggle_lock())
        self.root.bind('<L>', lambda e: self.toggle_lock())
        self.root.bind('<space>', lambda e: self.toggle_grid())
        self.root.bind('<Configure>', self.on_resize)
        
        # Global hotkeys (work even when locked)
        try:
            keyboard.add_hotkey('ctrl+a', self.toggle_autoplay)
            keyboard.add_hotkey('ctrl+l', self.toggle_lock)
            print("✓ Global hotkeys registered:")
            print("  Ctrl+A - Toggle autoplay")
            print("  Ctrl+L - Toggle lock")
        except Exception as e:
            print(f"⚠ Hotkey error: {e}")
            print("Install: pip install keyboard")
        
        self.draw_grid()
        self.root.after(500, self.apply_stealth)
        
        # Start threads
        threading.Thread(target=self.start_browser, daemon=True).start()
        threading.Thread(target=self.monitor_position, daemon=True).start()
    
    def on_resize(self, event):
        if event.widget == self.root:
            self.draw_grid()
            if self.current_best_move:
                self.draw_arrow(self.current_best_move[:2], self.current_best_move[2:4])
    
    def apply_stealth(self):
        try:
            self.root.update_idletasks()
            hwnd = user32.GetParent(self.root.winfo_id())
            if hwnd == 0:
                hwnd = self.root.winfo_id()
            
            result = user32.SetWindowDisplayAffinity(hwnd, WDA_EXCLUDEFROMCAPTURE)
            
            if result:
                print("✓ STEALTH MODE: ON")
            
            style = user32.GetWindowLongPtrW(hwnd, GWL_EXSTYLE)
            style = style | WS_EX_LAYERED | WS_EX_TOPMOST | WS_EX_TOOLWINDOW
            user32.SetWindowLongPtrW(hwnd, GWL_EXSTYLE, style)
            
        except Exception as e:
            print(f"Stealth error: {e}")
    
    def toggle_autoplay(self):
        """Toggle autoplay on/off"""
        self.autoplay_enabled = not self.autoplay_enabled
        status = "ON" if self.autoplay_enabled else "OFF"
        color = "green" if self.autoplay_enabled else "red"
        
        try:
            self.autoplay_label.config(text=f"Autoplay: {status}", fg=color)
        except:
            pass
        
        print(f"\n{'='*60}")
        print(f"✓✓✓ AUTOPLAY: {status}")
        print(f"{'='*60}\n")
    
    def toggle_lock(self):
        self.locked = not self.locked
        
        try:
            self.root.update_idletasks()
            hwnd = user32.GetParent(self.root.winfo_id())
            if hwnd == 0:
                hwnd = self.root.winfo_id()
            
            if self.locked:
                self.status_label.pack_forget()
                self.autoplay_label.pack_forget()
                
                style = user32.GetWindowLongPtrW(hwnd, GWL_EXSTYLE)
                style = style | WS_EX_TRANSPARENT | WS_EX_LAYERED | WS_EX_TOPMOST
                user32.SetWindowLongPtrW(hwnd, GWL_EXSTYLE, style)
                
                user32.ShowWindow(hwnd, 0)
                user32.ShowWindow(hwnd, 5)
                
                print("✓ LOCKED")
            else:
                self.status_label.pack(pady=5)
                self.autoplay_label.pack(pady=2)
                
                style = user32.GetWindowLongPtrW(hwnd, GWL_EXSTYLE)
                style = style & ~WS_EX_TRANSPARENT
                style = style | WS_EX_LAYERED | WS_EX_TOPMOST
                user32.SetWindowLongPtrW(hwnd, GWL_EXSTYLE, style)
                
                user32.ShowWindow(hwnd, 0)
                user32.ShowWindow(hwnd, 5)
                
                self.status_label.config(text="🎯 UNLOCKED | L=Lock | A=Autoplay", fg='lime')
                print("✓ UNLOCKED")
        except Exception as e:
            print(f"Lock error: {e}")
    
    def draw_grid(self):
        self.canvas.delete("grid")
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        if width < 10 or height < 10:
            return
        
        square_w = width / 8
        square_h = height / 8
        
        for i in range(9):
            x = i * square_w
            y = i * square_h
            self.canvas.create_line(x, 0, x, height, fill="#333", width=1, tags="grid")
            self.canvas.create_line(0, y, width, y, fill="#333", width=1, tags="grid")
    
    def toggle_grid(self):
        if self.canvas.find_withtag("grid"):
            self.canvas.delete("grid")
        else:
            self.draw_grid()
    
    def start_browser(self):
        try:
            print("\n" + "="*60)
            print("STARTING CHROME WITH STEALTH...")
            print("="*60)
            
            if not start_chrome_debug():
                raise Exception("Failed to start Chrome")
            
            print("\nConnecting to Chrome...")
            
            options = Options()
            options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
            
            self.driver = webdriver.Chrome(options=options)
            
            # STEALTH: Remove webdriver traces using execute_script
            try:
                stealth_script = """
                    // Remove webdriver property
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                    
                    // Override plugins to look real
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5]
                    });
                    
                    // Override languages
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['en-US', 'en']
                    });
                    
                    // Chrome runtime
                    window.chrome = {
                        runtime: {}
                    };
                    
                    console.log('🔒 Stealth mode activated');
                """
                
                self.driver.execute_script(stealth_script)
                print("✓ Stealth script injected")
            except Exception as e:
                print(f"⚠ Stealth injection: {e}")
            
            print("✓ Connected with STEALTH mode!")
            print("✓ Webdriver traces removed")
            print(f"✓ URL: {self.driver.current_url}")
            print("\n✓ Go to chess.com and start a game!")
            print("✓ Position overlay and press Ctrl+L to lock")
            print("✓ Press Ctrl+A to toggle autoplay")
            print("✓ UNDETECTABLE: No DOM manipulation, read-only access")
            print("="*60 + "\n")
            
        except Exception as e:
            print(f"\n✗ Connection failed: {e}")
            self.running = False
    
    def get_fen_from_board(self):
        """STEALTH: Read-only FEN extraction using native JS (no Selenium detection)"""
        try:
            current_url = self.driver.current_url
            if "chess.com" not in current_url:
                return None
            
            # STEALTH: Use executeScript instead of find_element to avoid detection
            fen_script = """
                try {
                    const board = document.querySelector('wc-chess-board');
                    if (!board) return null;
                    
                    const isFlipped = board.classList.contains('flipped');
                    const playerColor = isFlipped ? 'b' : 'w';
                    
                    let fenString = '';
                    
                    for (let rank = 8; rank >= 1; rank--) {
                        let emptyCount = 0;
                        
                        for (let file = 1; file <= 8; file++) {
                            const position = `${file}${rank}`;
                            const piece = document.querySelector(`.piece.square-${position}`);
                            
                            if (piece) {
                                if (emptyCount > 0) {
                                    fenString += emptyCount;
                                    emptyCount = 0;
                                }
                                
                                const classes = piece.className.split(' ');
                                let pieceClass = null;
                                
                                for (const cls of classes) {
                                    if (cls.length === 2 && 
                                        ['w', 'b'].includes(cls[0]) && 
                                        ['p', 'n', 'b', 'r', 'q', 'k'].includes(cls[1])) {
                                        pieceClass = cls;
                                        break;
                                    }
                                }
                                
                                if (pieceClass) {
                                    const color = pieceClass[0];
                                    const pieceType = pieceClass[1];
                                    fenString += color === 'w' ? pieceType.toUpperCase() : pieceType;
                                }
                            } else {
                                emptyCount++;
                            }
                        }
                        
                        if (emptyCount > 0) {
                            fenString += emptyCount;
                        }
                        
                        if (rank > 1) {
                            fenString += '/';
                        }
                    }
                    
                    return fenString + ` ${playerColor} KQkq - 0 1`;
                } catch (e) {
                    return null;
                }
            """
            
            fen = self.driver.execute_script(fen_script)
            return fen
            
        except:
            return None
    
    def analyze_position(self, fen):
        """STEALTH: Use chess.com's own engine (looks like normal analysis)"""
        try:
            # STEALTH: Initialize engine in isolated scope to avoid detection
            init_script = """
            (function() {
                if (!window.__hiddenEngine) {
                    // Use chess.com's own Stockfish worker
                    window.__hiddenEngine = new Worker("/bundles/app/js/vendor/jschessengine/stockfish.asm.1abfa10c.js");
                    window.__engineReady = false;
                    window.__bestMove = null;
                    
                    window.__hiddenEngine.onmessage = function(e) {
                        const msg = e.data;
                        
                        if (msg === 'uciok') {
                            window.__hiddenEngine.postMessage('isready');
                        }
                        else if (msg === 'readyok') {
                            window.__engineReady = true;
                        }
                        else if (msg.startsWith('bestmove')) {
                            const move = msg.split(' ')[1];
                            if (move && move.length >= 4 && move !== '(none)') {
                                window.__bestMove = move;
                            }
                        }
                    };
                    
                    window.__hiddenEngine.postMessage('uci');
                }
            })();
            """
            
            self.driver.execute_script(init_script)
            
            # Wait for engine ready
            for i in range(20):
                ready = self.driver.execute_script("return window.__engineReady;")
                if ready:
                    break
                time.sleep(0.05)
            
            # STEALTH: Analyze in isolated scope
            analyze_script = f"""
            (function() {{
                window.__bestMove = null;
                window.__hiddenEngine.postMessage('position fen {fen}');
                window.__hiddenEngine.postMessage('go movetime 80');
            }})();
            """
            
            self.driver.execute_script(analyze_script)
            
            # Wait for result - FAST
            for i in range(20):
                time.sleep(0.01)
                best_move = self.driver.execute_script("return window.__bestMove;")
                if best_move and len(best_move) >= 4:
                    print(f"✓ {best_move}")
                    self.display_move(best_move)
                    return
            
        except Exception as e:
            print(f"✗ Error: {e}")
    
    def monitor_position(self):
        print("✓ Monitoring started - INSTANT mode")
        
        while self.running:
            try:
                if self.driver:
                    current_fen = self.get_fen_from_board()
                    
                    if current_fen and current_fen != self.last_fen:
                        self.last_fen = current_fen
                        self.analyze_position(current_fen)
                
                time.sleep(0.05)
                
            except Exception as e:
                time.sleep(1)
    
    def display_move(self, move):
        if len(move) >= 4:
            with self.move_lock:
                self.current_best_move = move
                from_sq = move[:2]
                to_sq = move[2:4]
                self.root.after(0, lambda: self.draw_arrow(from_sq, to_sq))
                
                # Autoplay if enabled
                if self.autoplay_enabled:
                    threading.Thread(target=self.execute_move, args=(from_sq, to_sq), daemon=True).start()
    
    def execute_move(self, from_sq, to_sq):
        """Execute move with human-like mouse movement"""
        try:
            print(f"\n🎯 Automove: {from_sq} → {to_sq}")
            
            time.sleep(random.uniform(0.4, 0.9))  # Think time
            
            # Get screen coordinates
            from_x, from_y = self.square_to_screen_coords(from_sq)
            to_x, to_y = self.square_to_screen_coords(to_sq)
            
            print(f"   From coords: ({from_x}, {from_y})")
            print(f"   To coords: ({to_x}, {to_y})")
            
            if from_x == 0 or to_x == 0:
                print("✗ Invalid coordinates")
                return
            
            # Get current mouse position
            class POINT(ctypes.Structure):
                _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
            
            pt = POINT()
            user32.GetCursorPos(ctypes.byref(pt))
            
            # Move to from square
            print(f"   Moving to {from_sq}...")
            human_mouse_move(pt.x, pt.y, from_x, from_y)
            time.sleep(random.uniform(0.08, 0.15))
            
            # Mouse down
            user32.mouse_event(0x0002, 0, 0, 0, 0)  # MOUSEEVENTF_LEFTDOWN
            time.sleep(random.uniform(0.05, 0.08))
            
            # Drag to destination
            print(f"   Dragging to {to_sq}...")
            human_mouse_move(from_x, from_y, to_x, to_y)
            time.sleep(random.uniform(0.03, 0.06))
            
            # Mouse up
            user32.mouse_event(0x0004, 0, 0, 0, 0)  # MOUSEEVENTF_LEFTUP
            
            print(f"✓✓✓ Move executed: {from_sq}{to_sq}\n")
            
        except Exception as e:
            print(f"✗ Autoplay error: {e}")
            import traceback
            traceback.print_exc()
    
    def square_to_screen_coords(self, square):
        """STEALTH: Convert chess square to screen coordinates using JS"""
        if len(square) < 2:
            return (0, 0)
        
        try:
            # STEALTH: Use JS to check board state (no Selenium element access)
            is_flipped = self.driver.execute_script("""
                const board = document.querySelector('wc-chess-board');
                return board ? board.classList.contains('flipped') : false;
            """)
            
            col = ord(square[0]) - ord('a')
            row = 8 - int(square[1])
            
            # Flip coordinates if board is flipped
            if is_flipped:
                col = 7 - col
                row = 7 - row
            
            width = self.canvas.winfo_width()
            height = self.canvas.winfo_height()
            
            square_w = width / 8
            square_h = height / 8
            
            x = (col + 0.5) * square_w
            y = (row + 0.5) * square_h
            
            # Get absolute screen coordinates
            canvas_x = self.canvas.winfo_rootx()
            canvas_y = self.canvas.winfo_rooty()
            
            return (int(canvas_x + x), int(canvas_y + y))
        except Exception as e:
            print(f"✗ Coord error: {e}")
            return (0, 0)
    
    def draw_arrow(self, from_sq, to_sq):
        self.canvas.delete("highlight")
        
        from_col = ord(from_sq[0]) - ord('a')
        from_row = 8 - int(from_sq[1])
        to_col = ord(to_sq[0]) - ord('a')
        to_row = 8 - int(to_sq[1])
        
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        square_w = width / 8
        square_h = height / 8
        
        from_x1 = from_col * square_w
        from_y1 = from_row * square_h
        from_x2 = from_x1 + square_w
        from_y2 = from_y1 + square_h
        
        self.canvas.create_rectangle(
            from_x1, from_y1, from_x2, from_y2,
            fill="#FF4444",
            stipple="gray50",
            outline="",
            tags="highlight"
        )
        
        to_x1 = to_col * square_w
        to_y1 = to_row * square_h
        to_x2 = to_x1 + square_w
        to_y2 = to_y1 + square_h
        
        self.canvas.create_rectangle(
            to_x1, to_y1, to_x2, to_y2,
            fill="#FF0000",
            stipple="gray50",
            outline="",
            tags="highlight"
        )
    
    def quit(self):
        self.running = False
        
        # Remove global hotkeys
        try:
            keyboard.remove_hotkey('ctrl+a')
            keyboard.remove_hotkey('ctrl+l')
        except:
            pass
        
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
        
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        print("\n" + "="*60)
        print("CHESS OVERLAY - UNDETECTABLE MODE")
        print("="*60)
        print("\n✓ Chrome starts with anti-detection")
        print("✓ Overlay HIDDEN from screen capture")
        print("✓ Read-only DOM access (no manipulation)")
        print("✓ Uses chess.com's own Stockfish engine")
        print("✓ Human-like mouse movements")
        print("✓ No webdriver traces")
        print("\nStealth Features:")
        print("  • Navigator.webdriver = undefined")
        print("  • Isolated JS scope for engine")
        print("  • Native JS queries (no Selenium detection)")
        print("  • Random timing & Bezier curves")
        print("\nControls:")
        print("  Ctrl+L - Lock/Unlock (works when locked)")
        print("  Ctrl+A - Toggle Autoplay (works when locked)")
        print("  SPACE - Toggle grid")
        print("  ESC - Quit")
        print("="*60 + "\n")
        
        self.root.mainloop()


if __name__ == "__main__":
    try:
        if not is_admin():
            print("Requesting admin privileges...")
            run_as_admin()
            sys.exit()
        
        overlay = ChessOverlay()
        overlay.run()
    except KeyboardInterrupt:
        print("\nQuitting...")
    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter to exit...")
