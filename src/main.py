# main.py
import tkinter as tk
from tkinter import ttk, messagebox
from core.event_manager import EventManager
from core.api_client import APIClient
from ui.main_window import CalendarUI
from services.text_watcher import TextSelectionWatcher
from services.tray_icon import TrayIcon

class CalendarApp:
    def __init__(self, root):
        self.root = root
        self.event_manager = EventManager()
        self.api_handler = APIClient()
        self.ui = CalendarUI(root, self.event_manager, self.api_handler)
        self.selection_watcher = TextSelectionWatcher(self.ui)
        self.tray_icon = TrayIcon(self)
        self.minimized_to_tray = False
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self, force_quit=False):
        if not force_quit:
            choice = messagebox.askquestion(
                "退出确认",
                "您确定要退出程序吗？\n选择'否'将最小化到系统托盘",
                icon='question'
            )
            
            if choice == 'yes':
                self._cleanup_and_quit()  # 用户选择退出
            else:
                self.minimize_to_tray()   # 用户选择最小化
        else:
            self._cleanup_and_quit()     # 从托盘菜单强制退出

    def minimize_to_tray(self):
        """最小化到托盘，并确保托盘图标可见"""
        self.minimized_to_tray = True
        self.root.withdraw()  # 隐藏主窗口
        
        # 关键修复：确保托盘图标可见且未停止
        if hasattr(self, 'tray_icon') and self.tray_icon:
            if not self.tray_icon.tray_icon:  # 如果图标未运行，重新初始化
                self.tray_icon.setup_tray_icon()
            self.tray_icon.tray_icon.visible = True  # 强制显示
            
        self.tray_icon.show_notification("智能日历", "程序已最小化到系统托盘")

    def _cleanup_and_quit(self):
        """彻底退出程序，清理资源"""
        self.selection_watcher.running = False
        if hasattr(self.selection_watcher, 'popup') and self.selection_watcher.popup:
            self.selection_watcher.popup.destroy()
        
        self.event_manager.save_events_to_log()
        
        # 关键修复：仅在真正退出时停止托盘图标
        if hasattr(self, 'tray_icon') and self.tray_icon:
            if self.tray_icon.tray_icon:
                self.tray_icon.tray_icon.stop()  # 停止托盘线程
        self.root.quit()


def main():
    try:
        root = tk.Tk()
        style = ttk.Style()
        style.configure('Event.TButton', foreground='red', font=('Arial', 9, 'bold'))
        style.configure('Accent.TButton', foreground='blue')
        app = CalendarApp(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("启动错误", f"程序启动失败: {str(e)}")

if __name__ == "__main__":
    main()
