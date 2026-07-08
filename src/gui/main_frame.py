import tkinter as tk
from tkinter import ttk
from ..core.config import WINDOW_WIDTH, WINDOW_HEIGHT, TITLE

class MainFrame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(TITLE)
        self.geometry(f'{WINDOW_WIDTH}x{WINDOW_HEIGHT}')
        self.resizable(False, False)
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self._setup_styles()
        self.current_view = None
    
    def _setup_styles(self):
        self.style.configure('Title.TLabel', font=('微软雅黑', 24, 'bold'))
        self.style.configure('Subtitle.TLabel', font=('微软雅黑', 14))
        self.style.configure('Normal.TLabel', font=('微软雅黑', 11))
        self.style.configure('Large.TButton', font=('微软雅黑', 12), padding=10)
        self.style.configure('Small.TButton', font=('微软雅黑', 10), padding=5)
        self.style.configure('Evidence.TFrame', background='#f5f5f5')
        self.style.configure('Dialogue.TFrame', background='#e8f4f8')
        self.style.configure('Court.TFrame', background='#f0f4f8')
    
    def show_view(self, view_class, **kwargs):
        if self.current_view:
            self.current_view.destroy()
        self.current_view = view_class(self, **kwargs)
        self.current_view.pack(fill=tk.BOTH, expand=True)
    
    def center_window(self):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - WINDOW_WIDTH) // 2
        y = (screen_height - WINDOW_HEIGHT) // 2
        self.geometry(f'{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}')