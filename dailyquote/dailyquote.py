# -*- coding: utf-8 -*-
"""
DailyQuote - Cinematic Edition
==============================
CSC 303 practical project.

A premium, cinematic desktop quote application written with Python's
standard library only (Tkinter + ttk).  No internet, API keys or extra
packages are needed.

How the program is organised (top to bottom of this file):
    1. Colours, fonts and the list of quotes (the "data")
    2. Small helper functions (colour mixing, text spacing, dates ...)
    3. FavouritesStore   - reads and writes favourites.json
    4. DailyQuoteApp     - the main window: drawing, animation, buttons
    5. FavouritesWindow  - the second window that lists saved quotes
    6. main()            - starts the program

Run it with:   python dailyquote.py
"""

import json
import math
import os
import random
import sys
import time
import tkinter as tk
import tkinter.font as tkfont
from datetime import date
from tkinter import ttk


# ======================================================================
# 1. COLOURS, FONTS AND DATA
# ======================================================================

APP_TITLE = "DailyQuote \u2014 Cinematic Edition"
FAVOURITES_FILENAME = "favourites.json"

# The colour palette requested in the project brief.
BLACK = "#08090D"        # deep black
NAVY = "#101522"         # midnight navy
GOLD = "#D6B36A"         # muted gold
WARM_WHITE = "#F5F1E8"   # warm white
SOFT_GREY = "#A4A8B3"    # soft grey
ERROR_RED = "#D98C7A"    # soft red used only for error messages

# Fonts: we try each name in order and use the first one installed on the
# computer, so the program never crashes because of a missing font.
SERIF_CHOICES = ["Georgia", "Palatino Linotype", "Book Antiqua", "Cambria",
                 "Times New Roman", "DejaVu Serif", "Times"]
SANS_CHOICES = ["Segoe UI", "Calibri", "Helvetica", "Arial", "DejaVu Sans"]

# The quotes.  Each item is (quote text, author).
QUOTES = [
    ("The only way to do great work is to love what you do.", "Steve Jobs"),
    ("Stay hungry. Stay foolish.", "Steve Jobs"),
    ("Your time is limited, so don't waste it living someone else's life.", "Steve Jobs"),
    ("It always seems impossible until it's done.", "Nelson Mandela"),
    ("Education is the most powerful weapon which you can use to change the world.", "Nelson Mandela"),
    ("I learned that courage was not the absence of fear, but the triumph over it.", "Nelson Mandela"),
    ("The only thing we have to fear is fear itself.", "Franklin D. Roosevelt"),
    ("The only limit to our realization of tomorrow will be our doubts of today.", "Franklin D. Roosevelt"),
    ("You must do the thing you think you cannot do.", "Eleanor Roosevelt"),
    ("No one can make you feel inferior without your consent.", "Eleanor Roosevelt"),
    ("Do what you can, with what you have, where you are.", "Theodore Roosevelt"),
    ("Imagination is more important than knowledge.", "Albert Einstein"),
    ("I have no special talent. I am only passionately curious.", "Albert Einstein"),
    ("Strive not to be a success, but rather to be of value.", "Albert Einstein"),
    ("The important thing is not to stop questioning.", "Albert Einstein"),
    ("The unexamined life is not worth living.", "Socrates"),
    ("I think, therefore I am.", "Ren\u00e9 Descartes"),
    ("We are what we repeatedly do. Excellence, then, is not an act, but a habit.", "Will Durant"),
    ("The journey of a thousand miles begins with a single step.", "Lao Tzu"),
    ("Knowing others is intelligence; knowing yourself is true wisdom.", "Lao Tzu"),
    ("He who has a why to live can bear almost any how.", "Friedrich Nietzsche"),
    ("It does not matter how slowly you go as long as you do not stop.", "Confucius"),
    ("The best way to predict the future is to invent it.", "Alan Kay"),
    ("Programs must be written for people to read, and only incidentally for machines to execute.", "Harold Abelson"),
    ("Simplicity is prerequisite for reliability.", "Edsger W. Dijkstra"),
    ("Talk is cheap. Show me the code.", "Linus Torvalds"),
    ("Any sufficiently advanced technology is indistinguishable from magic.", "Arthur C. Clarke"),
    ("Genius is one percent inspiration and ninety-nine percent perspiration.", "Thomas Edison"),
    ("Courage is grace under pressure.", "Ernest Hemingway"),
    ("The best time to plant a tree was twenty years ago. The second best time is now.", "Chinese Proverb"),
    ("Fall seven times, stand up eight.", "Japanese Proverb"),
    ("If you want to go fast, go alone. If you want to go far, go together.", "African Proverb"),
    ("However long the night, the dawn will break.", "African Proverb"),
    ("Darkness cannot drive out darkness; only light can do that.", "Martin Luther King Jr."),
    ("Injustice anywhere is a threat to justice everywhere.", "Martin Luther King Jr."),
    ("Not everything that is faced can be changed, but nothing can be changed until it is faced.", "James Baldwin"),
    ("I am the master of my fate, I am the captain of my soul.", "William Ernest Henley"),
    ("Do the best you can until you know better. Then when you know better, do better.", "Maya Angelou"),
    ("You may encounter many defeats, but you must not be defeated.", "Maya Angelou"),
    ("Nothing great was ever achieved without enthusiasm.", "Ralph Waldo Emerson"),
    ("Every artist was first an amateur.", "Ralph Waldo Emerson"),
    ("You miss 100% of the shots you don't take.", "Wayne Gretzky"),
    ("Well done is better than well said.", "Benjamin Franklin"),
    ("The impediment to action advances action. What stands in the way becomes the way.", "Marcus Aurelius"),
    ("It is not that we have a short time to live, but that we waste a lot of it.", "Seneca"),
    ("We suffer more often in imagination than in reality.", "Seneca"),
    ("If I have seen further, it is by standing on the shoulders of giants.", "Isaac Newton"),
    ("Nothing in life is to be feared, it is only to be understood.", "Marie Curie"),
    ("The mind is not a vessel to be filled, but a fire to be kindled.", "Plutarch"),
    ("Happiness is not something ready made. It comes from your own actions.", "Dalai Lama"),
    ("Courage doesn't always roar. Sometimes courage is the quiet voice at the end of the day saying, I will try again tomorrow.", "Mary Anne Radmacher"),
    ("The single story creates stereotypes, and the problem with stereotypes is not that they are untrue, but that they are incomplete.", "Chimamanda Ngozi Adichie"),
    ("Do your little bit of good where you are; it's those little bits of good put together that overwhelm the world.", "Desmond Tutu"),
    ("If one advances confidently in the direction of his dreams, and endeavors to live the life which he has imagined, he will meet with a success unexpected in common hours.", "Henry David Thoreau"),
    ("Until the lion learns how to write, every story will glorify the hunter.", "African Proverb"),
    ("Nothing is permanent except change.", "Heraclitus"),
    ("Not all those who wander are lost.", "J. R. R. Tolkien"),
    ("Small deeds done are better than great deeds planned.", "Peter Marshall"),
    ("Be kind, for everyone you meet is fighting a hard battle.", "Ian Maclaren"),
    ("The best way out is always through.", "Robert Frost"),
]


