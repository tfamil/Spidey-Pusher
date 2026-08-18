"""
spidey_pusher.py

A borderless, always-on-top, TRANSPARENT desktop overlay that reminds you
to push your code to GitHub. There is no background panel — only
Spider-Man and the reminder text are visible, so it looks like he is
hanging right on top of your desktop. He descends from the very top edge
of your screen on a web line, then a "spider net" text panel unfurls
below him asking "DID YOU PUSH YOUR CODES IN YOUR GITHUB REPO?", followed
by YES / NO buttons.

Place this script in the same folder as `image_0.png` (a transparent PNG
of Spider-Man hanging upside down).

Requirements: Pillow (see requirements.txt)

NOTE: The transparent-background effect uses Tkinter's Windows-only
`-transparentcolor` window attribute, so this script is built to run on
Windows.
"""

import os
import sys
import math
import platform
import tkinter as tk
from tkinter import font as tkfont

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------
IMAGE_FILENAME = "image_0.png"
SPIDEY_MAX_WIDTH = 260          # max display width for the Spider-Man image
DESCEND_DURATION_MS = 3000      # ~3 seconds to descend
DESCEND_FPS = 60                # animation smoothness
SNOOZE_MS = 5 * 60 * 1000       # 5 minutes
DIALOGUE_LINES = [
    "DID YOU PUSH YOUR CODES",
    "IN YOUR GITHUB REPO?",
]

WINDOW_WIDTH = 640
WINDOW_MAX_HEIGHT = 900

# The "magic" color that becomes see-through on Windows. Kept far away
# from every other color used on the canvas so nothing is accidentally
# punched full of holes.
TRANSPARENT_KEY = "#ff00fe"

TEXT_COLOR = "#c60000"          # bold spidey-red for the dialogue text
TEXT_OUTLINE = "#050505"        # dark outline so text reads over any wallpaper
WEB_COLOR = "#e7e7e7"           # faint web-strand color
ACCENT_RED = "#c60000"
ACCENT_BLUE = "#1c3fa8"
BUTTON_TEXT = "#ffffff"
BUTTON_OUTLINE = "#050505"


