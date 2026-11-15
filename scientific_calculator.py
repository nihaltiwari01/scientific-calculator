"""
Scientific Calculator using Python Tkinter
Run:  python scientific_calculator.py
No extra libraries needed (tkinter and math come with Python).
"""

import math
import tkinter as tk


# ---------------------------------------------------------------
# 1. Math functions allowed inside an expression.
#    Trigonometric functions work in DEGREES (sin(90) = 1).
# ---------------------------------------------------------------
SAFE_NAMES = {
    "sin": lambda x: math.sin(math.radians(x)),
    "cos": lambda x: math.cos(math.radians(x)),
    "tan": lambda x: math.tan(math.radians(x)),
    "sqrt": math.sqrt,
    "log": math.log10,
    "ln": math.log,
    "pi": math.pi,
    "e": math.e,
}


class Calculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Scientific Calculator")
        self.root.resizable(False, False)
        self.root.configure(bg="#1e1e1e")

        self.expression = ""  # what the user has typed so far

        self.create_display()
        self.create_buttons()
        self.bind_keyboard()

    # -----------------------------------------------------------
    # 2. Display: one line for the expression, one for the result
    # -----------------------------------------------------------
    def create_display(self):
        self.expr_var = tk.StringVar()
        self.result_var = tk.StringVar(value="0")

        tk.Label(
            self.root, textvariable=self.expr_var, anchor="e",
            font=("Consolas", 14), bg="#1e1e1e", fg="#a0a0a0",
        ).grid(row=0, column=0, columnspan=5, sticky="ew", padx=10, pady=(10, 0))

        tk.Label(
            self.root, textvariable=self.result_var, anchor="e",
            font=("Consolas", 26, "bold"), bg="#1e1e1e", fg="white",
        ).grid(row=1, column=0, columnspan=5, sticky="ew", padx=10, pady=(0, 10))

    # -----------------------------------------------------------
    # 3. Buttons placed using the grid layout
    #    Each button: (label, text inserted / action)
    # -----------------------------------------------------------
    def create_buttons(self):
        layout = [
            [("sin", "sin("), ("cos", "cos("), ("tan", "tan("), ("log", "log("), ("ln", "ln(")],
            [("√", "sqrt("), ("x²", "**2"), ("xʸ", "^"), ("π", "pi"), ("e", "e")],
            [("(", "("), (")", ")"), ("C", "CLEAR"), ("⌫", "BACK"), ("÷", "/")],
            [("7", "7"), ("8", "8"), ("9", "9"), ("×", "*"), ("-", "-")],
            [("4", "4"), ("5", "5"), ("6", "6"), ("+", "+"), ("%", "%")],
            [("1", "1"), ("2", "2"), ("3", "3"), ("0", "0"), (".", ".")],
        ]

        for r, row in enumerate(layout, start=2):
            for c, (label, value) in enumerate(row):
                self.make_button(label, value, r, c)

        # Equals button spans the full width on the last row
        tk.Button(
            self.root, text="=", font=("Consolas", 16, "bold"),
            bg="#ff9500", fg="white", bd=0, height=2,
            command=self.calculate,
        ).grid(row=8, column=0, columnspan=5, sticky="nsew", padx=3, pady=3)

    def make_button(self, label, value, row, col):
        if value == "CLEAR":
            colour = "#d9534f"
        elif value == "BACK":
            colour = "#f0ad4e"
        elif label.isdigit() or label == ".":
            colour = "#3a3a3a"
        else:
            colour = "#505050"

        tk.Button(
            self.root, text=label, width=6, height=2,
            font=("Consolas", 13), bg=colour, fg="white",
            activebackground="#707070", activeforeground="white", bd=0,
            # lambda with default arg: each button remembers ITS OWN value
            command=lambda v=value: self.on_click(v),
        ).grid(row=row, column=col, sticky="nsew", padx=3, pady=3)

    # -----------------------------------------------------------
    # 4. Event handling: every button click ends up here
    # -----------------------------------------------------------
    def on_click(self, value):
        if value == "CLEAR":
            self.clear()
        elif value == "BACK":
            self.backspace()
        else:
            # If the last result was an error message, start fresh
            if self.result_var.get() in ("Error", "Cannot divide by zero"):
                self.clear()
            self.expression += value
            self.update_display()

    def clear(self):
        self.expression = ""
        self.expr_var.set("")
        self.result_var.set("0")

    def backspace(self):
        # Remove the last character typed
        self.expression = self.expression[:-1]
        self.update_display()

    def update_display(self):
        self.expr_var.set(self.expression)

    # -----------------------------------------------------------
    # 5. Evaluate the expression and handle errors
    # -----------------------------------------------------------
    def calculate(self):
        if not self.expression:
            return

        # Convert display symbols into Python syntax
        python_expr = self.expression.replace("^", "**")

        try:
            # eval() runs the text as a Python expression.
            # __builtins__ is emptied so only SAFE_NAMES can be used.
            result = eval(python_expr, {"__builtins__": {}}, SAFE_NAMES)

            # Show whole numbers without ".0" and trim float noise
            if isinstance(result, float):
                result = round(result, 10)
                if result == int(result):
                    result = int(result)

            self.result_var.set(str(result))
            self.expression = str(result)  # allows chaining calculations

        except ZeroDivisionError:
            self.result_var.set("Cannot divide by zero")
        except ValueError:
            # e.g. sqrt(-1), log(0)
            self.result_var.set("Error")
        except (SyntaxError, TypeError, NameError):
            # e.g. "5++" or unfinished brackets
            self.result_var.set("Error")
        except OverflowError:
            self.result_var.set("Error")

    # -----------------------------------------------------------
    # 6. Keyboard support (bonus)
    # -----------------------------------------------------------
    def bind_keyboard(self):
        self.root.bind("<Return>", lambda event: self.calculate())
        self.root.bind("<BackSpace>", lambda event: self.backspace())
        self.root.bind("<Escape>", lambda event: self.clear())
        self.root.bind("<Key>", self.on_key)

    def on_key(self, event):
        if event.char and event.char in "0123456789.+-*/()^%":
            self.on_click(event.char)


if __name__ == "__main__":
    root = tk.Tk()
    Calculator(root)
    root.mainloop()