# ======================================================================
# 2. SMALL HELPER FUNCTIONS
# ======================================================================

def hex_to_rgb(colour):
    """Turn '#D6B36A' into the numbers (214, 179, 106)."""
    colour = colour.lstrip("#")
    return int(colour[0:2], 16), int(colour[2:4], 16), int(colour[4:6], 16)


def mix(colour_a, colour_b, amount):
    """
    Blend two colours.  amount=0 gives colour_a, amount=1 gives colour_b.
    Tkinter cannot draw real transparency, so we fake it by blending a
    colour with the background colour behind it.  This is the trick that
    powers every fade, glow and hover effect in this program.
    """
    amount = max(0.0, min(1.0, amount))
    r1, g1, b1 = hex_to_rgb(colour_a)
    r2, g2, b2 = hex_to_rgb(colour_b)
    r = r1 + (r2 - r1) * amount
    g = g1 + (g2 - g1) * amount
    b = b1 + (b2 - b1) * amount
    return "#%02x%02x%02x" % (int(round(r)), int(round(g)), int(round(b)))


# Colours worked out from the palette above.
GOLD_DIM = mix(BLACK, GOLD, 0.40)       # thin frame lines
GOLD_FAINT = mix(BLACK, GOLD, 0.18)     # very faint lines
MARK_GOLD = mix(BLACK, GOLD, 0.55)      # big decorative quotation marks
BUTTON_BG = mix(BLACK, NAVY, 0.75)      # button / card background
CARD_BG = mix(BLACK, NAVY, 0.60)
GLOW_CENTRE = mix(BLACK, GOLD, 0.17)    # warm spotlight colour
TEXT_BG = mix(NAVY, GLOW_CENTRE, 0.5)   # roughly the colour behind the quote


def glow_colour(t, pulse):
    """
    Colour of one ring of the background spotlight.
    t     : 0 (outer edge, black) to 1 (centre, brightest)
    pulse : about 0.55 to 1.0, makes the glow slowly breathe
    """
    base = mix(BLACK, NAVY, min(1.0, t * 1.6))
    warm = max(0.0, (t - 0.45) / 0.55) ** 1.4 * pulse
    return mix(base, GLOW_CENTRE, warm)


def pick_font(choices, fallback):
    """Return the first font name from `choices` that is installed."""
    installed = set(tkfont.families())
    for name in choices:
        if name in installed:
            return name
    return fallback


def spaced(text, gap=1):
    """Add letter-spacing:  'AB CD'  ->  'A B   C D'  (cinematic title look)."""
    separator = " " * gap
    words = [separator.join(word) for word in text.split(" ")]
    return "   ".join(words)


def quote_index_for_date(day):
    """
    Pick the quote for a given date.  Using the day number means the same
    date always gives the same quote (consistent), and the quote changes
    every day, cycling through the whole list.
    """
    return day.toordinal() % len(QUOTES)


def pretty_date(iso_text):
    """'2026-10-25' -> '25 OCT 2026'.  Returns '' if the text is not a date."""
    try:
        return date.fromisoformat(iso_text).strftime("%d %b %Y").upper()
    except ValueError:
        return ""


def make_particles():
    """
    Create the floating stars and golden dust.  A fixed random seed means
    the sky looks the same every time the program starts.
    Positions are stored as fractions (0 to 1) so they scale with the window.
    """
    rng = random.Random(2026)
    particles = []
    for number in range(70):
        is_dust = (number % 5 == 0)
        particles.append({
            "kind": "dust" if is_dust else "star",
            "x": rng.random(),
            "y": rng.random(),
            "size": rng.uniform(1.6, 2.8) if is_dust else rng.uniform(0.8, 1.8),
            "speed": rng.uniform(0.012, 0.030) if is_dust else rng.uniform(0.004, 0.012),
            "drift": rng.uniform(-0.004, 0.004),
            "phase": rng.uniform(0, 6.28),
        })
    return particles


def particle_colour(particle, now):
    """Twinkling colour of one particle at time `now`."""
    twinkle = 0.35 + 0.65 * (0.5 + 0.5 * math.sin(now * 1.3 + particle["phase"]))
    if particle["kind"] == "dust":
        return mix(NAVY, GOLD, 0.65 * twinkle)
    return mix(NAVY, WARM_WHITE, 0.55 * twinkle)


def enable_sharp_text_on_windows():
    """Ask Windows not to blur the window on high-resolution screens."""
    if sys.platform != "win32":
        return
    try:
        import ctypes
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass  # Not important - the app still works without it.


def use_dark_title_bar(window):
    """On Windows 10/11, make the title bar dark to match the theme."""
    if sys.platform != "win32":
        return
    try:
        import ctypes
        window.update_idletasks()
        handle = ctypes.windll.user32.GetParent(window.winfo_id())
        value = ctypes.c_int(1)
        for attribute in (20, 19):  # 20 = Windows 11 / newer Windows 10, 19 = older
            result = ctypes.windll.dwmapi.DwmSetWindowAttribute(
                handle, attribute, ctypes.byref(value), ctypes.sizeof(value))
            if result == 0:
                break
    except Exception:
        pass  # Purely cosmetic, so any failure is safe to ignore.


def make_text_button(parent, text, command, font, accent=GOLD):
    """
    A small dark button with a gold outline that fills with colour on hover.
    Used in the favourites window.
    """
    border = mix(BLACK, accent, 0.40)
    button = tk.Label(parent, text=text, font=font, fg=accent, bg=BUTTON_BG,
                      padx=16, pady=7, cursor="hand2",
                      highlightthickness=1, highlightbackground=border)

    def on_enter(_event):
        button.configure(bg=accent, fg=BLACK, highlightbackground=accent)

    def on_leave(_event):
        button.configure(bg=BUTTON_BG, fg=accent, highlightbackground=border)

    button.bind("<Enter>", on_enter)
    button.bind("<Leave>", on_leave)
    button.bind("<Button-1>", lambda _event: command())
    return button


# ======================================================================
# 3. FAVOURITES STORAGE (JSON FILE)
# ======================================================================

