"""Interactive array and binary-tree traversal visualizer.

Run: python traversal_visualizer.py
Requires only Python's standard-library tkinter module.
"""

import tkinter as tk
from tkinter import ttk

ARRAY = [12, 7, 25, 9, 18, 31, 4] 

#Dictionary = {key: ('value1','value2')}
TREE = {
    "A": (50, "B", "C"),
    "B": (30, "D", "E"),
    "C": (70, "F", "G"),
    "D": (20, None, None),
    "E": (40, None, None),
    "F": (60, None, None),
    "G": (80, None, None),
}
POSITIONS = {"A": (470, 100), "B": (255, 220), "C": (685, 220),
             "D": (145, 345), "E": (365, 345), "F": (575, 345), "G": (795, 345)}
COLORS = {"bg": "#f6f8fc", "paper": "#ffffff", "ink": "#182439",
          "muted": "#66758b", "line": "#c7d1df", "idle": "#e8eef8",
          "visited": "#c4e8d8", "active": "#20845b", "active_text": "#ffffff"}


def preorder(node):
    if node is None:
        return []
    _, left, right = TREE[node]
    return [node] + preorder(left) + preorder(right)


def inorder(node):
    if node is None:
        return []
    _, left, right = TREE[node]
    return inorder(left) + [node] + inorder(right)


def postorder(node):
    if node is None:
        return []
    _, left, right = TREE[node]
    return postorder(left) + postorder(right) + [node]


def levelorder(root):
    queue, result = [root], []
    while queue:
        node = queue.pop(0)
        result.append(node)
        _, left, right = TREE[node]
        if left:
            queue.append(left)
        if right:
            queue.append(right)
    return result


