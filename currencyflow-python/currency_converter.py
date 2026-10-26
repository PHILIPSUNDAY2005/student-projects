# -*- coding: utf-8 -*-
"""
CurrencyFlow - Currency Converter
=================================
A modern, offline currency converter written with Python's standard
library only (Tkinter + ttk).  No internet, API keys or extra packages.

IMPORTANT - THE RATES ARE ILLUSTRATIVE
--------------------------------------
The exchange rates in RATES_PER_BASE (see section 1) are SAMPLE values for
demonstration.  They are NOT live market rates.  You can edit them freely.

HOW THE CONVERSION WORKS  (the algorithm)
-----------------------------------------
We store ONE rate per currency, measured against a common BASE currency
(USD).  A rate says: "how many units of this currency equal 1 USD?".

To convert  amount  from currency A to currency B:

    step 1:  amount_in_base = amount / rate[A]      (A  ->  USD)
    step 2:  result         = amount_in_base * rate[B]   (USD ->  B)

which is the same as   result = amount * (rate[B] / rate[A]).

Why use a base currency?  With n currencies we only store n rates instead of
n * (n - 1) separate pair rates, and adding a new currency means adding just
ONE line.  Each conversion is two arithmetic operations and two dictionary
look-ups, so it runs in constant time, O(1).

We use Python's `Decimal` type (not float) so that money maths is exact and
rounds the way people expect (0.005 rounds UP to 0.01).

HOW TO RUN
----------
    python currency_converter.py            (opens the app)
    python currency_converter.py --test     (runs the built-in logic tests)

HOW THE FILE IS ORGANISED
-------------------------
    1. Settings: the sample rates and currency names (edit these)
    2. Conversion logic: parse_amount, convert, formatting  (no GUI code)
    3. Colours, fonts and small drawing helpers
    4. Custom widgets: RoundedFrame, FlowButton, SwapButton, HeaderBar
    5. The application window (CurrencyFlowApp)
    6. Self-test and main()
"""

import sys
import tkinter as tk
import tkinter.font as tkfont
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from tkinter import ttk


# ======================================================================
# 1. SETTINGS - EDIT THE SAMPLE RATES HERE
# ======================================================================

APP_NAME = "CurrencyFlow"
AUTHOR_NAME = "Bayode Philip Sunday"     # shown in the footer - change it here

# The base currency every other rate is measured against.
BASE_CURRENCY = "USD"

# SAMPLE RATES (illustrative only, NOT live market rates).
# Meaning: how many units of the currency equal 1 unit of the base (USD).
RATES_PER_BASE = {
    "USD": 1.00,
    "NGN": 1500.00,
    "GBP": 0.79,
    "EUR": 0.92,
}

# Short names shown in the drop-down lists.
CURRENCY_NAMES = {
    "NGN": "Naira",
    "USD": "US Dollar",
    "GBP": "British Pound",
    "EUR": "Euro",
}

# The order the currencies appear in the drop-downs.
DISPLAY_ORDER = ["NGN", "USD", "GBP", "EUR"]

# Largest amount we accept (keeps the result display sensible).
MAX_AMOUNT = Decimal("1000000000000")      # one trillion
TWO_PLACES = Decimal("0.01")


# ======================================================================
# 2. CONVERSION LOGIC (no GUI code in this section)
# ======================================================================

class AmountError(ValueError):
    """Raised when the typed amount is not acceptable. The message is user-friendly."""


def parse_amount(text):
    """
    Turn the text typed by the user into a Decimal number.
    Raises AmountError with a friendly message if it is empty, not a
    number, zero, negative or too large.
    """
    cleaned = text.strip().replace(",", "").replace(" ", "")   # allow "1,500.50"
    if cleaned == "":
        raise AmountError("Please enter an amount to convert.")
    try:
        value = Decimal(cleaned)
    except InvalidOperation:
        raise AmountError("That doesn't look like a number. Try something like 2500.50.")
    if not value.is_finite():                                   # rejects "NaN" and "Infinity"
        raise AmountError("That doesn't look like a number. Try something like 2500.50.")
    if value < 0:
        raise AmountError("The amount cannot be negative.")
    if value == 0:
        raise AmountError("The amount must be greater than zero.")
    if value > MAX_AMOUNT:
        raise AmountError("That amount is too large. Please use a smaller number.")
    return value


def get_rate(code, rates):
    """Look up the rate of one currency as a Decimal, with clear errors."""
    if code not in rates:
        raise ValueError("No exchange rate is available for " + str(code) + ".")
    rate = Decimal(str(rates[code]))      # str() first, so 0.79 stays exactly 0.79
    if rate <= 0:
        raise ValueError("The rate for " + str(code) + " must be greater than zero.")
    return rate