class FavouritesStore:
    """
    Keeps the list of favourite quotes in memory and saves it to a JSON
    file so it is still there next time the program starts.
    """

    def __init__(self):
        self.path = self._choose_path()
        self.items = []            # each item: {"quote", "author", "saved_on"}
        self.load_message = None   # set if the file was damaged when loading
        self.load()

    @staticmethod
    def _choose_path():
        """Save next to the program if allowed, otherwise in the user's home folder."""
        try:
            folder = os.path.dirname(os.path.abspath(__file__))
        except NameError:
            folder = os.getcwd()
        if not os.access(folder, os.W_OK):
            folder = os.path.join(os.path.expanduser("~"), "DailyQuote")
            try:
                os.makedirs(folder, exist_ok=True)
            except OSError:
                folder = os.getcwd()
        return os.path.join(folder, FAVOURITES_FILENAME)

    @staticmethod
    def _key(quote, author):
        """Two quotes are 'the same' if text and author match ignoring case/spaces."""
        return quote.strip().lower(), author.strip().lower()

    def load(self):
        """Read the JSON file.  A missing file is fine; a damaged file is set aside."""
        self.items = []
        if not os.path.exists(self.path):
            return
        try:
            with open(self.path, "r", encoding="utf-8") as file:
                data = json.load(file)
            if not isinstance(data, list):
                raise ValueError("favourites file must contain a list")
        except (OSError, ValueError):
            # Keep the damaged file as a backup instead of deleting it.
            try:
                os.replace(self.path, self.path + ".damaged")
            except OSError:
                pass
            self.load_message = "Favourites file was unreadable \u2014 starting fresh"
            return

        for entry in data:
            if (isinstance(entry, dict)
                    and isinstance(entry.get("quote"), str)
                    and isinstance(entry.get("author"), str)
                    and entry["quote"].strip()):
                self.items.append({
                    "quote": entry["quote"],
                    "author": entry["author"],
                    "saved_on": str(entry.get("saved_on", "")),
                })

    def save(self):
        """Write to a temporary file first, then swap it in (safe against crashes)."""
        temporary_path = self.path + ".tmp"
        with open(temporary_path, "w", encoding="utf-8") as file:
            json.dump(self.items, file, ensure_ascii=False, indent=2)
        os.replace(temporary_path, self.path)

    def contains(self, quote, author):
        key = self._key(quote, author)
        return any(self._key(item["quote"], item["author"]) == key for item in self.items)

    def add(self, quote, author):
        """Returns True if added, False if it was already saved.  Raises OSError if the file cannot be written."""
        if self.contains(quote, author):
            return False
        entry = {"quote": quote, "author": author, "saved_on": date.today().isoformat()}
        self.items.append(entry)
        try:
            self.save()
        except OSError:
            self.items.remove(entry)   # undo, so memory matches the file
            raise
        return True

    def remove(self, quote, author):
        """Returns True if something was removed.  Raises OSError if the file cannot be written."""
        key = self._key(quote, author)
        remaining = [item for item in self.items
                     if self._key(item["quote"], item["author"]) != key]
        if len(remaining) == len(self.items):
            return False
        previous = self.items
        self.items = remaining
        try:
            self.save()
        except OSError:
            self.items = previous
            raise
        return True


# ======================================================================
# 4. THE MAIN WINDOW
# ======================================================================

