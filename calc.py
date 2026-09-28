import tkinter as tk

def button_click(symbol):
    if symbol == "C":
        entry.delete(0, tk.END)
    elif symbol == "=":
        try:
            result = eval(entry.get())
            entry.delete(0, tk.END)
            entry.insert(tk.END, str(result))
        except Exception:
            entry.delete(0, tk.END)
            entry.insert(tk.END, "Error")
    else:
        entry.insert(tk.END, symbol)

# Window Setup
root = tk.Tk()
root.title("Python Calculator")
root.geometry("300x400")

# Display
entry = tk.Entry(root, font=("Arial", 20), justify="right")
entry.pack(fill="x", padx=10, pady=10)

# Buttons Grid
buttons = [
    ['7', '8', '9', '/'],
    ['4', '5', '6', '*'],
    ['1', '2', '3', '-'],
    ['C', '0', '=', '+']
]

for row in buttons:
    frame = tk.Frame(root)
    frame.pack(expand=True, fill="both")
    for btn_text in row:
        btn = tk.Button(frame, text=btn_text, font=("Arial", 18),
                        command=lambda t=btn_text: button_click(t))
        btn.pack(side="left", expand=True, fill="both")

root.mainloop()