def convert(amount, from_code, to_code, rates=None):
    """
    Convert `amount` (a Decimal) from one currency to another THROUGH THE
    BASE CURRENCY.  The answer is returned unrounded; use round_money()
    to round it to two decimal places for display.
    """
    if rates is None:
        rates = RATES_PER_BASE
    rate_from = get_rate(from_code, rates)
    rate_to = get_rate(to_code, rates)
    amount_in_base = amount / rate_from        # step 1: source currency -> base
    return amount_in_base * rate_to            # step 2: base -> target currency


def round_money(value):
    """Round to two decimal places, halves round up (like a bank would show)."""
    return value.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)


def format_money(value):
    """12345.6 -> '12,345.60'"""
    return "{:,.2f}".format(round_money(value))


def format_rate(rate):
    """Format an exchange rate: 1500 -> '1,500.00', 0.000667 -> '0.000667'."""
    text = "{:,.6f}".format(rate) if rate < 1 else "{:,.4f}".format(rate)
    whole, fraction = text.split(".")
    return whole + "." + fraction.rstrip("0").ljust(2, "0")


# ======================================================================
# 3. COLOURS, FONTS AND DRAWING HELPERS
# ======================================================================

NAVY = "#0B1F4B"          # deep navy (header, result card, main text)
NAVY_LIGHT = "#102B63"    # slightly lighter navy for decoration
NAVY_LIGHTER = "#16377D"
BLUE = "#2F6BFF"          # primary blue
BLUE_DARK = "#2459DB"     # primary blue when hovered
BLUE_DARKER = "#1B49B8"   # primary blue when pressed
SOFT_BLUE = "#EAF0FF"     # soft blue backgrounds
SOFT_BLUE_DARK = "#D6E3FF"
LIGHT_BLUE_TEXT = "#8FB0FF"
WHITE = "#FFFFFF"
LIGHT_GREY = "#F2F5FA"    # page background
BORDER = "#DCE3EF"        # subtle borders
MUTED = "#6B7A99"         # secondary text
ERROR = "#D64550"         # friendly red for validation messages
PLACEHOLDER_ON_NAVY = "#6F8AC4"

FONT_CHOICES = ["Segoe UI", "SF Pro Display", "Helvetica Neue", "Inter",
                "Calibri", "Arial", "DejaVu Sans"]

DESIGN_WIDTH = 700     # window size the layout was designed for (in pixels at 100%)
DESIGN_HEIGHT = 720
SCALE = 1.0            # set in main(): 1.0 on a normal screen, bigger on high-DPI screens
FONTS = {}             # font name -> tkinter Font object, filled by build_fonts()


def hex_to_rgb(colour):
    colour = colour.lstrip("#")
    return int(colour[0:2], 16), int(colour[2:4], 16), int(colour[4:6], 16)


def mix(colour_a, colour_b, amount):
    """Blend two colours: amount 0 gives colour_a, amount 1 gives colour_b."""
    amount = max(0.0, min(1.0, amount))
    r1, g1, b1 = hex_to_rgb(colour_a)
    r2, g2, b2 = hex_to_rgb(colour_b)
    return "#%02x%02x%02x" % (int(round(r1 + (r2 - r1) * amount)),
                              int(round(g1 + (g2 - g1) * amount)),
                              int(round(b1 + (b2 - b1) * amount)))


def px(number):
    """Scale a design measurement (pixels) for this screen."""
    return int(round(number * SCALE))


def pick_font_family():
    """Use the first nice font that is installed, otherwise a safe default."""
    installed = set(tkfont.families())
    for name in FONT_CHOICES:
        if name in installed:
            return name
    return "Helvetica"


def build_fonts():
    """Create every font once.  (Fonts must be kept alive, so they live in FONTS.)"""
    family = pick_font_family()

    def make(size, bold=False):
        return tkfont.Font(family=family, size=-max(10, px(size)),
                           weight="bold" if bold else "normal")

    FONTS["title"] = make(21, True)
    FONTS["icon"] = make(19, True)
    FONTS["tag"] = make(10, True)
    FONTS["label"] = make(11, True)
    FONTS["input"] = make(24, True)
    FONTS["code_small"] = make(14, True)
    FONTS["combo"] = make(15)
    FONTS["button"] = make(15, True)
    FONTS["result"] = make(44, True)
    FONTS["code"] = make(20, True)
    FONTS["rate"] = make(13)
    FONTS["note"] = make(11)
    FONTS["error"] = make(12, True)
    FONTS["footer"] = make(11)