class SpideyPusherApp:
    def __init__(self, root):
        self.root = root
        self.window_height = 0
        self._configure_window()

        self.canvas = tk.Canvas(
            self.root,
            width=WINDOW_WIDTH,
            height=self.window_height,
            highlightthickness=0,
            bg=TRANSPARENT_KEY,
        )
        self.canvas.pack(fill="both", expand=True)

        self._load_fonts()
        self._spidey_photo = None
        self._spidey_item = None
        self._web_line_item = None

        self._build_sequence()

    # ------------------------------------------------------------------
    # Window setup
    # ------------------------------------------------------------------
    def _configure_window(self):
        self.root.overrideredirect(1)
        self.root.attributes("-topmost", True)

        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        self.window_height = min(WINDOW_MAX_HEIGHT, screen_h - 10)
        x = (screen_w - WINDOW_WIDTH) // 2
        y = 0  # flush with the very top edge of the screen

        self.root.geometry(f"{WINDOW_WIDTH}x{self.window_height}+{x}+{y}")

        # Make the window background see-through (Windows only). Falls
        # back gracefully to an opaque window on other platforms.
        self._transparent_supported = False
        if platform.system() == "Windows":
            try:
                self.root.attributes("-transparentcolor", TRANSPARENT_KEY)
                self._transparent_supported = True
            except tk.TclError:
                self._transparent_supported = False

        if not self._transparent_supported:
            # Non-Windows fallback: keep it visible but neutral.
            print("[spidey_pusher] Transparent window not supported on this "
                  "OS; showing a plain background instead.")

        self.root.bind("<Escape>", lambda e: self._on_yes())

    def _load_fonts(self):
        candidates = ["Comic Sans MS", "Arial Black", "Impact", "Helvetica"]
        available = set(tkfont.families())
        chosen = next((f for f in candidates if f in available), "Helvetica")
        self.font_bubble = tkfont.Font(family=chosen, size=22, weight="bold")
        self.font_button = tkfont.Font(family=chosen, size=18, weight="bold")

    # ------------------------------------------------------------------
    # Main sequence: spidey descends -> web text -> buttons
    # ------------------------------------------------------------------
    def _build_sequence(self):
        self.canvas.delete("all")
        if not self._transparent_supported:
            self.canvas.create_rectangle(
                0, 0, WINDOW_WIDTH, self.window_height,
                fill="#111111", outline="",
            )
        self._load_spidey_image()
        self._animate_descend()

    def _load_spidey_image(self):
        image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), IMAGE_FILENAME)

        if not PIL_AVAILABLE:
            self._spidey_photo = None
            self._draw_spidey_placeholder(reason="Pillow is not installed")
            return

        try:
            img = Image.open(image_path)
            img = img.convert("RGBA")
            w, h = img.size
            if w > SPIDEY_MAX_WIDTH:
                scale = SPIDEY_MAX_WIDTH / float(w)
                img = img.resize((SPIDEY_MAX_WIDTH, int(h * scale)), Image.LANCZOS)
            self._spidey_photo = ImageTk.PhotoImage(img)
            self._spidey_h = img.height
            self._spidey_w = img.width
        except FileNotFoundError:
            self._spidey_photo = None
            self._draw_spidey_placeholder(
                reason=f"Could not find '{IMAGE_FILENAME}' next to this script"
            )
        except Exception as exc:  # noqa: BLE001 - surface any Pillow/IO error visibly
            self._spidey_photo = None
            self._draw_spidey_placeholder(reason=f"Could not load image ({exc})")

    def _draw_spidey_placeholder(self, reason):
        self._spidey_w, self._spidey_h = 160, 160
        print(f"[spidey_pusher] Warning: {reason}. Using placeholder graphic.")

    # ------------------------------------------------------------------
    # Animation: Spider-Man descends slowly from the top edge of the screen
    # ------------------------------------------------------------------
    def _animate_descend(self):
        final_y = 10
        start_y = -self._spidey_h
        total_frames = max(1, int(DESCEND_DURATION_MS / (1000 / DESCEND_FPS)))
        distance = final_y - start_y
        self._frame = 0

        center_x = WINDOW_WIDTH // 2

        self._web_line_item = self.canvas.create_line(
            center_x, 0, center_x, start_y, width=2, fill=WEB_COLOR
        )

        if self._spidey_photo is not None:
            self._spidey_item = self.canvas.create_image(
                center_x, start_y, image=self._spidey_photo, anchor="n"
            )
        else:
            self._spidey_item = self.canvas.create_oval(
                center_x - 60, start_y, center_x + 60, start_y + self._spidey_h,
                fill=ACCENT_RED, outline=BUTTON_OUTLINE, width=3,
            )
            self._spidey_label = self.canvas.create_text(
                center_x, start_y + self._spidey_h // 2,
                text="SPIDEY", fill="white", font=self.font_button,
            )

        def ease_out_cubic(t):
            return 1 - (1 - t) ** 3

        def step():
            self._frame += 1
            t = min(self._frame / total_frames, 1.0)
            eased = ease_out_cubic(t)
            current_y = start_y + distance * eased

            self.canvas.coords(self._web_line_item, center_x, 0, center_x, current_y)
            if self._spidey_photo is not None:
                self.canvas.coords(self._spidey_item, center_x, current_y)
            else:
                self.canvas.coords(
                    self._spidey_item,
                    center_x - 60, current_y, center_x + 60, current_y + self._spidey_h,
                )
                self.canvas.coords(
                    self._spidey_label, center_x, current_y + self._spidey_h // 2
                )

            if t < 1.0:
                self.root.after(int(1000 / DESCEND_FPS), step)
            else:
                self._show_web_text(final_y + self._spidey_h + 20)

        step()

    # ------------------------------------------------------------------
    # Spider-web text panel (no filled background — just web strands)
    # ------------------------------------------------------------------
    def _draw_spiderweb(self, cx, cy, radius, spokes=10, rings=4):
        # Radial spokes
        for i in range(spokes):
            angle = (2 * math.pi / spokes) * i
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle) * 0.55  # squash vertically to fit panel
            self.canvas.create_line(cx, cy, x, y, fill=WEB_COLOR, width=1)

        # Concentric web rings connecting the spokes
        for r_step in range(1, rings + 1):
            r = radius * (r_step / rings)
            points = []
            for i in range(spokes):
                angle = (2 * math.pi / spokes) * i
                x = cx + r * math.cos(angle)
                y = cy + r * math.sin(angle) * 0.55
                points.append((x, y))
            for i in range(spokes):
                x0, y0 = points[i]
                x1, y1 = points[(i + 1) % spokes]
                self.canvas.create_line(x0, y0, x1, y1, fill=WEB_COLOR, width=1)

    def _draw_outlined_text(self, x, y, text, font, fill, outline, width=0, justify="center"):
        offsets = [(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)]
        for dx, dy in offsets:
            self.canvas.create_text(
                x + dx, y + dy, text=text, font=font, fill=outline,
                width=width, justify=justify,
            )
        return self.canvas.create_text(
            x, y, text=text, font=font, fill=fill, width=width, justify=justify,
        )

    def _show_web_text(self, top_y):
        cx = WINDOW_WIDTH // 2
        panel_height = 190
        cy = top_y + panel_height // 2
        radius = WINDOW_WIDTH // 2 - 40

        self._draw_spiderweb(cx, cy, radius, spokes=12, rings=5)

        line_gap = 34
        start_y = cy - (len(DIALOGUE_LINES) - 1) * line_gap / 2
        for i, line in enumerate(DIALOGUE_LINES):
            self._draw_outlined_text(
                cx, start_y + i * line_gap, line,
                font=self.font_bubble, fill=TEXT_COLOR, outline=TEXT_OUTLINE,
                width=WINDOW_WIDTH - 60,
            )

        self._show_buttons(top_y + panel_height + 10)

    # ------------------------------------------------------------------
    # YES / NO buttons
    # ------------------------------------------------------------------
    def _show_buttons(self, top_y):
        btn_w, btn_h = 180, 70
        gap = 30
        total_w = btn_w * 2 + gap
        start_x = (WINDOW_WIDTH - total_w) // 2

        # Keep the buttons on-screen even if the window got clamped short.
        max_top = self.window_height - btn_h - 20
        top_y = min(top_y, max_top)

        yes_x0 = start_x
        yes_x1 = start_x + btn_w
        no_x0 = start_x + btn_w + gap
        no_x1 = no_x0 + btn_w

        yes_rect = self.canvas.create_rectangle(
            yes_x0, top_y, yes_x1, top_y + btn_h,
            fill=ACCENT_BLUE, outline=BUTTON_OUTLINE, width=4,
        )
        yes_text = self.canvas.create_text(
            (yes_x0 + yes_x1) // 2, top_y + btn_h // 2,
            text="YES", fill=BUTTON_TEXT, font=self.font_button,
        )
        no_rect = self.canvas.create_rectangle(
            no_x0, top_y, no_x1, top_y + btn_h,
            fill=ACCENT_RED, outline=BUTTON_OUTLINE, width=4,
        )
        no_text = self.canvas.create_text(
            (no_x0 + no_x1) // 2, top_y + btn_h // 2,
            text="NO", fill=BUTTON_TEXT, font=self.font_button,
        )

        for item in (yes_rect, yes_text):
            self.canvas.tag_bind(item, "<Button-1>", lambda e: self._on_yes())
            self.canvas.tag_bind(item, "<Enter>", lambda e: self.canvas.config(cursor="hand2"))
            self.canvas.tag_bind(item, "<Leave>", lambda e: self.canvas.config(cursor=""))

        for item in (no_rect, no_text):
            self.canvas.tag_bind(item, "<Button-1>", lambda e: self._on_no())
            self.canvas.tag_bind(item, "<Enter>", lambda e: self.canvas.config(cursor="hand2"))
            self.canvas.tag_bind(item, "<Leave>", lambda e: self.canvas.config(cursor=""))

    # ------------------------------------------------------------------
    # Button handlers
    # ------------------------------------------------------------------
    def _on_yes(self):
        self.root.destroy()
        sys.exit(0)

    def _on_no(self):
        self.root.wm_withdraw()
        self.root.after(SNOOZE_MS, self._reappear)

    def _reappear(self):
        self.root.deiconify()
        self.root.attributes("-topmost", True)
        self._build_sequence()


def main():
    root = tk.Tk()
    app = SpideyPusherApp(root)  # noqa: F841 - kept alive via closures/callbacks
    root.mainloop()


if __name__ == "__main__":
    main()
