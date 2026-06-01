#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
番茄钟 · Pomodoro Timer (图形界面版)

圆环倒计时 + 番茄主题:
  - 外圈 Apple 经典彩虹装饰环
  - 内圈进度环（随剩余时间消减）
  - 专注 / 短休息 / 长休息自动循环，每 4 个番茄一次长休息
  - 阶段切换弹出 macOS 通知并响铃

依赖：Python 3 自带的 tkinter（无需额外安装）
运行：python3 pomodoro_gui.py
"""

import os
import subprocess
import tkinter as tk
from tkinter import font as tkfont

# ───────────────────────── 配置 ─────────────────────────
FOCUS_MIN     = 45     # 专注时长（分钟）
BREAK_MIN     = 10     # 短休息时长（分钟）
LONGBREAK_MIN = 30     # 长休息时长（分钟）
SET_SIZE      = 4      # 每几个番茄进入一次长休息

# ───────────────────────── 配色 ─────────────────────────
BG       = "#1d1d22"          # 窗口背景
CARD     = "#26262e"          # 卡片/轨道底色
TEXT     = "#f5f5f7"          # 主文字
SUBTEXT  = "#9a9aa5"          # 次要文字
TRACK    = "#3a3a44"          # 进度环轨道

PHASE = {
    "focus": {"label": "专注  ·  FOCUS",      "color": "#e8392b"},
    "short": {"label": "休息  ·  BREAK",      "color": "#5fbf4a"},
    "long":  {"label": "长休息  ·  LONG BREAK", "color": "#a45cd6"},
}

APPLE_RAINBOW = ["#61bb46", "#fdb827", "#f5821f",
                 "#e03a3e", "#963d97", "#009ddc"]

# 圆环几何
SIZE   = 300                  # 画布尺寸
CX = CY = SIZE // 2
R_RING = 120                  # 进度环半径
W_RING = 18                   # 进度环宽度
R_RAIN = 142                  # 彩虹环半径
W_RAIN = 6                    # 彩虹环宽度


class Pomodoro:
    def __init__(self, root):
        self.root = root
        self.phase = "focus"
        self.total = FOCUS_MIN * 60
        self.remaining = self.total
        self.running = False
        self.count = 0            # 已完成的番茄数
        self._job = None          # after 定时器句柄

        self._build_ui()
        self._refresh()

    # ───────────────── 界面构建 ─────────────────
    def _build_ui(self):
        self.root.title("番茄钟")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        # 字体
        self.f_title = tkfont.Font(family="Helvetica Neue", size=18, weight="bold")
        self.f_time  = tkfont.Font(family="Helvetica Neue", size=62, weight="bold")
        self.f_phase = tkfont.Font(family="Helvetica Neue", size=15, weight="bold")
        self.f_dots  = tkfont.Font(family="Helvetica Neue", size=20)
        self.f_btn   = tkfont.Font(family="Helvetica Neue", size=14, weight="bold")
        self.f_small = tkfont.Font(family="Helvetica Neue", size=11)

        # 标题
        tk.Label(self.root, text="番茄钟", font=self.f_title,
                 fg=TEXT, bg=BG).pack(pady=(22, 6))

        # 圆环画布
        self.canvas = tk.Canvas(self.root, width=SIZE, height=SIZE,
                                bg=BG, highlightthickness=0)
        self.canvas.pack(padx=40)

        # 外圈彩虹装饰（静态）
        seg = 360 / 6
        for i, col in enumerate(APPLE_RAINBOW):
            self.canvas.create_arc(
                CX - R_RAIN, CY - R_RAIN, CX + R_RAIN, CY + R_RAIN,
                start=90 - i * seg - 2, extent=-(seg - 4),
                style=tk.ARC, outline=col, width=W_RAIN)

        # 进度环轨道
        self.canvas.create_oval(
            CX - R_RING, CY - R_RING, CX + R_RING, CY + R_RING,
            outline=TRACK, width=W_RING)

        # 进度环（动态弧）
        self.arc = self.canvas.create_arc(
            CX - R_RING, CY - R_RING, CX + R_RING, CY + R_RING,
            start=90, extent=-359.999, style=tk.ARC,
            outline=PHASE["focus"]["color"], width=W_RING)

        # 中心时间文字
        self.time_text = self.canvas.create_text(
            CX, CY - 8, text="45:00", fill=TEXT, font=self.f_time)
        # 阶段文字
        self.phase_text = self.canvas.create_text(
            CX, CY + 46, text=PHASE["focus"]["label"],
            fill=PHASE["focus"]["color"], font=self.f_phase)

        # 番茄进度圆点
        self.dots = tk.Label(self.root, text="", font=self.f_dots, bg=BG)
        self.dots.pack(pady=(10, 2))

        # 状态信息
        self.status = tk.Label(self.root, text="", font=self.f_small,
                               fg=SUBTEXT, bg=BG)
        self.status.pack(pady=(0, 12))

        # 按钮区
        btns = tk.Frame(self.root, bg=BG)
        btns.pack(pady=(0, 24))
        self.btn_start = self._pill(btns, "开始", PHASE["focus"]["color"],
                                    self.toggle, width=10)
        self.btn_start.grid(row=0, column=0, padx=6)
        self._pill(btns, "重置", CARD, self.reset, width=7
                   ).grid(row=0, column=1, padx=6)
        self._pill(btns, "跳过", CARD, self.skip, width=7
                   ).grid(row=0, column=2, padx=6)

        # 尝试设置窗口图标
        self._set_icon()
        self._center_window()

    def _pill(self, parent, text, color, cmd, width=8):
        """用 Label 实现可着色的圆角风格按钮（macOS 下原生按钮无法改色）"""
        lbl = tk.Label(parent, text=text, font=self.f_btn, fg="#ffffff",
                       bg=color, width=width, pady=9, cursor="pointinghand")
        lbl.bind("<Button-1>", lambda e: cmd())
        # 悬停高亮
        def on_enter(e): lbl.configure(highlightbackground=color)
        lbl._base = color
        return lbl

    def _set_icon(self):
        here = os.path.dirname(os.path.abspath(__file__))
        png = os.path.join(here, "icon", "icon.png")
        if os.path.exists(png):
            try:
                self._iconimg = tk.PhotoImage(file=png)
                self.root.iconphoto(True, self._iconimg)
            except Exception:
                pass

    def _center_window(self):
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 3
        self.root.geometry(f"+{x}+{y}")

    # ───────────────── 计时逻辑 ─────────────────
    def toggle(self):
        self.running = not self.running
        if self.running:
            self.btn_start.configure(text="暂停")
            self._tick()
        else:
            self.btn_start.configure(text="继续")
            if self._job:
                self.root.after_cancel(self._job)
                self._job = None

    def _tick(self):
        if not self.running:
            return
        if self.remaining > 0:
            self.remaining -= 1
            self._refresh()
            self._job = self.root.after(1000, self._tick)
        else:
            self._advance()

    def _advance(self):
        """阶段切换"""
        if self.phase == "focus":
            self.count += 1
            if self.count % SET_SIZE == 0:
                self._set_phase("long")
                self._notify("专注结束", f"完成 {SET_SIZE} 个番茄，长休息 {LONGBREAK_MIN} 分钟")
            else:
                self._set_phase("short")
                self._notify("专注结束", f"休息 {BREAK_MIN} 分钟")
        else:
            self._set_phase("focus")
            self._notify("休息结束", f"开始第 {self.count + 1} 个番茄")
        # 自动进入下一阶段并继续计时
        self._refresh()
        if self.running:
            self._job = self.root.after(1000, self._tick)

    def _set_phase(self, phase):
        self.phase = phase
        self.total = {"focus": FOCUS_MIN, "short": BREAK_MIN,
                      "long": LONGBREAK_MIN}[phase] * 60
        self.remaining = self.total
        color = PHASE[phase]["color"]
        self.canvas.itemconfig(self.arc, outline=color)
        self.canvas.itemconfig(self.phase_text,
                               text=PHASE[phase]["label"], fill=color)
        if not self.running:
            self.btn_start.configure(bg=color)
            self.btn_start._base = color

    def reset(self):
        self.running = False
        if self._job:
            self.root.after_cancel(self._job)
            self._job = None
        self.remaining = self.total
        self.btn_start.configure(text="开始")
        self._refresh()

    def skip(self):
        was_running = self.running
        if self._job:
            self.root.after_cancel(self._job)
            self._job = None
        self.remaining = 0
        # 直接推进到下一阶段
        self.running = was_running
        self._advance()
        if not was_running:
            self.running = False
            self.btn_start.configure(text="开始")
            self._refresh()

    # ───────────────── 刷新显示 ─────────────────
    def _refresh(self):
        mm, ss = divmod(self.remaining, 60)
        self.canvas.itemconfig(self.time_text, text=f"{mm:02d}:{ss:02d}")
        # 进度弧：随剩余时间消减
        frac = self.remaining / self.total if self.total else 0
        extent = -359.999 * frac
        self.canvas.itemconfig(self.arc, extent=extent)
        # 圆点
        done = self.count % SET_SIZE
        if self.phase != "focus" and done == 0 and self.count > 0:
            done = SET_SIZE  # 刚完成一组、正在长休息
        dots = "● " * done + "○ " * (SET_SIZE - done)
        self.dots.configure(text=dots.strip(), fg=PHASE[self.phase]["color"])
        # 状态
        self.status.configure(
            text=f"已完成 {self.count} 个番茄    |    "
                 f"专注 {FOCUS_MIN}m · 短休 {BREAK_MIN}m · 长休 {LONGBREAK_MIN}m")

    # ───────────────── 通知 ─────────────────
    def _notify(self, title, msg):
        try:
            subprocess.Popen(
                ["osascript", "-e",
                 f'display notification "{msg}" with title "番茄钟 · {title}" sound name "Glass"'],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass


def main():
    root = tk.Tk()
    app = Pomodoro(root)
    if os.environ.get("POMODORO_SELFTEST") == "1":
        # 冒烟测试：刷新几帧后退出，验证无异常
        for _ in range(3):
            root.update()
        root.destroy()
        print("SELFTEST OK")
        return
    root.mainloop()


if __name__ == "__main__":
    main()
