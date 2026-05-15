#!/usr/bin/env python3
"""
Zen Sweeper — 精美扫雷
========================
一款适合消磨时间的扫雷游戏，界面简洁美观，规则经典。
纯 Python + tkinter，无需安装第三方库。

操作：
  左键点击  — 翻开格子
  右键点击  — 标记/取消旗帜
  双击笑脸  — 重新开始
  按 D 键   — 切换难度

难度：
  初级  9×9   10 颗雷
  中级  16×16 40 颗雷
  高级  30×16 99 颗雷
"""

import tkinter as tk
from tkinter import messagebox
import random
import math
import time
from collections import deque

# ═══════════════════════════════════════════════════════════════
#  配色方案
# ═══════════════════════════════════════════════════════════════

COLORS = {
    "bg":           "#1e1e2e",    # 深色背景
    "header_bg":    "#181825",    # 顶部栏背景
    "cell_hidden":  "#313244",    # 未翻开格子
    "cell_hover":   "#45475a",    # 悬停格子
    "cell_revealed":"#1e1e2e",    # 已翻开格子底
    "border_light": "#585b70",    # 格子亮边
    "border_dark":  "#11111b",    # 格子暗边
    "text_1":       "#89b4fa",    # 1 — 蓝
    "text_2":       "#a6e3a1",    # 2 — 绿
    "text_3":       "#f38ba8",    # 3 — 粉红
    "text_4":       "#cba6f7",    # 4 — 紫
    "text_5":       "#fab387",    # 5 — 橙
    "text_6":       "#94e2d5",    # 6 — 青
    "text_7":       "#f5c2e7",    # 7 — 浅紫
    "text_8":       "#f2cdcd",    # 8 — 浅红
    "mine":         "#f38ba8",    # 地雷
    "flag":         "#f9e2af",    # 旗帜
    "face_normal":  "#cdd6f4",    # 笑脸
    "face_won":     "#a6e3a1",    # 胜利脸
    "face_lost":    "#f38ba8",    # 失败脸
    "counter":      "#cdd6f4",    # 计数器文字
    "status_text":  "#a6adc8",    # 状态栏
    "accent":       "#89b4fa",    # 强调色
}

# ═══════════════════════════════════════════════════════════════
#  游戏逻辑
# ═══════════════════════════════════════════════════════════════

class Minesweeper:
    def __init__(self, rows=9, cols=9, mines=10):
        self.rows = rows
        self.cols = cols
        self.total_mines = mines
        self.reset()

    def reset(self):
        """重置游戏状态（不布雷，等第一次点击后布雷）。"""
        self.grid = [[0] * self.cols for _ in range(self.rows)]
        self.revealed = [[False] * self.cols for _ in range(self.rows)]
        self.flagged = [[False] * self.cols for _ in range(self.rows)]
        self.mines_placed = False
        self.game_over = False
        self.won = False
        self.first_click = True
        self.revealed_count = 0
        self.flag_count = 0
        self.start_time = None
        self.elapsed = 0

    def place_mines(self, safe_row, safe_col):
        """在避开 safe 格及其邻格的前提下随机布雷。"""
        safe_set = set()
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                r, c = safe_row + dr, safe_col + dc
                if 0 <= r < self.rows and 0 <= c < self.cols:
                    safe_set.add((r, c))

        candidates = [(r, c) for r in range(self.rows)
                      for c in range(self.cols) if (r, c) not in safe_set]
        if len(candidates) < self.total_mines:
            candidates = [(r, c) for r in range(self.rows)
                          for c in range(self.cols) if (r, c) != (safe_row, safe_col)]

        mine_positions = random.sample(candidates, self.total_mines)
        for r, c in mine_positions:
            self.grid[r][c] = -1
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.rows and 0 <= nc < self.cols and self.grid[nr][nc] != -1:
                        self.grid[nr][nc] += 1

        self.mines_placed = True

    def reveal(self, row, col):
        """翻开 (row, col)，返回本次新翻开的格子列表。如果是雷返回 None。"""
        if self.game_over:
            return []
        if self.revealed[row][col] or self.flagged[row][col]:
            return []

        if not self.mines_placed:
            self.place_mines(row, col)
            self.start_time = time.time()

        if self.grid[row][col] == -1:
            self.game_over = True
            self.won = False
            return None

        newly_revealed = []
        queue = deque()
        queue.append((row, col))
        self.revealed[row][col] = True
        newly_revealed.append((row, col))
        self.revealed_count += 1

        while queue:
            r, c = queue.popleft()
            if self.grid[r][c] == 0:
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < self.rows and 0 <= nc < self.cols:
                            if not self.revealed[nr][nc] and not self.flagged[nr][nc]:
                                self.revealed[nr][nc] = True
                                newly_revealed.append((nr, nc))
                                self.revealed_count += 1
                                if self.grid[nr][nc] == 0:
                                    queue.append((nr, nc))

        if self.revealed_count == self.rows * self.cols - self.total_mines:
            self.game_over = True
            self.won = True

        return newly_revealed

    def toggle_flag(self, row, col):
        """切换旗帜状态。"""
        if self.game_over or self.revealed[row][col]:
            return False
        self.flagged[row][col] = not self.flagged[row][col]
        self.flag_count += 1 if self.flagged[row][col] else -1
        return True

    def get_remaining_mines(self):
        return self.total_mines - self.flag_count