class DailyQuoteApp:
    """The main cinematic window: background, quote, buttons and animation."""

    # (internal name, text on the button)
    BUTTONS = (("new", "NEW QUOTE"),
               ("save", "SAVE FAVOURITE"),
               ("copy", "COPY QUOTE"),
               ("fav", "VIEW FAVOURITES"))

    def __init__(self, root):
        self.root = root
        self.closing = False
        # How much bigger than normal this screen draws things (1.0 = normal).
        self.scale = max(1.0, root.winfo_fpixels("1i") / 96.0)
        self.serif = pick_font(SERIF_CHOICES, "Times")
        self.sans = pick_font(SANS_CHOICES, "Helvetica")

        self.favourites = FavouritesStore()
        self.fav_window = None

        # Which quote is on screen?  On start-up it is today's quote.
        self.today = date.today()
        self.current_index = quote_index_for_date(self.today)
        self.showing_daily = True

        # Fade state: 0.0 = quote invisible, 1.0 = fully visible.
        self.text_alpha = 0.0
        self.is_transitioning = True   # blocks NEW QUOTE during the opening fade-in
        self.intro_pending = True

        # Layout information, filled in by compute_metrics().
        self.W = 0
        self.H = 0
        self.ui = self.scale
        self.m = {}
        self.font_cache = {}
        self.layout_job = None

        # Button hover animation: name -> [current level, target level]
        self.button_levels = {key: [0.0, 0.0] for key, _label in self.BUTTONS}
        self.hover_job = None

        # Pop-up message ("toast") state.
        self.toast_message = ""
        self.toast_kind = "success"
        self.toast_alpha = 0.0
        self.toast_job = None

        # Background animation state.
        self.particles = make_particles()
        self.particle_items = []   # list of (canvas item id, particle dict)
        self.glow_items = []       # list of (canvas item id, t)
        self.frame_count = 0
        self.last_tick = time.time()

        # One big canvas covers the whole window; everything is drawn on it.
        self.canvas = tk.Canvas(root, bg=BLACK, highlightthickness=0, bd=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self.on_resize)
        self.bind_button_events()
        self.bind_keyboard()

        self.centre_window()
        root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.animation_job = root.after(50, self.animate)

        if self.favourites.load_message:
            message = self.favourites.load_message
            root.after(1800, lambda: self.show_toast(message, "error"))

    # ------------------------------------------------------------------
    # Window set-up
    # ------------------------------------------------------------------

    def centre_window(self):
        """Choose a sensible size for this screen and place the window in the middle."""
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        width = min(int(1100 * self.scale), int(screen_w * 0.92))
        height = min(int(780 * self.scale), int(screen_h * 0.88))
        x = (screen_w - width) // 2
        y = max(0, (screen_h - height) // 2 - 20)
        self.root.geometry("%dx%d+%d+%d" % (width, height, x, y))
        self.root.minsize(min(int(780 * self.scale), int(screen_w * 0.9)),
                          min(int(640 * self.scale), int(screen_h * 0.85)))

    def bind_keyboard(self):
        """Keyboard shortcuts: N = new quote, Ctrl+S = save, Ctrl+C = copy, F = favourites."""
        self.root.bind("<Key-n>", lambda event: self.new_quote())
        self.root.bind("<Key-N>", lambda event: self.new_quote())
        self.root.bind("<Control-s>", lambda event: self.save_favourite())
        self.root.bind("<Control-c>", lambda event: self.copy_quote())
        self.root.bind("<Key-f>", lambda event: self.open_favourites())
        self.root.bind("<Key-F>", lambda event: self.open_favourites())

    def bind_button_events(self):
        """Connect mouse events to the canvas-drawn buttons (done once, by tag name)."""
        for key, _label in self.BUTTONS:
            tag = "btn_" + key
            self.canvas.tag_bind(tag, "<Enter>", lambda event, k=key: self.on_button_enter(k))
            self.canvas.tag_bind(tag, "<Leave>", lambda event, k=key: self.on_button_leave(k))
            self.canvas.tag_bind(tag, "<Button-1>", lambda event, k=key: self.on_button_click(k))

    def on_close(self):
        """Stop all timers, then close the window."""
        self.closing = True
        for job in (self.animation_job, self.layout_job, self.hover_job, self.toast_job):
            if job is not None:
                try:
                    self.root.after_cancel(job)
                except tk.TclError:
                    pass
        self.root.destroy()

    # ------------------------------------------------------------------
    # Layout helpers
    # ------------------------------------------------------------------

    def u(self, number):
        """Convert a design measurement into real pixels for the current window size."""
        return int(round(number * self.ui))

    def get_font(self, family, units, bold=False, italic=False, minimum=10):
        """Create (or reuse) a font.  Negative size means 'size in pixels'."""
        pixels = max(minimum, int(round(units * self.ui)))
        key = (family, pixels, bold, italic)
        if key not in self.font_cache:
            self.font_cache[key] = tkfont.Font(
                family=family, size=-pixels,
                weight="bold" if bold else "normal",
                slant="italic" if italic else "roman")
        return self.font_cache[key]

    @staticmethod
    def wrap_text(text, font, max_width):
        """Break text into lines that are no wider than max_width pixels."""
        lines = []
        line = ""
        for word in text.split():
            trial = word if not line else line + " " + word
            if line and font.measure(trial) > max_width:
                lines.append(line)
                line = word
            else:
                line = trial
        if line:
            lines.append(line)
        return lines

    def balanced_wrap(self, text, font, max_width):
        """
        Wrap text, then narrow the column as far as possible without adding
        a line.  This avoids a lonely last word and looks more elegant.
        """
        lines = self.wrap_text(text, font, max_width)
        if len(lines) < 2:
            return lines
        count = len(lines)
        best = lines
        low, high = max_width * 0.5, float(max_width)
        for _ in range(8):
            middle = (low + high) / 2.0
            trial = self.wrap_text(text, font, middle)
            if len(trial) <= count:
                best = trial
                high = middle
            else:
                low = middle
        return best

    def compute_metrics(self, width, height):
        """Work out where everything goes for the current window size."""
        scale = self.scale
        design_ratio = min(width / (1000.0 * scale), height / (700.0 * scale))
        ui = scale * max(0.8, min(1.25, design_ratio))
        if abs(ui - self.ui) > 1e-6:
            self.font_cache.clear()
        self.W, self.H, self.ui = width, height, ui
        u = self.u

        # --- buttons: one row of four if they fit, otherwise two rows of two ---
        button_font = self.get_font(self.sans, 12, bold=True, minimum=11)
        button_h = u(42)
        gap = u(14)
        side_margin = u(70)
        needed_width = max(button_font.measure(label) for _k, label in self.BUTTONS) + u(48)
        available = width - 2 * side_margin
        one_row_width = (available - 3 * gap) / 4.0

        footer_y = height - u(40)
        bottom_cy = footer_y - u(52)
        positions = []
        if one_row_width >= needed_width:
            button_w = min(one_row_width, u(210))
            total = 4 * button_w + 3 * gap
            first_x = (width - total) / 2.0 + button_w / 2.0
            for number, (key, label) in enumerate(self.BUTTONS):
                positions.append((key, label, first_x + number * (button_w + gap), bottom_cy))
            buttons_top = bottom_cy - button_h / 2.0
        else:
            button_w = min((available - gap) / 2.0, u(210))
            total = 2 * button_w + gap
            first_x = (width - total) / 2.0 + button_w / 2.0
            top_cy = bottom_cy - (button_h + u(12))
            for number, (key, label) in enumerate(self.BUTTONS):
                column, row = number % 2, number // 2
                positions.append((key, label, first_x + column * (button_w + gap),
                                  top_cy if row == 0 else bottom_cy))
            buttons_top = top_cy - button_h / 2.0

        toast_y = buttons_top - u(30)
        self.m = {
            "heading_y": u(54),
            "subtitle_y": u(84),
            "footer_y": footer_y,
            "area_top": u(84) + u(26),
            "area_bottom": toast_y - u(22),
            "toast_y": toast_y,
            "button_positions": positions,
            "button_w": button_w,
            "button_h": button_h,
            "button_font": button_font,
        }

    # ------------------------------------------------------------------
    # Drawing (everything is redrawn when the window size changes)
    # ------------------------------------------------------------------

    def on_resize(self, _event):
        """Wait a moment after resizing stops, then redraw once (keeps dragging smooth)."""
        if self.layout_job is not None:
            self.root.after_cancel(self.layout_job)
        self.layout_job = self.root.after(60, self.layout)

    def layout(self):
        """Clear the canvas and draw every layer from back to front."""
        self.layout_job = None
        if self.closing:
            return
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        if width < 200 or height < 200:
            return
        self.canvas.delete("all")
        self.compute_metrics(width, height)
        self.draw_background()
        self.draw_frame_and_header()
        self.draw_quote_block()
        self.draw_buttons()
        self.draw_toast()

        if self.intro_pending:
            # Opening shot: the quote slowly fades in from darkness.
            self.intro_pending = False
            self.root.after(300, lambda: self.run_fade(1.0, 40, 30, self.finish_transition))

    def draw_background(self):
        """Layer 1: spotlight made of nested ellipses, then stars and golden dust."""
        canvas = self.canvas
        centre_x = self.W / 2.0
        centre_y = (self.m["area_top"] + self.m["area_bottom"]) / 2.0
        steps = 48
        self.glow_items = []
        for number in range(steps):
            t = number / float(steps - 1)          # 0 = biggest ring, 1 = smallest
            fraction = (1.0 - t) ** 1.15
            radius_x = max(self.u(8), self.W * 0.95 * fraction)
            radius_y = max(self.u(6), self.H * 0.95 * fraction)
            item = canvas.create_oval(centre_x - radius_x, centre_y - radius_y,
                                      centre_x + radius_x, centre_y + radius_y,
                                      fill=glow_colour(t, 0.8), outline="", tags="bg")
            self.glow_items.append((item, t))

        now = time.time()
        self.particle_items = []
        for particle in self.particles:
            radius = particle["size"] * self.ui
            x = particle["x"] * self.W
            y = particle["y"] * self.H
            item = canvas.create_oval(x - radius, y - radius, x + radius, y + radius,
                                      fill=particle_colour(particle, now), outline="", tags="bg")
            self.particle_items.append((item, particle))

    def draw_flanked_text(self, y, text, font, text_colour, line_colour, line_length):
        """Centred text with a thin gold line on each side."""
        centre_x = self.W / 2.0
        self.canvas.create_text(centre_x, y, text=text, font=font, fill=text_colour,
                                anchor="center", tags="header")
        half_text = font.measure(text) / 2.0
        spacing = self.u(22)
        self.canvas.create_line(centre_x - half_text - spacing - line_length, y,
                                centre_x - half_text - spacing, y,
                                fill=line_colour, tags="header")
        self.canvas.create_line(centre_x + half_text + spacing, y,
                                centre_x + half_text + spacing + line_length, y,
                                fill=line_colour, tags="header")

    def draw_frame_and_header(self):
        """Layer 2: decorative frame, title, subtitle and footer."""
        canvas = self.canvas
        u = self.u
        outer, inner = u(16), u(24)
        canvas.create_rectangle(outer, outer, self.W - outer, self.H - outer,
                                outline=GOLD_DIM, width=1, tags="frame")
        canvas.create_rectangle(inner, inner, self.W - inner, self.H - inner,
                                outline=GOLD_FAINT, width=1, tags="frame")

        # Brighter gold corner accents (like a film viewfinder).
        length = u(34)
        corners = ((outer, outer, 1, 1), (self.W - outer, outer, -1, 1),
                   (outer, self.H - outer, 1, -1), (self.W - outer, self.H - outer, -1, -1))
        for x, y, step_x, step_y in corners:
            canvas.create_line(x, y + step_y * length, x, y, x + step_x * length, y,
                               fill=GOLD, width=2, tags="frame")

        self.draw_flanked_text(self.m["heading_y"], spaced("DAILYQUOTE", 2),
                               self.get_font(self.sans, 14, bold=True), GOLD, GOLD_DIM, u(90))
        canvas.create_text(self.W / 2.0, self.m["subtitle_y"],
                           text=spaced("WORDS THAT MOVE YOU.", 1),
                           font=self.get_font(self.sans, 11), fill=SOFT_GREY,
                           anchor="center", tags="header")
        self.draw_flanked_text(self.m["footer_y"], spaced("A MOMENT OF CLARITY.", 1),
                               self.get_font(self.sans, 10), mix(BLACK, SOFT_GREY, 0.70),
                               GOLD_FAINT, u(50))

    def draw_quote_block(self):
        """
        Layer 3: label, big quote mark, quote text, divider and author.
        The font size is chosen automatically: the biggest size that still
        fits the space available, so nothing is ever cut off.
        """
        canvas = self.canvas
        u = self.u
        canvas.delete("quote_block")
        if not self.m:
            return
        quote, author = QUOTES[self.current_index]
        centre_x = self.W / 2.0

        max_width = min(self.W - u(260), u(820))
        available = self.m["area_bottom"] - self.m["area_top"]
        label_h, mark_h, lines_gap = u(40), u(48), u(26)
        divider_h, author_gap, author_h = u(14), u(14), u(22)
        fixed_height = label_h + mark_h + lines_gap + divider_h + author_gap + author_h

        # Try big fonts first and shrink until the whole block fits.
        quote_font, lines, line_height, total = None, [], 0, 0
        for size in range(36, 13, -1):
            quote_font = self.get_font(self.serif, size, italic=True, minimum=13)
            lines = self.balanced_wrap(quote, quote_font, max_width)
            line_height = int(quote_font.metrics("linespace") * 1.32)
            total = fixed_height + len(lines) * line_height
            if total <= available:
                break

        # Author font also shrinks if the name is very long.
        author_text = spaced(author.upper(), 1)
        author_font = self.get_font(self.sans, 14, bold=True)
        for size in range(14, 9, -1):
            author_font = self.get_font(self.sans, size, bold=True)
            if author_font.measure(author_text) <= self.W - u(160):
                break

        y = self.m["area_top"] + max(0, (available - total) / 2.0)

        # Small label and date.
        label_text = "TODAY'S INSPIRATION" if self.showing_daily else "A FRESH INSPIRATION"
        canvas.create_text(centre_x, y, text=spaced(label_text, 1),
                           font=self.get_font(self.sans, 11, bold=True), anchor="n",
                           tags=("quote_block", "fade_gold"))
        canvas.create_text(centre_x, y + u(20),
                           text=self.today.strftime("%A, %d %B %Y").upper(),
                           font=self.get_font(self.sans, 10), anchor="n",
                           tags=("quote_block", "fade_grey"))
        y += label_h

        # Oversized opening quotation mark.
        canvas.create_text(centre_x, y, text="\u201c",
                           font=self.get_font(self.serif, 84, minimum=40), anchor="n",
                           tags=("quote_block", "fade_mark"))
        y += mark_h

        # The quote itself, one canvas text item per line (gives us full control of spacing).
        for line in lines:
            canvas.create_text(centre_x, y, text=line, font=quote_font, anchor="n",
                               tags=("quote_block", "fade_quote"))
            y += line_height

        # Closing quotation mark, tucked after the last word.
        last_line_y = y - line_height
        last_line_width = quote_font.measure(lines[-1]) if lines else 0
        canvas.create_text(centre_x + last_line_width / 2.0 + u(6), last_line_y - u(4),
                           text="\u201d", font=self.get_font(self.serif, 46, minimum=24),
                           anchor="nw", tags=("quote_block", "fade_mark"))

        # Thin gold divider with a small diamond in the middle.
        divider_y = y + lines_gap + divider_h / 2.0
        half_line, hole, diamond = u(80), u(12), u(4)
        canvas.create_line(centre_x - half_line, divider_y, centre_x - hole, divider_y,
                           fill=GOLD, width=1, tags=("quote_block", "fade_line"))
        canvas.create_line(centre_x + hole, divider_y, centre_x + half_line, divider_y,
                           fill=GOLD, width=1, tags=("quote_block", "fade_line"))
        canvas.create_polygon(centre_x, divider_y - diamond, centre_x + diamond, divider_y,
                              centre_x, divider_y + diamond, centre_x - diamond, divider_y,
                              fill=GOLD, outline="", tags=("quote_block", "fade_line"))
        y += lines_gap + divider_h + author_gap

        # Author.
        canvas.create_text(centre_x, y, text=author_text, font=author_font, anchor="n",
                           tags=("quote_block", "fade_gold"))

        self.apply_text_alpha()

    def apply_text_alpha(self):
        """Colour every quote item according to the current fade level."""
        alpha = self.text_alpha
        canvas = self.canvas
        canvas.itemconfigure("fade_quote", fill=mix(TEXT_BG, WARM_WHITE, alpha))
        canvas.itemconfigure("fade_gold", fill=mix(TEXT_BG, GOLD, alpha))
        canvas.itemconfigure("fade_grey", fill=mix(TEXT_BG, SOFT_GREY, alpha))
        canvas.itemconfigure("fade_mark", fill=mix(TEXT_BG, MARK_GOLD, alpha))
        canvas.itemconfigure("fade_line", fill=mix(TEXT_BG, GOLD, alpha))

    def draw_buttons(self):
        """Layer 4: the four buttons, drawn as rectangles with text on the canvas."""
        canvas = self.canvas
        canvas.delete("button")
        half_w = self.m["button_w"] / 2.0
        half_h = self.m["button_h"] / 2.0
        for key, label, x, y in self.m["button_positions"]:
            if key == "save":
                label = self.save_label()
            tag = "btn_" + key
            canvas.create_rectangle(x - half_w, y - half_h, x + half_w, y + half_h,
                                    fill=BUTTON_BG, outline=GOLD_DIM, width=1,
                                    tags=("button", tag, tag + "_rect"))
            canvas.create_text(x, y, text=label, font=self.m["button_font"], fill=WARM_WHITE,
                               tags=("button", tag, tag + "_text"))
            self.paint_button(key)

    def draw_toast(self):
        """Layer 5: the small message pill above the buttons (only if one is showing)."""
        canvas = self.canvas
        canvas.delete("toast")
        if self.toast_alpha <= 0.01 or not self.toast_message:
            return
        alpha = self.toast_alpha
        accent = GOLD if self.toast_kind == "success" else ERROR_RED
        text_colour = WARM_WHITE if self.toast_kind == "success" else ERROR_RED
        font = self.get_font(self.sans, 12, minimum=11)
        width = font.measure(self.toast_message) + self.u(48)
        height = self.u(32)
        x, y = self.W / 2.0, self.m["toast_y"]
        canvas.create_rectangle(x - width / 2.0, y - height / 2.0, x + width / 2.0, y + height / 2.0,
                                fill=mix(NAVY, BUTTON_BG, alpha),
                                outline=mix(NAVY, accent, alpha * 0.85), tags="toast")
        canvas.create_text(x, y, text=self.toast_message, font=font,
                           fill=mix(NAVY, text_colour, alpha), tags="toast")

    # ------------------------------------------------------------------
    # Animation
    # ------------------------------------------------------------------

    def animate(self):
        """Runs about 20 times a second: moves the particles and breathes the glow."""
        if self.closing:
            return
        self.animation_job = self.root.after(50, self.animate)   # schedule the next frame first
        now = time.time()
        dt = min(0.2, now - self.last_tick)
        self.last_tick = now
        if self.W < 200 or self.root.state() == "iconic":
            return   # nothing to draw / window minimised: save CPU
        self.frame_count += 1
        self.move_particles(now, dt)
        if self.frame_count % 3 == 0:
            self.pulse_glow(now)

    def move_particles(self, now, dt):
        """Drift every star/dust speck slowly upwards and twinkle its colour."""
        twinkle_now = (self.frame_count % 3 == 0)
        for item, particle in self.particle_items:
            particle["y"] -= particle["speed"] * dt
            particle["x"] += particle["drift"] * dt
            if particle["y"] < -0.02:          # left the top: re-enter at the bottom
                particle["y"] = 1.02
                particle["x"] = random.random()
            if particle["x"] < -0.02:
                particle["x"] = 1.02
            elif particle["x"] > 1.02:
                particle["x"] = -0.02
            radius = particle["size"] * self.ui
            x = particle["x"] * self.W
            y = particle["y"] * self.H
            self.canvas.coords(item, x - radius, y - radius, x + radius, y + radius)
            if twinkle_now:
                self.canvas.itemconfigure(item, fill=particle_colour(particle, now))

    def pulse_glow(self, now):
        """Make the spotlight slowly brighten and dim (a cycle of about 8 seconds)."""
        pulse = 0.78 + 0.22 * math.sin(now * 0.8)
        for item, t in self.glow_items:
            self.canvas.itemconfigure(item, fill=glow_colour(t, pulse))

    def run_fade(self, target, steps, interval, on_done=None):
        """
        Smoothly change the quote's visibility to `target` (0 or 1).
        steps    : how many small changes to make
        interval : milliseconds between changes
        """
        start = self.text_alpha

        def step(number):
            if self.closing:
                return
            t = number / float(steps)
            eased = t * t * (3 - 2 * t)        # smooth start and end
            self.text_alpha = start + (target - start) * eased
            self.apply_text_alpha()
            if number < steps:
                self.root.after(interval, lambda: step(number + 1))
            elif on_done is not None:
                on_done()

        step(1)

    def finish_transition(self):
        self.is_transitioning = False

    def transition_to(self, index, daily):
        """Fade the old quote out, swap in the new one, fade it in."""
        self.is_transitioning = True

        def swap():
            self.current_index = index
            self.showing_daily = daily
            self.draw_quote_block()
            self.update_save_button()
            self.run_fade(1.0, 14, 22, self.finish_transition)

        self.run_fade(0.0, 8, 20, swap)

    # Button hover effect ------------------------------------------------

    def on_button_enter(self, key):
        self.canvas.configure(cursor="hand2")
        self.set_button_target(key, 1.0)

    def on_button_leave(self, key):
        self.canvas.configure(cursor="")
        self.set_button_target(key, 0.0)

    def set_button_target(self, key, target):
        self.button_levels[key][1] = target
        if self.hover_job is None:
            self.hover_job = self.root.after(16, self.step_button_hover)

    def step_button_hover(self):
        """Move each button's hover level a little closer to its target."""
        self.hover_job = None
        if self.closing:
            return
        busy = False
        for key, state in self.button_levels.items():
            current, target = state
            if abs(current - target) > 0.01:
                current += (target - current) * 0.35
                if abs(target - current) < 0.02:
                    current = target
                state[0] = current
                self.paint_button(key)
                busy = True
        if busy:
            self.hover_job = self.root.after(16, self.step_button_hover)

    def paint_button(self, key):
        """Colour a button for its current hover level (0 = resting, 1 = hovered)."""
        level = self.button_levels[key][0]
        self.canvas.itemconfigure("btn_%s_rect" % key,
                                  fill=mix(BUTTON_BG, GOLD, level * 0.95),
                                  outline=mix(GOLD_DIM, GOLD, level))
        self.canvas.itemconfigure("btn_%s_text" % key, fill=mix(WARM_WHITE, BLACK, level))

    # Pop-up messages ----------------------------------------------------

    def show_toast(self, message, kind="success"):
        """Show a short message that fades in, waits, then fades out."""
        if self.toast_job is not None:
            self.root.after_cancel(self.toast_job)
            self.toast_job = None
        self.toast_message = message
        self.toast_kind = kind
        self.toast_step(1)

    def toast_step(self, direction):
        self.toast_job = None
        if self.closing:
            return
        if direction > 0:
            self.toast_alpha = min(1.0, self.toast_alpha + 0.2)
            self.draw_toast()
            if self.toast_alpha < 1.0:
                self.toast_job = self.root.after(20, lambda: self.toast_step(1))
            else:
                self.toast_job = self.root.after(2200, lambda: self.toast_step(-1))
        else:
            self.toast_alpha = max(0.0, self.toast_alpha - 0.1)
            self.draw_toast()
            if self.toast_alpha > 0.0:
                self.toast_job = self.root.after(25, lambda: self.toast_step(-1))

    # ------------------------------------------------------------------
    # What the buttons do
    # ------------------------------------------------------------------

    def on_button_click(self, key):
        actions = {
            "new": self.new_quote,
            "save": self.save_favourite,
            "copy": self.copy_quote,
            "fav": self.open_favourites,
        }
        actions[key]()

    def new_quote(self):
        """Show a different random quote (never the same one twice in a row)."""
        if self.is_transitioning:
            return
        choices = [number for number in range(len(QUOTES)) if number != self.current_index]
        self.transition_to(random.choice(choices), daily=False)

    def copy_to_clipboard(self, text):
        """Put text on the system clipboard.  Returns True if it worked."""
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.root.update()   # makes Windows keep the text after this call
            return True
        except tk.TclError:
            return False

    def copy_quote(self):
        quote, author = QUOTES[self.current_index]
        if self.copy_to_clipboard("\u201c%s\u201d\n\u2014 %s" % (quote, author)):
            self.show_toast("Quote copied to clipboard", "success")
        else:
            self.show_toast("Could not access the clipboard", "error")

    def save_favourite(self):
        quote, author = QUOTES[self.current_index]
        try:
            added = self.favourites.add(quote, author)
        except OSError:
            self.show_toast("Could not write the favourites file", "error")
            return
        if added:
            self.show_toast("Saved to your favourites", "success")
        else:
            self.show_toast("Already in your favourites", "error")
        self.notify_favourites_changed()

    def save_label(self):
        """The save button reads SAVED once the current quote is a favourite."""
        quote, author = QUOTES[self.current_index]
        return "SAVED" if self.favourites.contains(quote, author) else "SAVE FAVOURITE"

    def update_save_button(self):
        self.canvas.itemconfigure("btn_save_text", text=self.save_label())

    def notify_favourites_changed(self):
        """Called whenever favourites change, so both windows stay in step."""
        self.update_save_button()
        if self.fav_window is not None and self.fav_window.window.winfo_exists():
            self.fav_window.refresh()

    def open_favourites(self):
        """Open the favourites window (or bring it forward if it is already open)."""
        if self.fav_window is not None and self.fav_window.window.winfo_exists():
            self.fav_window.refresh()
            self.fav_window.window.deiconify()
            self.fav_window.window.lift()
            self.fav_window.window.focus_force()
            return
        self.fav_window = FavouritesWindow(self)


# ======================================================================
# 5. THE FAVOURITES WINDOW
# ======================================================================

class FavouritesWindow:
    """A dark, scrollable window listing every saved quote."""

    def __init__(self, app):
        self.app = app
        self.scale = app.scale
        self.status_job = None
        self.wrap_labels = []

        self.window = tk.Toplevel(app.root)
        self.window.title("DailyQuote \u2014 Favourites")
        self.window.configure(bg=BLACK)
        self.window.protocol("WM_DELETE_WINDOW", self.close)
        self.window.bind("<Escape>", lambda event: self.close())

        self.place_window()
        self.build_scrollbar_style()
        self.build_widgets()
        self.refresh()
        use_dark_title_bar(self.window)
        self.window.focus_force()

    # Small helpers for sizes and fonts that respect screen scaling.
    def px(self, number):
        return int(round(number * self.scale))

    def font(self, family, size, style=""):
        if style:
            return (family, -self.px(size), style)
        return (family, -self.px(size))

    def place_window(self):
        """Size the window for this screen and centre it over the main window."""
        root = self.app.root
        screen_w, screen_h = root.winfo_screenwidth(), root.winfo_screenheight()
        width = min(self.px(780), int(screen_w * 0.9))
        height = min(self.px(700), int(screen_h * 0.88))
        x = root.winfo_rootx() + (root.winfo_width() - width) // 2
        y = root.winfo_rooty() + (root.winfo_height() - height) // 2
        x = max(0, min(x, screen_w - width))
        y = max(0, min(y, screen_h - height - self.px(40)))
        self.window.geometry("%dx%d+%d+%d" % (width, height, x, y))
        self.window.minsize(min(self.px(520), width), min(self.px(420), height))

    def build_scrollbar_style(self):
        """Dark gold scrollbar using ttk styling."""
        style = ttk.Style(self.window)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Cinematic.Vertical.TScrollbar",
                        background=GOLD_DIM, troughcolor=BLACK, bordercolor=BLACK,
                        arrowcolor=GOLD, lightcolor=GOLD_DIM, darkcolor=GOLD_DIM,
                        relief="flat")
        style.map("Cinematic.Vertical.TScrollbar", background=[("active", GOLD)])

    def build_widgets(self):
        window = self.window
        sans, serif = self.app.sans, self.app.serif
        margin = self.px(30)

        # Header with title and a count of saved quotes.
        header = tk.Frame(window, bg=BLACK)
        header.pack(side="top", fill="x", padx=margin, pady=(self.px(26), self.px(10)))
        tk.Label(header, text=spaced("YOUR FAVOURITES", 1), font=self.font(sans, 16, "bold"),
                 fg=GOLD, bg=BLACK).pack(anchor="w")
        self.count_label = tk.Label(header, text="", font=self.font(sans, 11),
                                    fg=SOFT_GREY, bg=BLACK)
        self.count_label.pack(anchor="w", pady=(self.px(4), 0))
        tk.Frame(window, height=1, bg=GOLD_DIM).pack(side="top", fill="x", padx=margin)

        # Bottom bar (packed before the middle so it is never squeezed out).
        bottom = tk.Frame(window, bg=BLACK)
        bottom.pack(side="bottom", fill="x", padx=margin, pady=self.px(16))
        self.status_label = tk.Label(bottom, text="", font=self.font(sans, 12),
                                     fg=GOLD, bg=BLACK, anchor="w")
        self.status_label.pack(side="left")
        make_text_button(bottom, "CLOSE", self.close, self.font(sans, 11, "bold")).pack(side="right")
        tk.Frame(window, height=1, bg=GOLD_FAINT).pack(side="bottom", fill="x", padx=margin)

        # Scrollable list of quote cards.
        body = tk.Frame(window, bg=BLACK)
        body.pack(side="top", fill="both", expand=True, padx=margin, pady=(self.px(14), 0))
        self.canvas = tk.Canvas(body, bg=BLACK, highlightthickness=0, bd=0)
        scrollbar = ttk.Scrollbar(body, orient="vertical", command=self.canvas.yview,
                                  style="Cinematic.Vertical.TScrollbar")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.inner = tk.Frame(self.canvas, bg=BLACK)
        self.inner_id = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>",
                        lambda event: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", self.on_canvas_resize)

        # Mouse-wheel scrolling (Windows/macOS use <MouseWheel>, Linux uses Button-4/5).
        self.canvas.bind("<Enter>", lambda event: self.canvas.focus_set())
        window.bind("<MouseWheel>", self.on_mouse_wheel)
        window.bind("<Button-4>", self.on_mouse_wheel)
        window.bind("<Button-5>", self.on_mouse_wheel)

        self.serif = serif
        self.sans = sans

    def on_mouse_wheel(self, event):
        if self.canvas.yview() == (0.0, 1.0):
            return   # everything already fits, nothing to scroll
        if getattr(event, "num", 0) == 4:
            direction = -1
        elif getattr(event, "num", 0) == 5:
            direction = 1
        else:
            direction = -1 if event.delta > 0 else 1
        self.canvas.yview_scroll(direction * 2, "units")

    def on_canvas_resize(self, event):
        """Keep the cards as wide as the window and re-wrap the text."""
        self.canvas.itemconfigure(self.inner_id, width=event.width)
        self.apply_wraplength(event.width)

    def apply_wraplength(self, width):
        wrap = max(self.px(200), width - 2 * self.px(22) - self.px(6))
        for label in self.wrap_labels:
            label.configure(wraplength=wrap)

    # Content -------------------------------------------------------------

    def refresh(self):
        """Rebuild the list of cards from the saved favourites."""
        for child in self.inner.winfo_children():
            child.destroy()
        self.wrap_labels = []
        items = self.app.favourites.items

        if not items:
            self.count_label.configure(text="NO SAVED QUOTES YET")
            tk.Label(self.inner, text="Nothing here yet", font=self.font(self.serif, 26, "italic"),
                     fg=WARM_WHITE, bg=BLACK).pack(pady=(self.px(70), self.px(8)))
            tk.Label(self.inner, text="Press SAVE FAVOURITE on a quote you love\nand it will appear here.",
                     font=self.font(self.sans, 13), fg=SOFT_GREY, bg=BLACK,
                     justify="center").pack()
            return

        self.count_label.configure(
            text="%d SAVED QUOTE%s" % (len(items), "" if len(items) == 1 else "S"))
        for item in reversed(items):          # newest first
            self.build_card(item)
        self.apply_wraplength(self.canvas.winfo_width())

    def build_card(self, item):
        """One framed card showing a quote, its author and its Copy / Remove buttons."""
        card = tk.Frame(self.inner, bg=CARD_BG, highlightthickness=1, highlightbackground=GOLD_FAINT)
        card.pack(fill="x", pady=(0, self.px(14)))
        body = tk.Frame(card, bg=CARD_BG)
        body.pack(fill="x", padx=self.px(22), pady=self.px(18))

        quote_label = tk.Label(body, text="\u201c%s\u201d" % item["quote"],
                               font=self.font(self.serif, 20, "italic"),
                               fg=WARM_WHITE, bg=CARD_BG, justify="left", anchor="w",
                               wraplength=self.px(500))
        quote_label.pack(fill="x")
        self.wrap_labels.append(quote_label)

        tk.Label(body, text="\u2014 " + item["author"], font=self.font(self.sans, 13, "bold"),
                 fg=GOLD, bg=CARD_BG, anchor="w").pack(fill="x", pady=(self.px(10), 0))

        actions = tk.Frame(body, bg=CARD_BG)
        actions.pack(fill="x", pady=(self.px(14), 0))
        saved_text = pretty_date(item.get("saved_on", ""))
        if saved_text:
            tk.Label(actions, text="SAVED " + saved_text, font=self.font(self.sans, 10),
                     fg=SOFT_GREY, bg=CARD_BG).pack(side="left")

        small_font = self.font(self.sans, 11, "bold")
        remove_button = make_text_button(actions, "REMOVE", lambda: None, small_font, ERROR_RED)
        remove_button.pack(side="right")
        copy_button = make_text_button(actions, "COPY", lambda: self.copy_item(item), small_font)
        copy_button.pack(side="right", padx=(0, self.px(10)))

        # Removing needs two clicks so a favourite is never deleted by accident.
        state = {"armed": False}

        def disarm():
            state["armed"] = False
            if remove_button.winfo_exists():
                remove_button.configure(text="REMOVE")

        def on_remove_click(_event):
            if state["armed"]:
                self.remove_item(item)
            else:
                state["armed"] = True
                remove_button.configure(text="CLICK AGAIN TO CONFIRM")
                self.window.after(2500, disarm)

        remove_button.bind("<Button-1>", on_remove_click)

    # Actions --------------------------------------------------------------

    def copy_item(self, item):
        text = "\u201c%s\u201d\n\u2014 %s" % (item["quote"], item["author"])
        if self.app.copy_to_clipboard(text):
            self.flash("Quote copied to clipboard")
        else:
            self.flash("Could not access the clipboard", error=True)

    def remove_item(self, item):
        try:
            self.app.favourites.remove(item["quote"], item["author"])
        except OSError:
            self.flash("Could not update the favourites file", error=True)
            return
        self.app.update_save_button()
        self.refresh()
        self.flash("Removed from favourites")

    def flash(self, message, error=False):
        """Show a short status message at the bottom of this window."""
        if self.status_job is not None:
            self.window.after_cancel(self.status_job)
        self.status_label.configure(text=message, fg=ERROR_RED if error else GOLD)
        self.status_job = self.window.after(2600, self.clear_status)

    def clear_status(self):
        self.status_job = None
        if self.status_label.winfo_exists():
            self.status_label.configure(text="")

    def close(self):
        self.window.destroy()
        self.app.fav_window = None


# ======================================================================
# 6. START THE PROGRAM
# ======================================================================

def main():
    enable_sharp_text_on_windows()
    root = tk.Tk()
    root.title(APP_TITLE)
    root.configure(bg=BLACK)
    DailyQuoteApp(root)
    use_dark_title_bar(root)
    root.mainloop()


if __name__ == "__main__":
    main()