def rounded_points(x1, y1, x2, y2, radius):
    """Corner points for a rounded rectangle (draw with smooth=True)."""
    r = radius
    return [x1 + r, y1, x1 + r, y1, x2 - r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
            x2, y1 + r, x2, y2 - r, x2, y2 - r, x2, y2, x2 - r, y2, x2 - r, y2,
            x1 + r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y2 - r, x1, y1 + r,
            x1, y1 + r, x1, y1]


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
        pass   # not important - the app still works


# ======================================================================
# 4. CUSTOM WIDGETS (these give the modern, rounded look)
# ======================================================================

class RoundedFrame(tk.Canvas):
    """
    A frame with rounded corners, a border and an optional soft shadow.
    Put your widgets inside `.inner`.  It sizes itself to fit what is inside.
    """

    def __init__(self, parent, fill, outline, radius, pad_x, pad_y, page_bg,
                 border_width=1, shadow=0, **options):
        tk.Canvas.__init__(self, parent, bg=page_bg, highlightthickness=0, bd=0, **options)
        self.fill = fill
        self.outline = outline
        self.radius = radius
        self.pad_x = pad_x
        self.pad_y = pad_y
        self.page_bg = page_bg
        self.border_width = border_width
        self.shadow = shadow
        self.shape = None

        self.inner = tk.Frame(self, bg=fill)
        self.window_id = self.create_window(shadow + pad_x, pad_y, window=self.inner, anchor="nw")
        self.bind("<Configure>", self._on_canvas_configure)
        self.inner.bind("<Configure>", self._on_inner_configure)

    def _on_canvas_configure(self, event):
        # Make the inner frame as wide as the card (minus padding), then redraw.
        inner_width = max(1, event.width - 2 * (self.shadow + self.pad_x))
        self.itemconfigure(self.window_id, width=inner_width)
        self._draw(event.width, event.height)

    def _on_inner_configure(self, _event):
        # Grow or shrink the card so it always fits its content.
        wanted = self.inner.winfo_reqheight() + 2 * self.pad_y + self.shadow
        if int(float(self.cget("height"))) != wanted:
            self.configure(height=wanted)

    def _draw(self, width, height):
        self.delete("shape")
        half = self.border_width / 2.0
        x1, y1 = self.shadow + half, half
        x2, y2 = width - self.shadow - half, height - self.shadow - half
        if x2 - x1 < 4 or y2 - y1 < 4:
            return
        radius = min(self.radius, (x2 - x1) / 2.0, (y2 - y1) / 2.0)

        # Soft shadow: a few slightly larger, very light shapes behind the card.
        for layer in range(self.shadow, 0, -1):
            strength = 0.05 + 0.07 * (self.shadow - layer) / max(1, self.shadow - 1)
            self.create_polygon(
                rounded_points(x1 - layer * 0.8, y1 + layer, x2 + layer * 0.8, y2 + layer, radius),
                smooth=True, fill=mix(self.page_bg, "#5B6F99", strength), outline="", tags="shape")

        outline = self.outline if self.border_width > 0 else self.fill
        self.create_polygon(rounded_points(x1, y1, x2, y2, radius), smooth=True,
                            fill=self.fill, outline=outline,
                            width=max(1, self.border_width), tags=("shape", "card"))
        self.tag_lower("shape")

    def set_outline(self, colour, width=None):
        """Change the border colour (used for focus and error highlights)."""
        self.outline = colour
        if width is not None:
            self.border_width = width
        self._draw(self.winfo_width(), self.winfo_height())


class FlowButton(tk.Canvas):
    """A rounded button with hover and pressed colours."""

    STYLES = {
        "primary": {"fill": BLUE, "hover": BLUE_DARK, "press": BLUE_DARKER,
                    "text": WHITE, "outline": BLUE},
        "secondary": {"fill": WHITE, "hover": SOFT_BLUE, "press": SOFT_BLUE_DARK,
                      "text": NAVY, "outline": BORDER},
    }

    def __init__(self, parent, text, command, style, height, page_bg, **options):
        tk.Canvas.__init__(self, parent, height=height, bg=page_bg, highlightthickness=0,
                           bd=0, cursor="hand2", **options)
        self.text = text
        self.command = command
        self.look = self.STYLES[style]
        self.state = "normal"          # "normal", "hover" or "press"
        self.bind("<Configure>", lambda event: self.redraw())
        self.bind("<Enter>", lambda event: self.set_state("hover"))
        self.bind("<Leave>", lambda event: self.set_state("normal"))
        self.bind("<ButtonPress-1>", lambda event: self.set_state("press"))
        self.bind("<ButtonRelease-1>", self.on_release)

    def set_state(self, state):
        self.state = state
        self.redraw()

    def on_release(self, event):
        inside = 0 <= event.x <= self.winfo_width() and 0 <= event.y <= self.winfo_height()
        self.set_state("hover" if inside else "normal")
        if inside:
            self.command()

    def redraw(self):
        self.delete("all")
        width, height = self.winfo_width(), self.winfo_height()
        if width < 10 or height < 10:
            return
        colour = {"normal": self.look["fill"], "hover": self.look["hover"],
                  "press": self.look["press"]}[self.state]
        self.create_polygon(rounded_points(1, 1, width - 1, height - 1, px(14)), smooth=True,
                            fill=colour, outline=self.look["outline"] if self.state == "normal"
                            else colour, width=1)
        self.create_text(width / 2.0, height / 2.0, text=self.text, font=FONTS["button"],
                         fill=self.look["text"])


