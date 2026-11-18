"""
Scientific Calculator using Python Tkinter  (Dark card + blue theme)
Run:  python scientific_calculator.py
No extra libraries needed (tkinter and math come with Python).

Layout: the keypad uses Tkinter's real GRID geometry manager.
Every button is a small Canvas widget placed with
    button.grid(row=..., column=..., rowspan=..., columnspan=...)
inside Frame widgets (the "+" spans 2 rows, the "0" spans 2 columns).
The background, dark card and display text are drawn on one big Canvas.

Trigonometric functions support DEG and RAD modes (DEG is the default).
Standard angles show EXACT values like a trigonometric table:
    sin(30) = 1/2     cos(45) = 1/√2     tan(60) = √3     tan(90) = Undefined

History: click the "History" pill (top-left of the card) to open a panel
with your previous calculations. Click a row to load it again, "Clear" to
empty the list, and use the mouse wheel to scroll.

The DEG/RAD pill at the top-right switches the trigonometric angle mode.
If an answer is on the screen, pressing the pill converts ONLY the result
(the expression line stays as you typed it):
        90 =  then RAD  ->  1.5707963268     and then DEG  ->  90
"""

import math
import re
import tkinter as tk


# ---------------------------------------------------------------
# 1. Math functions allowed inside an expression.
#    Trigonometric functions work in DEGREES (sin(90) = 1).
# ---------------------------------------------------------------
class UndefinedError(Exception):
    """Raised when a trig function is undefined (e.g. tan(90))."""


# The calculator starts in degree mode. The DEG/RAD button switches modes.
ANGLE = {"mode": "DEG"}


def to_deg(x):
    """Convert an entered angle to degrees for the internal trig functions."""
    return x if ANGLE["mode"] == "DEG" else math.degrees(x)


def sin_d(x):
    return math.sin(math.radians(x))


def cos_d(x):
    return math.cos(math.radians(x))


def tan_d(x):
    if abs(x % 180 - 90) < 1e-9:
        raise UndefinedError
    return math.tan(math.radians(x))


def sec_d(x):
    if abs(x % 180 - 90) < 1e-9:
        raise UndefinedError
    return 1 / math.cos(math.radians(x))


def cosec_d(x):
    r = x % 180
    if r < 1e-9 or 180 - r < 1e-9:
        raise UndefinedError
    return 1 / math.sin(math.radians(x))


def cot_d(x):
    r = x % 180
    if r < 1e-9 or 180 - r < 1e-9:
        raise UndefinedError
    return math.cos(math.radians(x)) / math.sin(math.radians(x))


DEG_FUNCS = {
    "sin": sin_d, "cos": cos_d, "tan": tan_d,
    "sec": sec_d, "cosec": cosec_d, "cot": cot_d,
}


def make_trig(name):
    """Make a trig function that respects the selected angle mode."""
    func = DEG_FUNCS[name]
    return lambda x: func(to_deg(x))


SAFE_NAMES = {
    "sin": make_trig("sin"), "cos": make_trig("cos"),
    "tan": make_trig("tan"), "sec": make_trig("sec"),
    "cosec": make_trig("cosec"), "cot": make_trig("cot"),
    "sqrt": math.sqrt,
    "log": math.log10,
    "ln": math.log,
    "pi": math.pi,
    "e": math.e,
}

# ---------------------------------------------------------------
# 2. Exact trigonometric table (values for the reference angle)
#    None means "Undefined".
# ---------------------------------------------------------------
TRIG_TABLE = {
    #          0°      30°      45°      60°      90°
    "sin":   {0: "0",  30: "1/2",   45: "1/√2", 60: "√3/2",  90: "1"},
    "cos":   {0: "1",  30: "√3/2",  45: "1/√2", 60: "1/2",   90: "0"},
    "tan":   {0: "0",  30: "1/√3",  45: "1",    60: "√3",    90: None},
    "sec":   {0: "1",  30: "2/√3",  45: "√2",   60: "2",     90: None},
    "cosec": {0: None, 30: "2",     45: "√2",   60: "2/√3",  90: "1"},
    "cot":   {0: None, 30: "√3",    45: "1",    60: "1/√3",  90: "0"},
}

