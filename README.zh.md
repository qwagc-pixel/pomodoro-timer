# 番茄钟 · Pomodoro Timer

[English](README.md) · **简体中文**

一个纯 Bash 编写的终端番茄钟,带实时时钟、ASCII 大号倒计时、进度条,以及 Apple 经典彩虹配色的 WWDC 倒计时横幅。附带 macOS `.app` 应用包与图标。

> 本项目使用 Anthropic 的 AI 助手 [Claude](https://claude.com/claude-code) 开发。

![icon](icon/icon.png)

## 功能

- **实时时钟** + 日期显示
- **番茄工作法**:专注 / 短休息 / 长休息自动循环
- 每完成 **4 个番茄**进入一次**长休息**,并用圆点 `●●●○` 显示本组进度
- 5 行高的 **ASCII 大号倒计时**数字,远距离也清晰
- 彩色**进度条** + 百分比
- 阶段切换时**终端响铃 + macOS 系统通知**
- **WWDC 倒计时**横幅,字母采用 1977 年 Apple 彩虹 logo 六色
- 全 ASCII / Unicode 制表符绘制,适配标准终端,不闪烁不错位

## 用法

### 直接运行脚本

```bash
./pomodoro                 # 默认:专注 45 / 短休 10 / 长休 30 分钟
./pomodoro 25 5 15         # 自定义:专注 25 / 短休 5 / 长休 15 分钟
```

按 `Ctrl-C` 退出。

### 作为 macOS 应用(终端界面)

双击 `番茄钟.app` 即可,它会打开一个 Terminal 窗口运行番茄钟。可拖入「程序坞」或「应用程序」文件夹。

> 首次打开若被 Gatekeeper 拦截(未签名的本地 App),右键图标 → **打开** → 再点一次「打开」即可。

### 图形界面版(GUI)

用 Python + tkinter 编写的窗口版本(无需额外依赖):

```bash
python3 pomodoro_gui.py
```

或双击 `番茄钟GUI.app`。界面包含圆环倒计时(外圈 Apple 彩虹装饰)、当前阶段、番茄进度圆点,以及 开始 / 暂停 / 重置 / 跳过 按钮。

## 配置

脚本顶部可调整:

```bash
FOCUS_MIN=45            # 默认专注时长
BREAK_MIN=10            # 短休息时长
LONGBREAK_MIN=30        # 长休息时长
SET_SIZE=4              # 每几个番茄进入一次长休息
WWDC_DATE="2026-06-08"  # WWDC 日期,天数自动重算
```

## 项目结构

```
pomodoro            # 终端版番茄钟(Bash 脚本 / Unix 可执行文件)
pomodoro_gui.py     # 图形界面版(Python + tkinter)
番茄钟.app/          # macOS 应用包 —— 终端界面(双击启动)
番茄钟GUI.app/       # macOS 应用包 —— 图形界面(双击启动)
icon/               # 图标素材(png / svg / icns)
```

## 环境要求

- macOS(系统通知与 `.app` 启动依赖 `osascript`;核心计时逻辑为通用 Bash)
- 一个支持 256 色与 Unicode 的终端

## License

MIT