class SwapButton(tk.Canvas):
    """A round button with two arrows, used to swap the two currencies."""

    def __init__(self, parent, command, page_bg):
        size = px(46)
        tk.Canvas.__init__(self, parent, width=size, height=size, bg=page_bg,
                           highlightthickness=0, bd=0, cursor="hand2")
        self.command = command
        self.size = size
        self.hover = False
        self.redraw()
        self.bind("<Enter>", lambda event: self.set_hover(True))
        self.bind("<Leave>", lambda event: self.set_hover(False))
        self.bind("<ButtonRelease-1>", lambda event: self.command())

    def set_hover(self, hover):
        self.hover = hover
        self.redraw()

    def redraw(self):
        self.delete("all")
        s = self.size
        fill = SOFT_BLUE if self.hover else WHITE
        outline = BLUE if self.hover else BORDER
        self.create_oval(2, 2, s - 2, s - 2, fill=fill, outline=outline, width=1)
        arm = s * 0.22
        centre = s / 2.0
        # upper arrow points right, lower arrow points left
        self.create_line(centre - arm, centre - s * 0.08, centre + arm, centre - s * 0.08,
                         fill=BLUE, width=2, arrow="last", arrowshape=(7, 8, 3), capstyle="round")
        self.create_line(centre + arm, centre + s * 0.12, centre - arm, centre + s * 0.12,
                         fill=BLUE, width=2, arrow="last", arrowshape=(7, 8, 3), capstyle="round")


class HeaderBar(tk.Canvas):
    """The navy header with the small currency icon and the app name."""

    def __init__(self, parent, height):
        tk.Canvas.__init__(self, parent, height=height, bg=NAVY, highlightthickness=0, bd=0)
        self.bind("<Configure>", lambda event: self.redraw())

    def redraw(self):
        self.delete("all")
        width, height = self.winfo_width(), self.winfo_height()
        self.create_rectangle(0, 0, width, height, fill=NAVY, outline="")
        # Subtle decorative circles on the right-hand side.
        self.create_oval(width - px(230), -px(130), width + px(50), px(120),
                         fill=NAVY_LIGHT, outline="")
        self.create_oval(width - px(120), px(8), width + px(100), px(190),
                         fill=NAVY_LIGHTER, outline="")

        centre_y = height / 2.0
        icon_x, radius = px(40), px(20)
        self.create_oval(icon_x - radius, centre_y - radius, icon_x + radius, centre_y + radius,
                         fill=BLUE, outline="")
        self.create_text(icon_x, centre_y - 1, text="$", font=FONTS["icon"], fill=WHITE)

        text_x = icon_x + radius + px(14)
        self.create_text(text_x, centre_y, text="Currency", anchor="w",
                         font=FONTS["title"], fill=WHITE)
        self.create_text(text_x + FONTS["title"].measure("Currency"), centre_y, text="Flow",
                         anchor="w", font=FONTS["title"], fill=LIGHT_BLUE_TEXT)
        self.create_text(width - px(32), centre_y, text="SAMPLE RATES", anchor="e",
                         font=FONTS["tag"], fill=LIGHT_BLUE_TEXT)


# ======================================================================
# 5. THE APPLICATION WINDOW
# ======================================================================

