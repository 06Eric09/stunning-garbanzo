# tray_icon.py
import platform
import threading
import pystray
from PIL import Image
import win10toast

class TrayIcon:
    def __init__(self, app):
        self.app = app
        self.tray_icon = None
        self.setup_tray_icon()

    def setup_tray_icon(self):
        if platform.system() == "Windows":
            image = Image.new('RGB', (64, 64), 'white')
            
            menu = pystray.Menu(
                pystray.MenuItem('显示', self.restore_from_tray),
                pystray.MenuItem('退出', self.quit_application)
            )
            
            self.tray_icon = pystray.Icon(
                "calendar_app",
                image,
                "智能日历",
                menu
            )
            
            threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def restore_from_tray(self, icon, item):
        self.app.root.after(0, self._restore_window)

    def _restore_window(self):
        self.app.root.deiconify()
        self.app.root.state('normal')
        if self.tray_icon:
            self.tray_icon.visible = False

    def quit_application(self, icon, item):
        self.app.root.after(0, self._quit_app)

    def _quit_app(self):
        self.app.on_close(force_quit=True)
        if self.tray_icon:
            self.tray_icon.stop()
        self.app.root.destroy()

    def show_notification(self, title, message):
        if platform.system() == "Windows":
            try:
                toaster = win10toast.ToastNotifier()
                toaster.show_toast(
                    title,
                    message,
                    duration=3,
                    threaded=True
                )
            except ImportError:
                pass