CALL_PATTERN = re.compile(r"^(sin|cos|tan|sec|cosec|cot)\((.*)\)$")


def exact_value(name, angle):
    """Exact text for a trig function at an angle in degrees.
    Returns e.g. '1/2', '-√3/2', 'Undefined', or None if the angle
    is not one of the standard angles."""
    ang = round(angle % 360, 9)
    if ang >= 360:
        ang = 0
    # reference angle (angle measured from the x-axis, 0 to 90)
    if ang <= 90:
        ref = ang
    elif ang <= 180:
        ref = 180 - ang
    elif ang <= 270:
        ref = ang - 180
    else:
        ref = 360 - ang
    if ref not in TRIG_TABLE[name]:
        return None
    value = TRIG_TABLE[name][ref]
    if value is None:
        return "Undefined"
    # the sign comes from the real value of the function
    if value != "0" and DEG_FUNCS[name](ang) < 0:
        return "-" + value
    return value


def exact_trig(expr):
    """If expr is exactly ONE trig call like sin(30), return its exact
    text. Otherwise return None (a normal decimal answer is used)."""
    match = CALL_PATTERN.match(expr)
    if not match:
        return None
    inner = match.group(2)
    depth = 0
    for ch in inner:                  # the first "(" must close at the end
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth < 0:
                return None
    if depth != 0:
        return None
    try:
        angle = eval(inner, {"__builtins__": {}}, SAFE_NAMES)
    except Exception:
        return None
    if not isinstance(angle, (int, float)):
        return None
    # The exact-value table is defined in degrees.
    return exact_value(match.group(1), to_deg(angle))


# ---------------------------------------------------------------
# 3. Sizes and colours
# ---------------------------------------------------------------
W, H = 360, 624                     # window size (keep both even)
CARD = (16, 16, 344, 608)           # dark card: x1, y1, x2, y2
CARD_R = 30                         # card corner radius
LEFT, COLW, GAP = 32, 68, 8         # first column x, button width, gap
PAD = GAP // 2                      # grid padding around every button
ROWH = 52                           # height of a main button
SMALL_H, SMALL_TOP = 30, 140        # small (scientific) buttons
MAIN_TOP = 300                      # y where the main buttons start
SHADOW = 4                          # extra pixels under a button for its shadow

# --- History ---
PANEL = (28, 134, 332, 292)         # history panel, covers the small buttons
HISTORY_MAX = 30                    # how many calculations to remember
HIST_ROWS = 5                       # rows visible at once

WHITE = "#ffffff"
PAGE = "#eaf2fb"                    # light page colour
BLUE = "#1f7ae6"                    # big circle colour
CARD_COLOR = "#151921"

# Button colours: (fill, text colour)
STYLE_SMALL = ("#1f2530", "#8294ad")
STYLE_NUMBER = ("#232a36", "#a9b8cf")
STYLE_GRAY = ("#4b515c", WHITE)
STYLE_OPERATOR = ("#0f66d9", WHITE)
STYLE_EQUALS = ("#1e90ff", WHITE)
STYLE_MODE = ("#1b3a66", "#7fb8ff")

ERRORS = ("Error", "Cannot divide by zero", "Undefined")


def blend(color1, color2, t):
    """Mix two hex colours. t=0 gives color1, t=1 gives color2."""
    r1, g1, b1 = (int(color1[i:i + 2], 16) for i in (1, 3, 5))
    r2, g2, b2 = (int(color2[i:i + 2], 16) for i in (1, 3, 5))
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    return f"#{r:02x}{g:02x}{b:02x}"


def bg_at(x, y):
    """Page colour at (x, y): light background with soft blue circles."""
    color = PAGE
    d = math.hypot(x - 70, y - 150)
    if d < 210:
        color = blend(color, BLUE, min(1.0, (1 - d / 210) * 2.4))
    d = math.hypot(x - 310, y - 560)
    if d < 130:
        color = blend(color, "#9cc6f5", (1 - d / 130) * 0.9)
    return color


