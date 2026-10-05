import tkinter as tk
from gui.dashboard import Dashboard

def main():
    root = tk.Tk()
    root.title("Smart Travel Planner")
    root.geometry("1100x700")

    app = Dashboard(root)
    app.pack(fill="both", expand=True)

    root.mainloop()

if __name__ == "__main__":
    main()