# ═══════════════════════════════════════════════════════════════
#  Canvas 渲染的格子
# ═══════════════════════════════════════════════════════════════

CELL_SIZE = 32
BORDER_WIDTH = 2
REVEALED_PAD = 3


class ZenSweeperUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Zen Sweeper")
        self.root.resizable(False, False)
        self.root.configure(bg=COLORS["bg"])

        self.difficulties = [
            ("初级  9×9",   9,  9,  10),
            ("中级  16×16", 16, 16, 40),
            ("高级  30×16", 30, 16, 99),
        ]
        self.diff_index = 0
        _, rows, cols, mines = self.difficulties[self.diff_index]
        self.game = Minesweeper(rows, cols, mines)

        self._build_ui()
        self._bind_events()
        self._draw_all()
        self._tick()

    def _build_ui(self):
        rows = self.game.rows
        cols = self.game.cols

        self.header = tk.Frame(self.root, bg=COLORS["header_bg"],
                               highlightthickness=0)
        self.header.pack(fill=tk.X, padx=0, pady=0)

        self.mine_label = tk.Label(
            self.header, text="", font=("Cascadia Code", 18, "bold"),
            fg=COLORS["counter"], bg=COLORS["header_bg"], width=5, anchor=tk.CENTER)
        self.mine_label.pack(side=tk.LEFT, padx=14, pady=8)

        self.face_btn = tk.Label(
            self.header, text="\U0001f642", font=("Segoe UI Emoji", 22),
            fg=COLORS["face_normal"], bg=COLORS["header_bg"],
            cursor="hand2")
        self.face_btn.pack(side=tk.LEFT, expand=True, pady=6)

        self.time_label = tk.Label(
            self.header, text="000", font=("Cascadia Code", 18, "bold"),
            fg=COLORS["counter"], bg=COLORS["header_bg"], width=5, anchor=tk.CENTER)
        self.time_label.pack(side=tk.RIGHT, padx=14, pady=8)

        self.diff_frame = tk.Frame(self.root, bg=COLORS["bg"])
        self.diff_frame.pack(fill=tk.X, padx=10, pady=(6, 0))
        for i, (name, _, _, _) in enumerate(self.difficulties):
            btn = tk.Label(
                self.diff_frame, text=name,
                font=("Microsoft YaHei UI", 10),
                fg=COLORS["status_text"], bg=COLORS["cell_hidden"],
                padx=10, pady=3, cursor="hand2",
                relief=tk.FLAT)
            btn.pack(side=tk.LEFT, padx=3)
            btn.bind("<Button-1>", lambda e, idx=i: self._switch_difficulty(idx))
            if i == self.diff_index:
                btn.configure(fg=COLORS["accent"], bg=COLORS["header_bg"])

        sep = tk.Frame(self.root, height=1, bg=COLORS["border_light"])
        sep.pack(fill=tk.X, padx=12, pady=(6, 8))

        canvas_w = cols * CELL_SIZE + 2
        canvas_h = rows * CELL_SIZE + 2
        self.canvas = tk.Canvas(
            self.root, width=canvas_w, height=canvas_h,
            bg=COLORS["bg"], highlightthickness=0, bd=0)
        self.canvas.pack(padx=16, pady=(0, 2))

        self.status_label = tk.Label(
            self.root, text="左键翻开  ·  右键插旗  ·  D 切换难度",
            font=("Microsoft YaHei UI", 9),
            fg=COLORS["status_text"], bg=COLORS["bg"])
        self.status_label.pack(pady=(0, 8))

        self.cell_rects = [[None for _ in range(cols)] for _ in range(rows)]
        self.cell_texts = [[None for _ in range(cols)] for _ in range(rows)]
        self._hovered = None

    def _rebuild_grid(self):
        rows = self.game.rows
        cols = self.game.cols
        canvas_w = cols * CELL_SIZE + 2
        canvas_h = rows * CELL_SIZE + 2
        self.canvas.configure(width=canvas_w, height=canvas_h)
        self.cell_rects = [[None for _ in range(cols)] for _ in range(rows)]
        self.cell_texts = [[None for _ in range(cols)] for _ in range(rows)]
        self._hovered = None

        for widget in self.diff_frame.winfo_children():
            widget.destroy()
        for i, (name, _, _, _) in enumerate(self.difficulties):
            btn = tk.Label(
                self.diff_frame, text=name,
                font=("Microsoft YaHei UI", 10),
                fg=COLORS["accent"] if i == self.diff_index else COLORS["status_text"],
                bg=COLORS["header_bg"] if i == self.diff_index else COLORS["cell_hidden"],
                padx=10, pady=3, cursor="hand2",
                relief=tk.FLAT)
            btn.pack(side=tk.LEFT, padx=3)
            btn.bind("<Button-1>", lambda e, idx=i: self._switch_difficulty(idx))

    def _bind_events(self):
        self.canvas.bind("<Button-1>", self._on_left_click)
        self.canvas.bind("<Button-3>", self._on_right_click)
        self.canvas.bind("<Motion>", self._on_mouse_move)
        self.canvas.bind("<Leave>", self._on_mouse_leave)
        self.face_btn.bind("<Button-1>", lambda e: self._reset())
        self.root.bind("<Key-d>", lambda e: self._cycle_difficulty())
        self.root.bind("<Key-D>", lambda e: self._cycle_difficulty())
        self.canvas.bind("<Button-2>", self._on_right_click)

    def _on_left_click(self, event):
        r, c = self._event_to_cell(event)
        if r is None:
            return
        if self.game.game_over:
            return

        revealed = self.game.reveal(r, c)
        if revealed is None:
            self._draw_all()
            self._show_game_over(False)
            return

        for rr, cc in revealed:
            self._draw_cell(rr, cc)

        if self.game.won:
            self._draw_all()
            self._show_game_over(True)

    def _on_right_click(self, event):
        r, c = self._event_to_cell(event)
        if r is None or self.game.game_over:
            return
        self.game.toggle_flag(r, c)
        self._draw_cell(r, c)
        self._update_counters()

    def _on_mouse_move(self, event):
        r, c = self._event_to_cell(event)
        if (r, c) == self._hovered:
            return
        if self._hovered is not None:
            pr, pc = self._hovered
            self._draw_cell(pr, pc)
        self._hovered = (r, c)
        if r is not None and not self.game.revealed[r][c] and not self.game.game_over:
            self._draw_hovered(r, c)

    def _on_mouse_leave(self, event):
        if self._hovered is not None:
            pr, pc = self._hovered
            self._hovered = None
            self._draw_cell(pr, pc)

    def _event_to_cell(self, event):
        c = (event.x - 1) // CELL_SIZE
        r = (event.y - 1) // CELL_SIZE
        if 0 <= r < self.game.rows and 0 <= c < self.game.cols:
            return r, c
        return None, None

    def _draw_all(self):
        for r in range(self.game.rows):
            for c in range(self.game.cols):
                self._draw_cell(r, c)
        self._update_counters()
        self._update_face()

    def _draw_cell(self, r, c):
        x1 = 1 + c * CELL_SIZE
        y1 = 1 + r * CELL_SIZE
        x2 = x1 + CELL_SIZE
        y2 = y1 + CELL_SIZE

        if self.cell_rects[r][c] is not None:
            self.canvas.delete(self.cell_rects[r][c])
        if self.cell_texts[r][c] is not None:
            self.canvas.delete(self.cell_texts[r][c])

        revealed = self.game.revealed[r][c]
        flagged = self.game.flagged[r][c]
        is_mine = self.game.grid[r][c] == -1
        is_game_over = self.game.game_over

        if revealed:
            if is_mine:
                rect_id = self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill="#f38ba8", outline=COLORS["border_dark"], width=1)
                text_id = self.canvas.create_text(
                    (x1 + x2) // 2, (y1 + y2) // 2,
                    text="\U0001f4a3", font=("Segoe UI Emoji", CELL_SIZE - 10),
                    anchor=tk.CENTER)
            else:
                rect_id = self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=COLORS["cell_revealed"], outline=COLORS["border_light"], width=1)
                num = self.game.grid[r][c]
                if num > 0:
                    color = COLORS.get(f"text_{num}", COLORS["counter"])
                    text_id = self.canvas.create_text(
                        (x1 + x2) // 2, (y1 + y2) // 2,
                        text=str(num),
                        font=("Cascadia Code", CELL_SIZE - 10, "bold"),
                        fill=color, anchor=tk.CENTER)
                else:
                    text_id = None
        else:
            if flagged:
                rect_id = self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=COLORS["cell_hidden"], outline=COLORS["border_dark"], width=1)
                text_id = self.canvas.create_text(
                    (x1 + x2) // 2, (y1 + y2) // 2,
                    text="\U0001f6a9", font=("Segoe UI Emoji", CELL_SIZE - 10),
                    anchor=tk.CENTER)
            elif is_game_over and is_mine:
                rect_id = self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=COLORS["cell_hidden"], outline=COLORS["border_dark"], width=1)
                text_id = self.canvas.create_text(
                    (x1 + x2) // 2, (y1 + y2) // 2,
                    text="\U0001f4a3", font=("Segoe UI Emoji", CELL_SIZE - 10),
                    anchor=tk.CENTER)
            else:
                rect_id = self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=COLORS["cell_hidden"], outline=COLORS["border_dark"], width=1)
                self.canvas.create_line(x1, y1, x2 - 1, y1, fill=COLORS["border_light"], width=2)
                self.canvas.create_line(x1, y1, x1, y2 - 1, fill=COLORS["border_light"], width=2)
                self.canvas.create_line(x1 + 1, y2 - 1, x2 - 1, y2 - 1,
                                        fill=COLORS["border_dark"], width=2)
                self.canvas.create_line(x2 - 1, y1 + 1, x2 - 1, y2 - 1,
                                        fill=COLORS["border_dark"], width=2)
                text_id = None

        self.cell_rects[r][c] = rect_id
        self.cell_texts[r][c] = text_id

    def _draw_hovered(self, r, c):
        x1 = 1 + c * CELL_SIZE
        y1 = 1 + r * CELL_SIZE
        x2 = x1 + CELL_SIZE
        y2 = y1 + CELL_SIZE

        if self.cell_rects[r][c] is not None:
            self.canvas.delete(self.cell_rects[r][c])
        if self.cell_texts[r][c] is not None:
            self.canvas.delete(self.cell_texts[r][c])

        flagged = self.game.flagged[r][c]
        rect_id = self.canvas.create_rectangle(
            x1, y1, x2, y2,
            fill=COLORS["cell_hover"], outline=COLORS["border_dark"], width=1)
        self.canvas.create_line(x1, y1, x2 - 1, y1, fill=COLORS["border_light"], width=2)
        self.canvas.create_line(x1, y1, x1, y2 - 1, fill=COLORS["border_light"], width=2)
        self.canvas.create_line(x1 + 1, y2 - 1, x2 - 1, y2 - 1,
                                fill=COLORS["border_dark"], width=2)
        self.canvas.create_line(x2 - 1, y1 + 1, x2 - 1, y2 - 1,
                                fill=COLORS["border_dark"], width=2)

        text_id = None
        if flagged:
            text_id = self.canvas.create_text(
                (x1 + x2) // 2, (y1 + y2) // 2,
                text="\U0001f6a9", font=("Segoe UI Emoji", CELL_SIZE - 10),
                anchor=tk.CENTER)

        self.cell_rects[r][c] = rect_id
        self.cell_texts[r][c] = text_id

    def _update_counters(self):
        remaining = self.game.get_remaining_mines()
        self.mine_label.configure(text=f"{remaining:03d}")

    def _update_face(self):
        if self.game.won:
            self.face_btn.configure(text="\U0001f60e", fg=COLORS["face_won"])
        elif self.game.game_over and not self.game.won:
            self.face_btn.configure(text="\U0001f635", fg=COLORS["face_lost"])
        else:
            self.face_btn.configure(text="\U0001f642", fg=COLORS["face_normal"])

    def _show_game_over(self, won):
        self._update_face()
        if won:
            self.status_label.configure(text=f"\U0001f389 恭喜通关！耗时 {self.game.elapsed} 秒")
        else:
            self.status_label.configure(text="\U0001f4a5 踩到雷了…点击笑脸重新开始")

    def _tick(self):
        if self.game.start_time is not None and not self.game.game_over:
            self.game.elapsed = int(time.time() - self.game.start_time)
            self.time_label.configure(text=f"{min(self.game.elapsed, 999):03d}")
        self.root.after(200, self._tick)

    def _reset(self):
        _, rows, cols, mines = self.difficulties[self.diff_index]
        self.game = Minesweeper(rows, cols, mines)
        self._rebuild_grid()
        self._draw_all()
        self.status_label.configure(
            text="左键翻开  ·  右键插旗  ·  D 切换难度")

    def _switch_difficulty(self, idx):
        if idx == self.diff_index:
            return
        self.diff_index = idx
        _, rows, cols, mines = self.difficulties[idx]
        self.game = Minesweeper(rows, cols, mines)
        self._rebuild_grid()
        self._draw_all()
        self.status_label.configure(
            text="左键翻开  ·  右键插旗  ·  D 切换难度")
        self.face_btn.configure(text="\U0001f642", fg=COLORS["face_normal"])

    def _cycle_difficulty(self):
        nxt = (self.diff_index + 1) % len(self.difficulties)
        self._switch_difficulty(nxt)

    def run(self):
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.root.geometry(f"+{x}+{y}")

        self.root.after(50, lambda: self.root.deiconify())
        try:
            self.root.iconbitmap(default="")
        except Exception:
            pass

        self.root.mainloop()


if __name__ == "__main__":
    app = ZenSweeperUI()
    app.run()