class Visualizer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Interactive Traversal Visualizer — Arrays & Binary Trees")
        self.geometry("1020x735")
        self.minsize(900, 650)
        self.configure(bg=COLORS["bg"])

        self.mode = tk.StringVar(value="Array")
        self.order = tk.StringVar(value="Inorder")
        self.speed = tk.IntVar(value=750)
        self.step = -1
        self.playing = False
        self.timer = None

        style = ttk.Style(self)
        if "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure("TCombobox", font=("Segoe UI", 11), padding=6)
        style.configure("TButton", font=("Segoe UI", 11), padding=8)
        style.configure("TLabel", background=COLORS["bg"], foreground=COLORS["ink"])

        top = tk.Frame(self, bg=COLORS["bg"])
        top.pack(fill="x", padx=24, pady=(18, 10))
        tk.Label(top, text="Traversal Visualizer", font=("Segoe UI", 23, "bold"),
                 bg=COLORS["bg"], fg=COLORS["ink"]).pack(anchor="w")
        tk.Label(top, text="Explore traversal one step at a time. Green = current; pale green = visited.",
                 font=("Segoe UI", 11), bg=COLORS["bg"], fg=COLORS["muted"]).pack(anchor="w", pady=(3, 0))

        selector = tk.Frame(self, bg=COLORS["bg"])
        selector.pack(fill="x", padx=24, pady=(8, 10))
        tk.Label(selector, text="Structure", font=("Segoe UI", 11, "bold"),
                 bg=COLORS["bg"], fg=COLORS["ink"]).pack(side="left", padx=(0, 10))
        mode_picker = ttk.Combobox(selector, textvariable=self.mode, state="readonly", width=16,
                                   values=["Array", "Binary Tree"])
        mode_picker.pack(side="left")
        mode_picker.bind("<<ComboboxSelected>>", self.change_mode)
        tk.Label(selector, text="Traversal", font=("Segoe UI", 11, "bold"),
                 bg=COLORS["bg"], fg=COLORS["ink"]).pack(side="left", padx=(28, 10))
        self.order_picker = ttk.Combobox(selector, textvariable=self.order, state="readonly", width=16,
                                         values=["Preorder", "Inorder", "Postorder", "Level Order"])
        self.order_picker.pack(side="left")
        self.order_picker.bind("<<ComboboxSelected>>", self.change_mode)
        self.order_picker.configure(state="disabled")

        self.canvas = tk.Canvas(self, bg=COLORS["paper"], highlightthickness=1,
                                highlightbackground="#dfe5ef", height=410)
        self.canvas.pack(fill="both", expand=True, padx=24, pady=(0, 14))
        self.canvas.bind("<Configure>", lambda e: self.draw())

        panel = tk.Frame(self, bg=COLORS["bg"])
        panel.pack(fill="x", padx=24)
        self.message = tk.Label(panel, text="", font=("Segoe UI", 12),
                                bg=COLORS["bg"], fg=COLORS["ink"], anchor="w")
        self.message.pack(fill="x")
        self.progress = tk.Label(panel, text="", font=("Consolas", 11),
                                 bg=COLORS["bg"], fg=COLORS["muted"], anchor="w")
        self.progress.pack(fill="x", pady=(5, 0))

        controls = tk.Frame(self, bg=COLORS["bg"])
        controls.pack(fill="x", padx=24, pady=(17, 20))
        self.prev_btn = ttk.Button(controls, text="◀ Previous", command=self.previous)
        self.prev_btn.pack(side="left", padx=(0, 8))
        self.next_btn = ttk.Button(controls, text="Next ▶", command=self.next_step)
        self.next_btn.pack(side="left", padx=(0, 8))
        self.play_btn = ttk.Button(controls, text="▶ Play", command=self.toggle_play)
        self.play_btn.pack(side="left", padx=(0, 8))
        ttk.Button(controls, text="↺ Reset", command=self.reset).pack(side="left")
        tk.Label(controls, text="Auto-play delay (ms)", font=("Segoe UI", 10),
                 bg=COLORS["bg"], fg=COLORS["muted"]).pack(side="right", padx=(8, 0))
        ttk.Scale(controls, from_=1300, to=250, variable=self.speed, orient="horizontal",
                  length=130).pack(side="right")

        self.bind("<Right>", lambda e: self.next_step())
        self.bind("<Left>", lambda e: self.previous())
        self.reset()

    def steps(self):
        if self.mode.get() == "Array":
            return list(range(len(ARRAY)))
        return {"Preorder": preorder, "Inorder": inorder, "Postorder": postorder,
                "Level Order": levelorder}[self.order.get()]("A")

    def change_mode(self, _event=None):
        self.order_picker.configure(state="readonly" if self.mode.get() == "Binary Tree" else "disabled")
        self.reset()

    def stop_play(self):
        self.playing = False
        if self.timer is not None:
            self.after_cancel(self.timer)
            self.timer = None
        self.play_btn.configure(text="▶ Play")

    def reset(self):
        self.stop_play()
        self.step = -1
        self.draw()

    def next_step(self):
        if self.step < len(self.steps()) - 1:
            self.step += 1
        else:
            self.stop_play()
        self.draw()

    def previous(self):
        self.stop_play()
        self.step = max(-1, self.step - 1)
        self.draw()

    def toggle_play(self):
        if self.playing:
            self.stop_play()
        else:
            if self.step == len(self.steps()) - 1:
                self.step = -1
            self.playing = True
            self.play_btn.configure(text="❚❚ Pause")
            self.advance_auto()

    def advance_auto(self):
        if not self.playing:
            return
        self.next_step()
        if self.step < len(self.steps()) - 1:
            self.timer = self.after(max(200, int(self.speed.get())), self.advance_auto)
        else:
            self.stop_play()

    def draw(self):
        if not hasattr(self, "canvas"):
            return
        self.canvas.delete("all")
        width = max(self.canvas.winfo_width(), 900)
        height = max(self.canvas.winfo_height(), 360)
        sequence = self.steps()
        visited = set(sequence[:self.step + 1])
        active = sequence[self.step] if self.step >= 0 else None
        if self.mode.get() == "Array":
            self.draw_array(width, height, visited, active)
            label = f"Index {active}, value {ARRAY[active]}" if active is not None else "Press Next to start array traversal."
            result = [ARRAY[i] for i in sequence[:self.step + 1]]
        else:
            self.draw_tree(width, height, visited, active)
            label = f"Visit node {TREE[active][0]} ({active})" if active is not None else f"Press Next to start {self.order.get()} traversal."
            result = [TREE[node][0] for node in sequence[:self.step + 1]]
        if self.step == len(sequence) - 1:
            label += "  — Traversal complete!"
        self.message.configure(text=label)
        self.progress.configure(text=f"Step {self.step + 1} / {len(sequence)}      Visited: " +
                                (" → ".join(map(str, result)) if result else "(none)"))
        self.prev_btn.configure(state="normal" if self.step >= 0 else "disabled")
        self.next_btn.configure(state="normal" if self.step < len(sequence) - 1 else "disabled")

    def draw_array(self, w, h, visited, active):
        self.canvas.create_text(w / 2, max(40, h * .23), text="ARRAY TRAVERSAL  •  Left to Right",
                                font=("Segoe UI", 16, "bold"), fill=COLORS["ink"])
        count = len(ARRAY)
        box_w = min(100, (w - 90) / count)
        start = (w - count * box_w) / 2
        top = max(100, h * .43)
        for i, value in enumerate(ARRAY):
            x1, x2 = start + i * box_w + 4, start + (i + 1) * box_w - 4
            color = COLORS["active"] if i == active else (COLORS["visited"] if i in visited else COLORS["idle"])
            self.canvas.create_rectangle(x1, top, x2, top + 73, fill=color, outline="#b5c5d7", width=1)
            self.canvas.create_text((x1 + x2) / 2, top + 36, text=str(value),
                                    font=("Segoe UI", 19, "bold"),
                                    fill="white" if i == active else COLORS["ink"])
            self.canvas.create_text((x1 + x2) / 2, top + 96, text=f"index {i}",
                                    font=("Segoe UI", 10), fill=COLORS["muted"])
            if i == active:
                self.canvas.create_text((x1 + x2) / 2, top - 23, text="▼ CURRENT",
                                        font=("Segoe UI", 10, "bold"), fill=COLORS["active"])

    def draw_tree(self, w, h, visited, active):
        self.canvas.create_text(w / 2, 30, text=f"BINARY TREE  •  {self.order.get()}",
                                font=("Segoe UI", 16, "bold"), fill=COLORS["ink"])
        # Scale the logical positions to the available canvas area.
        sx = min((w - 90) / 940, 1.3)
        sy = min((h - 92) / 410, 1.05)
        def pos(node):
            x, y = POSITIONS[node]
            return w / 2 + (x - 470) * sx, 42 + y * sy
        for node, (_, left, right) in TREE.items():
            for child in (left, right):
                if child:
                    ax, ay = pos(node)
                    bx, by = pos(child)
                    self.canvas.create_line(ax, ay, bx, by, width=2.5, fill=COLORS["line"])
        r = 29
        for node, (value, _, _) in TREE.items():
            x, y = pos(node)
            color = COLORS["active"] if node == active else (COLORS["visited"] if node in visited else COLORS["idle"])
            self.canvas.create_oval(x-r, y-r, x+r, y+r, fill=color, outline="#b5c5d7", width=1.5)
            self.canvas.create_text(x, y, text=str(value), font=("Segoe UI", 16, "bold"),
                                    fill="white" if node == active else COLORS["ink"])
            if node == active:
                self.canvas.create_text(x, y-r-15, text="CURRENT", font=("Segoe UI", 9, "bold"),
                                        fill=COLORS["active"])


if __name__ == "__main__":
    Visualizer().mainloop()