class CurrencyFlowApp:
    """Builds the window and connects the buttons to the conversion logic."""

    def __init__(self, root):
        self.root = root
        self.rates = RATES_PER_BASE
        self.result_visible = False     # True once a conversion is on screen
        self.count_job = None           # timer id of the number count-up animation
        self.has_error = False

        # Drop-down text looks like "USD - US Dollar"; the code is its first 3 letters.
        self.currency_choices = ["%s - %s" % (code, CURRENCY_NAMES[code]) for code in DISPLAY_ORDER]
        self.choice_for_code = {code: choice for code, choice in zip(DISPLAY_ORDER, self.currency_choices)}

        root.title(APP_NAME)
        root.configure(bg=LIGHT_GREY)
        self.build_styles()
        self.build_layout()
        self.centre_window()
        self.bind_keys()
        self.amount_entry.focus_set()

    # ---------------------------- set-up ----------------------------

    def centre_window(self):
        """Pick a window size that fits this screen and place it in the middle."""
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        width = min(px(DESIGN_WIDTH), int(screen_w * 0.94))
        height = min(px(DESIGN_HEIGHT), int(screen_h * 0.92))
        x = (screen_w - width) // 2
        y = max(0, (screen_h - height) // 2 - px(16))
        self.root.geometry("%dx%d+%d+%d" % (width, height, x, y))
        self.root.minsize(min(px(600), width), min(px(660), height))

    def build_styles(self):
        """Style the ttk drop-downs so they match the rest of the design."""
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Flow.TCombobox", fieldbackground=WHITE, background=WHITE,
                        foreground=NAVY, bordercolor=WHITE, lightcolor=WHITE, darkcolor=WHITE,
                        arrowcolor=BLUE, arrowsize=px(18), padding=(px(8), px(8)),
                        relief="flat", selectbackground=WHITE, selectforeground=NAVY)
        style.map("Flow.TCombobox",
                  fieldbackground=[("readonly", WHITE)],
                  background=[("active", SOFT_BLUE), ("readonly", WHITE)],
                  foreground=[("readonly", NAVY)],
                  selectbackground=[("readonly", WHITE)],
                  selectforeground=[("readonly", NAVY)],
                  bordercolor=[("focus", WHITE)], lightcolor=[("focus", WHITE)],
                  darkcolor=[("focus", WHITE)], arrowcolor=[("active", BLUE_DARK)])
        # The pop-up list of the drop-down is a plain Tk listbox; style it too.
        self.root.option_add("*TCombobox*Listbox.background", WHITE)
        self.root.option_add("*TCombobox*Listbox.foreground", NAVY)
        self.root.option_add("*TCombobox*Listbox.selectBackground", SOFT_BLUE_DARK)
        self.root.option_add("*TCombobox*Listbox.selectForeground", NAVY)
        self.root.option_add("*TCombobox*Listbox.font", FONTS["combo"])
        self.root.option_add("*TCombobox*Listbox.relief", "flat")

    def bind_keys(self):
        """Enter converts, Escape clears."""
        self.root.bind("<Return>", lambda event: self.on_convert())
        self.root.bind("<KP_Enter>", lambda event: self.on_convert())
        self.root.bind("<Escape>", lambda event: self.on_clear())

    # ---------------------------- layout ----------------------------

    def build_layout(self):
        """Header on top, footer at the bottom, the converter card in the middle."""
        self.header = HeaderBar(self.root, height=px(76))
        self.header.pack(side="top", fill="x")

        footer = tk.Frame(self.root, bg=LIGHT_GREY)
        footer.pack(side="bottom", fill="x")
        tk.Frame(footer, height=1, bg=BORDER).pack(fill="x")
        tk.Label(footer, text="CurrencyFlow • Student Project • Built by " + AUTHOR_NAME,
                 font=FONTS["footer"],
                 fg=MUTED, bg=LIGHT_GREY).pack(pady=px(11))

        self.body = tk.Frame(self.root, bg=LIGHT_GREY)
        self.body.pack(side="top", fill="both", expand=True)
        self.card = RoundedFrame(self.body, fill=WHITE, outline=BORDER, radius=px(24),
                                 pad_x=px(30), pad_y=px(26), page_bg=LIGHT_GREY,
                                 shadow=px(6), width=px(580))
        self.card.pack(expand=True, pady=px(10))
        self.body.bind("<Configure>", self.on_body_resize)
        self.build_card(self.card.inner)

    def on_body_resize(self, event):
        """Keep the card centred and never wider than the window."""
        self.card.configure(width=min(px(580), event.width - px(40)))

    def build_card(self, inner):
        """All the controls inside the white converter card."""
        inner.columnconfigure(0, weight=1)
        inner.columnconfigure(1, weight=0)
        inner.columnconfigure(2, weight=1)

        # --- amount ---
        tk.Label(inner, text="AMOUNT", font=FONTS["label"], fg=MUTED, bg=WHITE,
                 anchor="w").grid(row=0, column=0, columnspan=3, sticky="w")
        self.amount_box = RoundedFrame(inner, fill=WHITE, outline=BORDER, radius=px(14),
                                       pad_x=px(16), pad_y=px(10), page_bg=WHITE)
        self.amount_box.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(px(6), px(16)))
        self.amount_var = tk.StringVar()
        self.amount_entry = tk.Entry(self.amount_box.inner, textvariable=self.amount_var,
                                     font=FONTS["input"], relief="flat", bd=0,
                                     highlightthickness=0, bg=WHITE, fg=NAVY,
                                     insertbackground=BLUE, selectbackground=SOFT_BLUE_DARK,
                                     selectforeground=NAVY)
        self.amount_entry.pack(side="left", fill="x", expand=True)
        self.amount_code_label = tk.Label(self.amount_box.inner, text="USD", font=FONTS["code_small"],
                                          fg=BLUE, bg=WHITE)
        self.amount_code_label.pack(side="right", padx=(px(10), 0))
        self.amount_entry.bind("<FocusIn>", lambda event: self.refresh_amount_outline(True))
        self.amount_entry.bind("<FocusOut>", lambda event: self.refresh_amount_outline(False))
        self.amount_var.trace_add("write", lambda *args: self.clear_error())

        # --- from / swap / to ---
        tk.Label(inner, text="FROM", font=FONTS["label"], fg=MUTED, bg=WHITE,
                 anchor="w").grid(row=2, column=0, sticky="w")
        tk.Label(inner, text="TO", font=FONTS["label"], fg=MUTED, bg=WHITE,
                 anchor="w").grid(row=2, column=2, sticky="w")

        self.from_var = tk.StringVar(value=self.choice_for_code["USD"])
        self.to_var = tk.StringVar(value=self.choice_for_code["NGN"])
        self.from_box, self.from_combo = self.make_currency_picker(inner, self.from_var)
        self.to_box, self.to_combo = self.make_currency_picker(inner, self.to_var)
        self.from_box.grid(row=3, column=0, sticky="ew", pady=(px(6), 0))
        self.to_box.grid(row=3, column=2, sticky="ew", pady=(px(6), 0))
        SwapButton(inner, self.on_swap, WHITE).grid(row=3, column=1, padx=px(12), pady=(px(6), 0))

        # --- validation message (always takes one line of space so nothing jumps) ---
        self.status_label = tk.Label(inner, text="", font=FONTS["error"], fg=ERROR, bg=WHITE,
                                     anchor="w", justify="left")
        self.status_label.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(px(8), px(8)))

        # --- buttons ---
        button_row = tk.Frame(inner, bg=WHITE)
        button_row.grid(row=5, column=0, columnspan=3, sticky="ew", pady=(0, px(18)))
        button_row.columnconfigure(0, weight=1)
        self.convert_button = FlowButton(button_row, "Convert", self.on_convert, "primary",
                                         px(52), WHITE)
        self.convert_button.grid(row=0, column=0, sticky="ew")
        self.clear_button = FlowButton(button_row, "Clear", self.on_clear, "secondary",
                                       px(52), WHITE, width=px(120))
        self.clear_button.grid(row=0, column=1, padx=(px(12), 0))

        # --- result card (deep navy, the visual focus) ---
        self.result_box = RoundedFrame(inner, fill=NAVY, outline=NAVY, radius=px(20),
                                       pad_x=px(24), pad_y=px(16), page_bg=WHITE, border_width=0)
        self.result_box.grid(row=6, column=0, columnspan=3, sticky="ew")
        result_inner = self.result_box.inner
        self.result_caption = tk.Label(result_inner, text="CONVERTED AMOUNT", font=FONTS["tag"],
                                       fg=LIGHT_BLUE_TEXT, bg=NAVY, anchor="w")
        self.result_caption.pack(fill="x")
        self.result_row = tk.Frame(result_inner, bg=NAVY)
        self.result_row.pack(fill="x", pady=(px(2), 0))
        self.result_amount = tk.Label(self.result_row, text="0.00", font=FONTS["result"],
                                      fg=PLACEHOLDER_ON_NAVY, bg=NAVY)
        self.result_amount.pack(side="left")
        self.result_code = tk.Label(self.result_row, text="NGN", font=FONTS["code"],
                                    fg=LIGHT_BLUE_TEXT, bg=NAVY)
        self.result_code.pack(side="left", padx=(px(10), 0), anchor="s", pady=(0, px(8)))
        self.rate_label = tk.Label(result_inner, text="Enter an amount and press Convert.",
                                   font=FONTS["rate"], fg=LIGHT_BLUE_TEXT, bg=NAVY, anchor="w")
        self.rate_label.pack(fill="x")
        self.result_row.bind("<Configure>", lambda event: self.fit_result_font())

        # --- honest note about the rates ---
        tk.Frame(inner, height=1, bg=BORDER).grid(row=7, column=0, columnspan=3,
                                                   sticky="ew", pady=(px(18), px(10)))
        self.note_label = tk.Label(inner, text="Sample rates for demonstration only. They are "
                                   "illustrative and are not live market rates.",
                                   font=FONTS["note"], fg=MUTED, bg=WHITE, anchor="w",
                                   justify="left")
        self.note_label.grid(row=8, column=0, columnspan=3, sticky="ew")
        inner.bind("<Configure>", self.on_card_resize, add="+")

        self.update_currency_labels()

    def make_currency_picker(self, parent, variable):
        """A rounded box containing a read-only drop-down of currencies."""
        box = RoundedFrame(parent, fill=WHITE, outline=BORDER, radius=px(14),
                           pad_x=px(8), pad_y=px(4), page_bg=WHITE)
        combo = ttk.Combobox(box.inner, textvariable=variable, values=self.currency_choices,
                             state="readonly", style="Flow.TCombobox", font=FONTS["combo"],
                             width=14)
        combo.pack(fill="x", expand=True)
        combo.bind("<<ComboboxSelected>>", self.on_currency_changed)
        combo.bind("<FocusIn>", lambda event: box.set_outline(BLUE, 2))
        combo.bind("<FocusOut>", lambda event: box.set_outline(BORDER, 1))
        return box, combo

    def on_card_resize(self, event):
        """Let the small note text wrap when the card is narrow."""
        self.note_label.configure(wraplength=max(px(200), event.width))

    # ---------------------------- helpers ----------------------------

    @staticmethod
    def code_of(choice):
        """'USD - US Dollar'  ->  'USD'"""
        return choice[:3]

    def refresh_amount_outline(self, focused):
        """Border colour of the amount box: red on error, blue when focused, grey otherwise."""
        if self.has_error:
            self.amount_box.set_outline(ERROR, 2)
        elif focused:
            self.amount_box.set_outline(BLUE, 2)
        else:
            self.amount_box.set_outline(BORDER, 1)

    def show_error(self, message):
        self.has_error = True
        self.status_label.configure(text=message)
        self.refresh_amount_outline(self.root.focus_get() is self.amount_entry)

    def clear_error(self):
        if self.has_error or self.status_label.cget("text"):
            self.has_error = False
            self.status_label.configure(text="")
            self.refresh_amount_outline(self.root.focus_get() is self.amount_entry)

    def update_currency_labels(self):
        """Keep the small currency codes next to the amount and result in step with the drop-downs."""
        self.amount_code_label.configure(text=self.code_of(self.from_var.get()))
        if not self.result_visible:
            self.result_code.configure(text=self.code_of(self.to_var.get()))

    def fit_result_font(self):
        """Shrink the big number if it is too wide, so it never gets cut off."""
        available = self.result_row.winfo_width() - self.result_code.winfo_reqwidth() - px(16)
        if available < px(80):
            return
        text = self.result_amount.cget("text")
        size = 44
        while size > 20:
            FONTS["result"].configure(size=-max(10, px(size)))
            if FONTS["result"].measure(text) <= available:
                break
            size -= 2

    # ---------------------------- actions ----------------------------

    def on_convert(self):
        """Validate the input, convert, and show the result."""
        self.clear_error()
        try:
            amount = parse_amount(self.amount_var.get())
        except AmountError as error:
            self.show_error(str(error))
            return

        from_code = self.code_of(self.from_var.get())
        to_code = self.code_of(self.to_var.get())
        try:
            exact_result = convert(amount, from_code, to_code, self.rates)
            unit_rate = convert(Decimal(1), from_code, to_code, self.rates)
        except ValueError as error:
            self.show_error(str(error))
            return

        result = round_money(exact_result)
        self.result_visible = True
        self.result_caption.configure(text="%s %s EQUALS" % (format_money(amount), from_code))
        self.result_code.configure(text=to_code)
        self.result_amount.configure(fg=WHITE)
        self.rate_label.configure(text="1 %s = %s %s" % (from_code, format_rate(unit_rate), to_code))
        self.animate_result(result)

    def animate_result(self, target):
        """Count the number up to the answer in a quick, smooth animation."""
        if self.count_job is not None:
            self.root.after_cancel(self.count_job)
            self.count_job = None
        steps = 14

        def step(number):
            fraction = number / float(steps)
            eased = 1 - (1 - fraction) ** 3            # fast start, gentle finish
            shown = target if number == steps else round_money(target * Decimal(str(eased)))
            self.result_amount.configure(text=format_money(shown))
            self.fit_result_font()
            if number < steps:
                self.count_job = self.root.after(22, lambda: step(number + 1))
            else:
                self.count_job = None

        step(1)

    def reset_result(self):
        """Put the result card back to its empty state."""
        if self.count_job is not None:
            self.root.after_cancel(self.count_job)
            self.count_job = None
        self.result_visible = False
        self.result_caption.configure(text="CONVERTED AMOUNT")
        self.result_amount.configure(text="0.00", fg=PLACEHOLDER_ON_NAVY)
        self.rate_label.configure(text="Enter an amount and press Convert.")
        self.result_code.configure(text=self.code_of(self.to_var.get()))
        self.fit_result_font()

    def on_clear(self):
        """Empty the amount, any message and the result."""
        self.amount_var.set("")
        self.clear_error()
        self.reset_result()
        self.amount_entry.focus_set()

    def on_swap(self):
        """Swap the FROM and TO currencies."""
        from_value, to_value = self.from_var.get(), self.to_var.get()
        self.from_var.set(to_value)
        self.to_var.set(from_value)
        self.on_currency_changed()

    def on_currency_changed(self, _event=None):
        """After any currency change, refresh the labels and re-convert if a result is showing."""
        self.from_combo.selection_clear()
        self.to_combo.selection_clear()
        self.update_currency_labels()
        if self.result_visible:
            self.on_convert()