def rounded_points(x1, y1, x2, y2, r):
    """Points of a rounded rectangle (used with smooth=True)."""
    return [
        x1 + r, y1, x1 + r, y1, x2 - r, y1, x2 - r, y1,
        x2, y1, x2, y1 + r, x2, y1 + r, x2, y2 - r, x2, y2 - r,
        x2, y2, x2 - r, y2, x2 - r, y2, x1 + r, y2, x1 + r, y2,
        x1, y2, x1, y2 - r, x1, y2 - r, x1, y1 + r, x1, y1 + r,
        x1, y1,
    ]


def pretty(text):
    """Add thousand separators: 12454 -> 12,454 (other text unchanged)."""
    try:
        if "e" in text.lower():
            return text
        if "." in text:
            whole, fraction = text.split(".")
            return f"{int(whole):,}.{fraction}"
        return f"{int(text):,}"
    except ValueError:
        return text


def short(text, limit):
    """Cut long text and add … so it fits on one history row."""
    return text if len(text) <= limit else text[:limit - 1] + "…"


# ---------------------------------------------------------------
# 4. One rounded button = one small Canvas WIDGET.
#    It is placed on the keypad with .grid(row, column, ...).
#    Layers (bottom to top): shadow, body, ripple, shine, label.
#    On press: the body squishes and a water ripple spreads out.
# ---------------------------------------------------------------
class GlassButton(tk.Canvas):
    FRAMES = 16     # animation steps
    DELAY = 14      # milliseconds between steps

    def __init__(self, parent, text, value, style, font, command,
                 width=COLW, height=ROWH, radius=14):
        super().__init__(parent, width=width, height=height + SHADOW,
                         bg=CARD_COLOR, highlightthickness=0, cursor="hand2")
        self.w, self.h = width, height
        self.radius = radius
        self.value = value
        self.command = command
        self.busy = False

        fill, text_color = style
        self.base = fill
        self.base_text = text_color
        self.normal = fill
        self.hover = blend(fill, WHITE, 0.12)
        self.edge = blend(fill, WHITE, 0.10)
        self.glow = blend(fill, WHITE, 0.38)

        # soft shadow under the button
        self.create_polygon(
            rounded_points(1, 3, width - 1, height + 2, radius),
            smooth=True, fill="#0b0e13", outline="")
        self.body = self.create_polygon(
            self.body_points(0), smooth=True, fill=self.normal,
            outline=self.edge, width=1)
        self.shine = self.create_polygon(
            self.shine_points(0), smooth=True,
            fill=blend(fill, WHITE, 0.06), outline="")
        self.label = self.create_text(
            width / 2, height / 2, text=text, fill=text_color, font=font)

        # each button handles its own mouse events
        self.bind("<Enter>", lambda e: self.set_hover(True))
        self.bind("<Leave>", lambda e: self.set_hover(False))
        self.bind("<ButtonPress-1>", lambda e: self.on_press())

    # ----- shapes (inset makes the button shrink a little when pressed)
    def body_points(self, inset):
        return rounded_points(inset, inset, self.w - inset, self.h - inset,
                              self.radius)

    def shine_points(self, inset):
        top = 3 + inset
        bottom = self.h * 0.46
        side = 6 + inset
        return rounded_points(side, top, self.w - side, bottom,
                              max(2, self.radius - 4))

    def set_label(self, text):
        self.itemconfig(self.label, text=text)

    def set_active(self, on):
        """Highlight the button (used by the History pill while open)."""
        fill = STYLE_OPERATOR[0] if on else self.base
        self.normal = fill
        self.hover = blend(fill, WHITE, 0.12)    # hover colour follows the new colour
        self.glow = blend(fill, WHITE, 0.38)     # ripple colour follows it too
        self.itemconfig(self.body, fill=self.normal)
        self.itemconfig(self.shine, fill=blend(fill, WHITE, 0.06))
        self.itemconfig(self.label, fill=WHITE if on else self.base_text)

    def set_hover(self, on):
        self.itemconfig(self.body, fill=self.hover if on else self.normal)
        self.itemconfig(
            self.shine, fill=blend(self.normal, WHITE, 0.16 if on else 0.06))

    def on_press(self):
        self.start_animation()
        self.command(self.value)

    # ----- press animation
    def start_animation(self):
        if not self.busy:
            self.busy = True
            self.animate(0)

    def animate(self, step):
        self.delete("ripple")
        if step > self.FRAMES:                     # animation finished
            self.coords(self.body, *self.body_points(0))
            self.coords(self.shine, *self.shine_points(0))
            self.busy = False
            return

        t = step / self.FRAMES                     # goes from 0 to 1
        inset = 2.5 * math.sin(math.pi * t)        # shrink, then spring back
        self.coords(self.body, *self.body_points(inset))
        self.coords(self.shine, *self.shine_points(inset))

        # ripple: an oval growing from the centre and fading away
        rx, ry = (self.w / 2 - 3) * t, (self.h / 2 - 3) * t
        cx, cy = self.w / 2, self.h / 2
        self.create_oval(cx - rx, cy - ry, cx + rx, cy + ry,
                         fill=blend(self.glow, self.hover, t), outline="",
                         tags="ripple")
        self.tag_raise(self.shine)                 # keep shine and text on top
        self.tag_raise(self.label)
        self.after(self.DELAY, self.animate, step + 1)


class Calculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Scientific Calculator")
        self.root.resizable(False, False)

        self.expression = ""      # what the user has typed so far
        self.result = "0"         # raw result (used for errors)
        self.by_value = {}        # value -> button (used by the keyboard)

        # --- DEG/RAD answer conversion ---
        self.last_value = None        # exact number of the last answer
        self.just_calculated = False  # True right after pressing "="
        self.last_typed = ""          # expression that produced the last answer

        # --- History ---
        self.history = []             # (expression, result), oldest first
        self.history_open = False
        self.history_offset = 0       # scroll position
        self.history_hits = []        # clickable rows, rebuilt on every draw
        self.clear_box = (0, 0, 0, 0)

        self.canvas = tk.Canvas(root, width=W, height=H, highlightthickness=0,
                                bg=PAGE)
        self.canvas.pack()

        self.bg_image = self.make_background()     # keep a reference!
        self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")

        self.create_card()
        self.create_display()
        self.create_buttons()
        self.create_history_panel()
        self.bind_events()

    # -----------------------------------------------------------
    # 5. Background image (painted at half size, then zoomed 2x)
    # -----------------------------------------------------------
    def make_background(self):
        small = tk.PhotoImage(width=W // 2, height=H // 2)
        rows = []
        for y in range(0, H, 2):
            row = " ".join(bg_at(x, y) for x in range(0, W, 2))
            rows.append("{" + row + "}")
        small.put(" ".join(rows))
        return small.zoom(2, 2)

    # -----------------------------------------------------------
    # 6. Dark rounded card with a soft shadow
    # -----------------------------------------------------------
    def create_card(self):
        x1, y1, x2, y2 = CARD
        for grow in (14, 10, 6, 3):                # layered soft shadow
            shade = blend(bg_at(W / 2, y2), "#0b1b33", 0.10 + (14 - grow) * 0.03)
            self.canvas.create_polygon(
                rounded_points(x1 - grow, y1 - grow + 8, x2 + grow,
                               y2 + grow + 8, CARD_R + grow),
                smooth=True, fill=shade, outline="")
        self.canvas.create_polygon(
            rounded_points(x1, y1, x2, y2, CARD_R), smooth=True,
            fill=CARD_COLOR, outline="#232b38", width=1)

    # -----------------------------------------------------------
    # 7. Display: expression line + big result line.
    #    Exact trig answers are drawn as a STACKED fraction
    #    (numerator, line, denominator) like a trig table.
    # -----------------------------------------------------------
    def create_display(self):
        c = self.canvas
        right = CARD[2] - 22
        self.expr_text = c.create_text(
            right, 58, anchor="e", text="", fill="#8a93a3",
            font=("Segoe UI", 12))
        self.result_text = c.create_text(
            right, 98, anchor="e", text="0", fill=WHITE,
            font=("Segoe UI", 32, "bold"))

        # fraction parts (hidden until needed)
        self.frac_eq = c.create_text(
            right, 99, anchor="e", text="=", fill=WHITE,
            font=("Segoe UI", 26, "bold"), state="hidden")
        self.frac_num = c.create_text(
            right, 83, text="", fill=WHITE,
            font=("Segoe UI", 17, "bold"), state="hidden")
        self.frac_bar = c.create_line(
            right - 30, 99, right, 99, fill=WHITE, width=2, state="hidden")
        self.frac_den = c.create_text(
            right, 115, text="", fill=WHITE,
            font=("Segoe UI", 17, "bold"), state="hidden")
        self.frac_items = [self.frac_eq, self.frac_num, self.frac_bar,
                           self.frac_den]

    def show_expression(self):
        text = self.expression
        if len(text) > 30:
            text = "…" + text[-29:]
        self.canvas.itemconfig(self.expr_text, text=text)

    def hide_fraction(self):
        for item in self.frac_items:
            self.canvas.itemconfig(item, state="hidden")
        self.canvas.itemconfig(self.result_text, state="normal")

    def show_fraction(self, text):
        """Draw text like '-√3/2' as a stacked fraction."""
        negative = text.startswith("-")
        numerator, denominator = text.lstrip("-").split("/")
        c = self.canvas
        right = CARD[2] - 22
        width = max(len(numerator), len(denominator)) * 12 + 10
        centre = right - width / 2

        c.itemconfig(self.result_text, state="hidden")
        c.coords(self.frac_bar, centre - width / 2, 99, centre + width / 2, 99)
        c.coords(self.frac_num, centre, 83)
        c.coords(self.frac_den, centre, 115)
        c.coords(self.frac_eq, right - width - 8, 99)
        c.itemconfig(self.frac_num, text=numerator)
        c.itemconfig(self.frac_den, text=denominator)
        c.itemconfig(self.frac_eq, text="=−" if negative else "=")
        for item in self.frac_items:
            c.itemconfig(item, state="normal")

    def show_result(self, text, calculated=False):
        self.result = text
        self.hide_fraction()
        shown = ("=" + pretty(text)) if calculated else text
        # smaller font for longer text so it always fits
        n = len(shown)
        size = 32 if n <= 9 else 26 if n <= 12 else 20 if n <= 16 else 15
        self.canvas.itemconfig(self.result_text, text=shown,
                               font=("Segoe UI", size, "bold"))

    def show_exact(self, text):
        """Show an exact trig answer such as 1/2, √3 or -1."""
        if "/" in text:
            self.result = text
            self.show_fraction(text)
        else:
            self.show_result(text, calculated=True)

    # -----------------------------------------------------------
    # 8. Buttons placed with Tkinter's GRID layout manager
    #    Three Frames (header, small keys, main keypad) sit on the card.
    #    Inside each Frame every button uses .grid(row, column, ...).
    # -----------------------------------------------------------
    def add_button(self, parent, label, value, style, font, row, column,
                   width=COLW, height=ROWH, radius=14, rowspan=1,
                   columnspan=1, sticky=None, pady=(0, PAD)):
        button = GlassButton(parent, label, value, style, font,
                             self.on_click, width, height, radius)
        button.grid(row=row, column=column, rowspan=rowspan,
                    columnspan=columnspan, padx=PAD, pady=pady, sticky=sticky)
        self.by_value[value] = button
        return button

    def create_buttons(self):
        S, N, G = STYLE_SMALL, STYLE_NUMBER, STYLE_GRAY
        O, E = STYLE_OPERATOR, STYLE_EQUALS
        pill_font = ("Segoe UI", 9, "bold")
        grid_w = 4 * (COLW + 2 * PAD)               # width of a 4-column grid

        # ---- header row: History pill (left) and DEG/RAD pill (right)
        header = tk.Frame(self.canvas, bg=CARD_COLOR)
        header.grid_columnconfigure(1, weight=1)    # empty middle column
        self.history_pill = self.add_button(
            header, "History", "HISTORY", S, pill_font, 0, 0,
            width=74, height=22, radius=11, sticky="w", pady=0)
        self.add_button(
            header, ANGLE["mode"], "MODE", STYLE_MODE, pill_font, 0, 2,
            width=54, height=22, radius=9, sticky="e", pady=0)
        self.canvas.create_window(LEFT - PAD, 24, anchor="nw", window=header,
                                  width=grid_w, height=28)

        # ---- small scientific buttons: 4 rows x 4 columns
        small_frame = tk.Frame(self.canvas, bg=CARD_COLOR)
        small = [
            [("sin", "sin("), ("cos", "cos("), ("tan", "tan("), ("π", "pi")],
            [("sec", "sec("), ("cosec", "cosec("), ("cot", "cot("), ("e", "e")],
            [("log", "log("), ("ln", "ln("), ("√", "sqrt("), ("x²", "**2")],
            [("xʸ", "^"), ("(", "("), (")", ")"), ("%", "%")],
        ]
        for r, row in enumerate(small):
            for c, (label, value) in enumerate(row):
                self.add_button(small_frame, label, value, S,
                                ("Segoe UI", 10, "bold"), r, c,
                                height=SMALL_H, radius=10)
        self.small_window = self.canvas.create_window(
            LEFT - PAD, SMALL_TOP, anchor="nw", window=small_frame,
            width=grid_w, height=4 * (SMALL_H + SHADOW + PAD))

        # ---- main keypad: 4 columns x 5 rows
        main_frame = tk.Frame(self.canvas, bg=CARD_COLOR)
        main = [
            [("AC", "CLEAR", G), ("⌫", "BACK", G), ("÷", "/", O), ("×", "*", O)],
            [("7", "7", N), ("8", "8", N), ("9", "9", N), ("−", "-", O)],
            [("4", "4", N), ("5", "5", N), ("6", "6", N)],
            [("1", "1", N), ("2", "2", N), ("3", "3", N)],
        ]
        for r, row in enumerate(main):
            for c, (label, value, style) in enumerate(row):
                size = 16 if label.isdigit() else 15
                self.add_button(main_frame, label, value, style,
                                ("Segoe UI", size, "bold"), r, c)

        # tall "+" spans 2 rows (rowspan=2) in the last column
        self.add_button(main_frame, "+", "+", O, ("Segoe UI", 18, "bold"),
                        2, 3, height=ROWH * 2 + GAP, rowspan=2)

        # last row: wide "0" spans 2 columns (columnspan=2), ".", "="
        self.add_button(main_frame, "0", "0", N, ("Segoe UI", 16, "bold"),
                        4, 0, width=COLW * 2 + GAP, columnspan=2)
        self.add_button(main_frame, ".", ".", N, ("Segoe UI", 16, "bold"), 4, 2)
        self.add_button(main_frame, "=", "=", E, ("Segoe UI", 20, "bold"), 4, 3)

        self.canvas.create_window(
            LEFT - PAD, MAIN_TOP, anchor="nw", window=main_frame,
            width=grid_w, height=5 * (ROWH + SHADOW + PAD))

    # -----------------------------------------------------------
    # 8b. History panel (its own Canvas widget, shown on top of the
    #     small buttons while it is open)
    # -----------------------------------------------------------
    def create_history_panel(self):
        x1, y1, x2, y2 = PANEL
        self.panel_w, self.panel_h = x2 - x1, y2 - y1
        self.panel = tk.Canvas(self.canvas, width=self.panel_w,
                               height=self.panel_h, bg=CARD_COLOR,
                               highlightthickness=0)
        self.panel.bind("<ButtonPress-1>", self.on_history_click)
        self.panel.bind("<MouseWheel>", self.on_wheel)    # Windows, macOS
        self.panel.bind("<Button-4>", self.on_wheel)      # Linux
        self.panel.bind("<Button-5>", self.on_wheel)
        self.panel_window = self.canvas.create_window(
            x1, y1, anchor="nw", window=self.panel, state="hidden")

    def add_history(self, expression, result):
        entry = (expression, result)
        if self.history and self.history[-1] == entry:
            return                                   # skip exact repeats
        self.history.append(entry)
        del self.history[:-HISTORY_MAX]              # keep only the newest
        self.history_offset = 0
        if self.history_open:
            self.draw_history()

    @staticmethod
    def in_box(x, y, box):
        return box[0] <= x <= box[2] and box[1] <= y <= box[3]

    def toggle_history(self):
        self.history_open = not self.history_open
        self.history_offset = 0
        on = self.history_open
        self.history_pill.set_active(on)
        # hide the small buttons while the panel covers their place
        self.canvas.itemconfig(self.small_window,
                               state="hidden" if on else "normal")
        self.canvas.itemconfig(self.panel_window,
                               state="normal" if on else "hidden")
        self.draw_history()

    def draw_history(self):
        p = self.panel
        p.delete("all")
        self.history_hits = []
        if not self.history_open:
            return
        w, h = self.panel_w, self.panel_h
        p.create_polygon(rounded_points(0, 0, w, h, 16), smooth=True,
                         fill="#10141b", outline="#2a3342")
        p.create_text(16, 16, anchor="w", text="History", fill="#8294ad",
                      font=("Segoe UI", 10, "bold"))
        self.clear_box = (w - 66, 5, w - 8, 27)
        p.create_text(w - 16, 16, anchor="e", text="Clear", fill="#5aa2ff",
                      font=("Segoe UI", 10, "bold"))
        if not self.history:
            p.create_text(w / 2, h / 2 + 10, text="No calculations yet",
                          fill="#5d6a80", font=("Segoe UI", 11))
            return
        newest_first = self.history[::-1]
        shown = newest_first[self.history_offset:
                             self.history_offset + HIST_ROWS]
        for i, (expression, result) in enumerate(shown):
            top = 34 + i * 24
            self.history_hits.append(
                ((8, top, w - 8, top + 22), expression, result))
            p.create_line(16, top - 1, w - 16, top - 1, fill="#1c222d")
            p.create_text(16, top + 11, anchor="w",
                          text=short(expression, 20), fill="#8a93a3",
                          font=("Segoe UI", 10))
            p.create_text(w - 16, top + 11, anchor="e",
                          text="= " + short(result, 12), fill=WHITE,
                          font=("Segoe UI", 11, "bold"))

    def on_history_click(self, event):
        x, y = event.x, event.y                      # inside the panel
        if self.in_box(x, y, self.clear_box):
            self.history.clear()
            self.history_offset = 0
            self.draw_history()
            return
        for box, expression, result in self.history_hits:
            if self.in_box(x, y, box):
                self.expression = expression          # editable again
                self.show_expression()
                self.show_exact(result)               # handles fractions too
                self.just_calculated = False          # not a fresh answer
                self.toggle_history()                 # close the panel
                return

    def on_wheel(self, event):
        if not self.history_open:
            return
        step = -1 if (event.delta > 0 or event.num == 4) else 1
        limit = max(0, len(self.history) - HIST_ROWS)
        self.history_offset = min(limit, max(0, self.history_offset + step))
        self.draw_history()

    # -----------------------------------------------------------
    # 9. Event handling: keyboard (each button handles its own mouse)
    # -----------------------------------------------------------
    def bind_events(self):
        self.root.bind("<Return>", lambda e: self.press("="))
        self.root.bind("<BackSpace>", lambda e: self.press("BACK"))
        self.root.bind("<Escape>", lambda e: self.press("CLEAR"))
        self.root.bind("<Key>", self.on_key)

    def on_key(self, event):
        if event.char and event.char in "0123456789.+-*/()^%":
            self.press(event.char)

    def press(self, value):
        """Used by the keyboard: animate the matching button, then click."""
        button = self.by_value.get(value)
        if button:
            button.start_animation()
        self.on_click(value)

    # -----------------------------------------------------------
    # 10. Every button click ends up here
    # -----------------------------------------------------------
    def on_click(self, value):
        if value == "CLEAR":
            self.clear()
        elif value == "BACK":
            self.backspace()
        elif value == "=":
            self.calculate()
        elif value == "MODE":
            self.toggle_mode()
        elif value == "HISTORY":
            self.toggle_history()
        else:
            # If the last result was an error message, start fresh
            if self.result in ERRORS:
                self.clear()
            self.just_calculated = False       # typing a new expression
            self.expression += value
            self.show_expression()

    def toggle_mode(self):
        """Switch between degree and radian input.
        If an answer is on the screen, convert ONLY that answer
        (the expression line is left exactly as it was)."""
        old_mode = ANGLE["mode"]
        ANGLE["mode"] = "RAD" if old_mode == "DEG" else "DEG"
        self.by_value["MODE"].set_label(ANGLE["mode"])

        if self.just_calculated and isinstance(self.last_value, (int, float)):
            if old_mode == "DEG":                  # DEG -> RAD
                value = math.radians(self.last_value)
            else:                                  # RAD -> DEG
                value = math.degrees(self.last_value)
            self.last_value = value                # keep the exact value
            shown = round(value, 10)
            if shown == int(shown):
                shown = int(shown)
            self.expression = str(shown)           # keeps chaining working
            self.show_result(str(shown), calculated=True)

    def clear(self):
        self.just_calculated = False
        self.last_value = None
        self.last_typed = ""
        self.expression = ""
        self.show_expression()
        self.show_result("0")

    def backspace(self):
        if self.just_calculated and self.last_typed:
            # right after "=": edit the expression that was calculated,
            # so the top line never jumps to the result number
            self.expression = self.last_typed[:-1]
            self.last_typed = ""
        else:
            self.expression = self.expression[:-1]
        self.just_calculated = False
        self.show_expression()

    # -----------------------------------------------------------
    # 11. Evaluate the expression and handle errors
    # -----------------------------------------------------------
    def calculate(self):
        if not self.expression:
            return

        # Convert display symbols into Python syntax
        python_expr = self.expression.replace("^", "**")

        try:
            # Exact trig answer, e.g. sin(30) -> 1/2 (None if not applicable)
            exact = exact_trig(python_expr)
            if exact == "Undefined":
                self.show_result("Undefined")
                return

            # eval() runs the text as a Python expression.
            # __builtins__ is emptied so only SAFE_NAMES can be used.
            result = eval(python_expr, {"__builtins__": {}}, SAFE_NAMES)
            raw_result = result            # exact value for DEG/RAD

            # Show whole numbers without ".0" and trim float noise
            if isinstance(result, float):
                result = round(result, 10)
                if result == int(result):
                    result = int(result)

            if exact is not None:
                self.show_exact(exact)
            else:
                self.show_result(str(result), calculated=True)

            # save to history BEFORE the expression is replaced by the result
            self.add_history(self.expression,
                             exact if exact is not None else str(result))
            self.last_typed = self.expression      # remembered for Backspace
            self.expression = str(result)  # allows chaining calculations

            # remember the answer so DEG/RAD can convert it
            self.last_value = raw_result
            self.just_calculated = True

        except ZeroDivisionError:
            self.show_result("Cannot divide by zero")
        except UndefinedError:
            self.show_result("Undefined")
        except ValueError:
            # e.g. sqrt(-1), log(0)
            self.show_result("Error")
        except (SyntaxError, TypeError, NameError):
            # e.g. "5++" or unfinished brackets
            self.show_result("Error")
        except OverflowError:
            self.show_result("Error")


if __name__ == "__main__":
    root = tk.Tk()
    Calculator(root)
    root.mainloop()
