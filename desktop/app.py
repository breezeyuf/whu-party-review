from __future__ import annotations

import argparse
import logging
import multiprocessing
from pathlib import Path
import queue
import sys
import threading
import time
import traceback

from desktop.runtime import APP_TITLE, AlreadyRunning, Runtime, app_directory


def start_with_progress(runtime):
    import tkinter as tk
    from tkinter import ttk, messagebox
    root = tk.Tk()
    root.title(APP_TITLE)
    root.geometry("520x240")
    root.resizable(False, False)
    root.configure(bg="#f4f6f8")
    root.eval("tk::PlaceWindow . center")
    tk.Label(root, text=APP_TITLE, font=("Microsoft YaHei UI", 19, "bold"), fg="#243342", bg="#f4f6f8").pack(pady=(32, 16))
    status = tk.StringVar(value="正在启动本地工作台…")
    tk.Label(root, textvariable=status, font=("Microsoft YaHei UI", 10), bg="#f4f6f8", fg="#627280").pack()
    bar = ttk.Progressbar(root, mode="indeterminate", length=420)
    bar.pack(pady=22); bar.start(12)
    tk.Label(root, text="材料和账号保存在本机，退出后继续保留。", bg="#f4f6f8", fg="#627280").pack()
    events = queue.Queue()
    runtime.progress = lambda message: events.put(("progress", message))
    done = {"ok": False, "cancel": False}
    def boot():
        try:
            runtime.start(); events.put(("ready", ""))
        except Exception as exc:
            traceback.print_exc(); events.put(("error", exc))
    def cancel():
        done["cancel"] = True
        status.set("正在完成当前操作，请稍候…")
    root.protocol("WM_DELETE_WINDOW", cancel)
    def poll():
        try:
            while True:
                kind, value = events.get_nowait()
                if kind == "progress":
                    if not done["cancel"]: status.set(value)
                else:
                    bar.stop()
                    if kind == "ready": done["ok"] = not done["cancel"]
                    elif not done["cancel"]:
                        if isinstance(value, AlreadyRunning): messagebox.showinfo(APP_TITLE, str(value), parent=root)
                        else: messagebox.showerror("启动失败", f"{value}\n\n日志位置：{runtime.data_dir / 'desktop.log'}", parent=root)
                    root.destroy(); return
        except queue.Empty:
            root.after(100, poll)
    threading.Thread(target=boot, daemon=True).start()
    root.after(100, poll)
    root.mainloop()
    return done["ok"]


def main():
    parser = argparse.ArgumentParser(description=APP_TITLE)
    parser.add_argument("--demo", action="store_true", help="使用独立的虚构演示数据库")
    parser.add_argument("--data-dir", type=Path, help="指定独立数据目录，供备份恢复及测试")
    parser.add_argument("--headless", action="store_true", help="只启动本地服务，供自动化验收")
    parser.add_argument("--smoke-window", action="store_true", help="启动真实桌面窗口后自动关闭，供验收")
    args = parser.parse_args()
    data_dir = args.data_dir or app_directory() / ("demo-data" if args.demo else "data")
    data_dir.mkdir(parents=True, exist_ok=True)
    log_stream = (data_dir / "desktop.log").open("a", encoding="utf-8", buffering=1)
    if sys.stdout is None: sys.stdout = log_stream
    if sys.stderr is None: sys.stderr = log_stream
    logging.basicConfig(stream=log_stream, level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    runtime = Runtime(data_dir, demo=args.demo)
    try:
        if args.headless:
            runtime.start()
            while not (data_dir / "stop.request").exists(): time.sleep(0.25)
            (data_dir / "stop.request").unlink(missing_ok=True)
        elif start_with_progress(runtime):
            import webview
            webview.settings["ALLOW_DOWNLOADS"] = True
            title = APP_TITLE + (" · 演示工作台" if args.demo else " · 本地工作台")
            window = webview.create_window(title, runtime.url, width=1280, height=860, min_size=(760, 560))
            def smoke_window():
                time.sleep(3)
                if args.smoke_window:
                    result = window.evaluate_js("({ title: document.title, login: !!document.querySelector('input[autocomplete=\"username\"]') })")
                    import json
                    (data_dir / "window-check.json").write_text(json.dumps(result), encoding="utf-8")
                    window.destroy()
            webview.start(smoke_window if args.smoke_window else None, gui="edgechromium", private_mode=True,
                          storage_path=str(data_dir / "webview"))
    except AlreadyRunning:
        return 2
    except Exception:
        traceback.print_exc(file=log_stream)
        if not args.headless:
            import ctypes
            ctypes.windll.user32.MessageBoxW(None, f"程序启动失败，请查看：\n{data_dir / 'desktop.log'}", APP_TITLE, 16)
        return 1
    finally:
        runtime.stop()
        log_stream.flush()
    return 0


if __name__ == "__main__":
    multiprocessing.freeze_support()
    raise SystemExit(main())