# ======================================================================
# 6. SELF-TEST AND START-UP
# ======================================================================

def run_self_test():
    """
    Check the conversion maths and the validation without opening a window.
    Run with:  python currency_converter.py --test
    """
    def money(amount, source, target):
        return format_money(convert(Decimal(amount), source, target))

    checks = [
        ("1 USD -> NGN", money("1", "USD", "NGN"), "1,500.00"),
        ("1500 NGN -> USD", money("1500", "NGN", "USD"), "1.00"),
        ("100 USD -> GBP", money("100", "USD", "GBP"), "79.00"),
        ("100 USD -> EUR", money("100", "USD", "EUR"), "92.00"),
        ("100 GBP -> EUR (via USD)", money("100", "GBP", "EUR"), "116.46"),
        ("100 EUR -> NGN (via USD)", money("100", "EUR", "NGN"), "163,043.48"),
        ("250 NGN -> NGN (same currency)", money("250", "NGN", "NGN"), "250.00"),
        ("0.005 USD -> USD rounds half up", money("0.005", "USD", "USD"), "0.01"),
    ]
    # Converting there and back should return (almost exactly) the starting amount.
    start = Decimal("1234.56")
    back = round_money(convert(convert(start, "NGN", "GBP"), "GBP", "NGN"))
    checks.append(("round trip NGN -> GBP -> NGN", str(back), str(start)))
    # Every pair of currencies must agree: A->B multiplied by B->A is 1.
    for a in RATES_PER_BASE:
        for b in RATES_PER_BASE:
            product = convert(Decimal(1), a, b) * convert(Decimal(1), b, a)
            checks.append(("rate %s->%s x %s->%s = 1" % (a, b, b, a),
                           str(round(product, 10)), "1.0000000000"))

    # Validation messages.
    for text, expected in [("", "enter an amount"), ("abc", "doesn't look like a number"),
                           ("0", "greater than zero"), ("-5", "cannot be negative"),
                           ("NaN", "doesn't look like a number"), ("1e30", "too large")]:
        try:
            parse_amount(text)
            actual = "no error"
        except AmountError as error:
            actual = str(error)
        checks.append(("validation of %r" % text, expected in actual and expected or actual, expected))
    checks.append(("amount with commas", str(parse_amount("1,500.50")), "1500.50"))
    checks.append(("amount with spaces", str(parse_amount("  250 ")), "250"))

    failures = 0
    for name, actual, expected in checks:
        ok = (actual == expected)
        failures += 0 if ok else 1
        print(("PASS  " if ok else "FAIL  ") + name + ("" if ok else "   got %s, expected %s" % (actual, expected)))
    print("\n%d checks, %d failed." % (len(checks), failures))
    return failures == 0


def main():
    global SCALE
    if "--test" in sys.argv:
        sys.exit(0 if run_self_test() else 1)

    enable_sharp_text_on_windows()
    root = tk.Tk()
    # Work out how big to draw things: bigger on high-DPI screens, but never so big
    # that the window would not fit on a small laptop screen.
    dpi_scale = max(1.0, root.winfo_fpixels("1i") / 96.0)
    fit_scale = root.winfo_screenheight() * 0.92 / DESIGN_HEIGHT
    SCALE = max(0.85, min(dpi_scale, fit_scale))
    build_fonts()
    CurrencyFlowApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
