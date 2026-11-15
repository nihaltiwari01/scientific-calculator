# 🧮 Scientific Calculator (Python Tkinter)

A desktop scientific calculator built with Python and Tkinter. It supports basic arithmetic and scientific operations through a simple graphical interface.

> **Course Assignment** · Problem 1 · Marks: 20

---

## 📸 Screenshot

![Calculator Screenshot](screenshot.png)

---

## ✨ Features

- Number buttons (0-9) and decimal point
- Basic operators: `+`  `-`  `×`  `÷`  `%`
- Scientific functions: square root (`√`), square (`x²`), power (`xʸ`)
- Trigonometric functions: `sin`, `cos`, `tan` (angles in **degrees**)
- Extra functions: `log`, `ln`, `π`, `e`, brackets `( )`
- Two-line display: the expression you typed and the calculated result
- **C** (Clear) and **⌫** (Backspace) buttons
- Keyboard support: `Enter` = calculate, `Backspace` = delete, `Esc` = clear
- Error handling for division by zero, invalid expressions and math errors

---

## 🛠️ Requirements

- Python 3.8 or higher
- Tkinter (comes pre-installed with Python on Windows and macOS)

No extra libraries need to be installed.

> On some Linux systems, install Tkinter with: `sudo apt install python3-tk`

---

## 🚀 How to Run

1. Clone the repository:
   ```bash
   git clone https://github.com/nihaltiwari01/scientific-calculator.git
   ```
2. Go into the folder:
   ```bash
   cd scientific-calculator
   ```
3. Run the program:
   ```bash
   python scientific_calculator.py
   ```
   (Use `python3` instead of `python` on macOS/Linux if needed.)

---

## 📖 How to Use

| To do this | Do this |
|---|---|
| Add numbers | Click digit buttons or type on the keyboard |
| Use a function | Click `sin`, `√`, etc. and then type the value and close the bracket, e.g. `sqrt(16)` |
| Square a number | Type the number, then click `x²` |
| Raise to a power | Type the base, click `xʸ`, then type the exponent |
| Get the answer | Click `=` or press `Enter` |
| Delete last character | Click `⌫` |
| Reset everything | Click `C` |

**Examples**

| Input | Output |
|---|---|
| `2^3` | `8` |
| `sqrt(16)` | `4` |
| `sin(90)` | `1` |
| `5/0` | `Cannot divide by zero` |
| `sqrt(-1)` | `Error` |

---

## ⚙️ How It Works

1. **Button clicks** – Every button is created with a `command` that calls `on_click(value)`. The value is added to the current expression and shown on the display.
2. **Evaluating the expression** – When `=` is pressed, `calculate()` converts `^` to `**` and evaluates the text using Python's `eval()`. Only the allowed math names (`sin`, `cos`, `sqrt`, etc.) are available, and Python's built-in functions are disabled for safety.
3. **Error handling** – A `try/except` block catches `ZeroDivisionError`, `ValueError`, `SyntaxError`, `TypeError`, `NameError` and `OverflowError`, and shows a friendly message instead of crashing.

---

## 📚 Concepts Demonstrated

- Tkinter widgets (`Tk`, `Label`, `Button`)
- Grid layout (`.grid()` with rows, columns and spans)
- Event handling (button commands and keyboard bindings)
- Functions and classes (object-oriented structure)
- Mathematical operations using the `math` module
- Exception handling (`try/except`)

---

## 📁 Project Structure

```
scientific-calculator/
├── scientific_calculator.py   # Main source code
├── screenshot.png             # Screenshot of the app
└── README.md                  # Project documentation
```

---

## 👥 Team Members

| Name | Roll No. |
|---|---|
| Nihal Tiwari | C25CS007 |
| Mudit Tejra | C25CS009 |
| Pawan Kumar Nayak | C25CS011 |

**Institute:** National Institute of Technology Meghalaya  
**Program:** MCA, 3rd Semester

---

## 📄 License

This project was created for academic purposes.
