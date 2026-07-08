import tkinter as tk
from tkinter import ttk, messagebox
from ..core.config_manager import ConfigManager, DEFAULT_SHORTCUTS


class ShortcutsSettings(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.config_manager = ConfigManager()
        self.shortcuts = self.config_manager.get_shortcuts()
        self.editing_action = None
        self._setup_ui()
    
    def _setup_ui(self):
        self.title('快捷键设置')
        self.geometry('500x400')
        self.resizable(False, False)
        self.focus_set()
        
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text='快捷键配置', font=('微软雅黑', 14, 'bold')).pack(pady=(0, 15))
        
        shortcuts_frame = ttk.Frame(main_frame)
        shortcuts_frame.pack(fill=tk.BOTH, expand=True)
        
        actions = [
            ('收集证据', 'collect_evidence'),
            ('分析证据', 'analyze_evidence'),
            ('询问证人', 'interview_witness'),
            ('搜索法律', 'search_laws'),
            ('返回', 'back'),
            ('进入法庭', 'enter_court'),
            ('取消/退出', 'escape')
        ]
        
        for label, action in actions:
            row_frame = ttk.Frame(shortcuts_frame)
            row_frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(row_frame, text=label, width=12, font=('微软雅黑', 11)).pack(side=tk.LEFT)
            
            key_var = tk.StringVar(value=self._format_key(self.shortcuts[action]))
            key_label = ttk.Label(row_frame, textvariable=key_var, width=15, 
                                  font=('微软雅黑', 11, 'bold'), foreground='#27ae60',
                                  background='#f0f8f0', borderwidth=1, relief='solid')
            key_label.pack(side=tk.LEFT, padx=10)
            
            ttk.Button(row_frame, text='修改', 
                       command=lambda a=action, l=key_label, v=key_var: 
                       self.on_edit_shortcut(a, l, v)).pack(side=tk.RIGHT)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        ttk.Button(button_frame, text='恢复默认', command=self.on_reset).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text='确定', command=self.on_ok).pack(side=tk.RIGHT, padx=10)
    
    def _format_key(self, key):
        key = key.replace('<Control-', 'Ctrl+')
        key = key.replace('<Shift-', 'Shift+')
        key = key.replace('<Alt-', 'Alt+')
        key = key.replace('<Escape>', 'Esc')
        key = key.replace('<Return>', 'Enter')
        key = key.replace('<Tab>', 'Tab')
        key = key.replace('<BackSpace>', 'Backspace')
        key = key.replace('<Delete>', 'Del')
        key = key.replace('<>', '')
        return key
    
    def _parse_key(self, event):
        keys = []
        if event.state & 0x4:
            keys.append('Control')
        if event.state & 0x1:
            keys.append('Shift')
        if event.state & 0x8:
            keys.append('Alt')
        
        key = event.keysym
        if key in ['Control_L', 'Control_R', 'Shift_L', 'Shift_R', 'Alt_L', 'Alt_R']:
            return None
        
        if key == 'Escape':
            keys.append('Escape')
        elif key == 'Return':
            keys.append('Return')
        elif key == 'Tab':
            keys.append('Tab')
        elif key == 'BackSpace':
            keys.append('BackSpace')
        elif key == 'Delete':
            keys.append('Delete')
        elif len(key) == 1:
            keys.append(key.lower())
        else:
            keys.append(key)
        
        if not keys:
            return None
        
        if len(keys) == 1:
            return f'<{keys[0]}>'
        else:
            modifier = keys[0]
            key = keys[-1]
            return f'<{modifier}-{key}>'
    
    def on_edit_shortcut(self, action, label, var):
        self.editing_action = action
        self.editing_label = label
        self.editing_var = var
        
        edit_window = tk.Toplevel(self)
        edit_window.title('设置快捷键')
        edit_window.geometry('350x150')
        edit_window.resizable(False, False)
        edit_window.grab_set()
        
        self.edit_window = edit_window
        
        ttk.Label(edit_window, text=f'请按下新的快捷键（按Esc取消）', 
                  font=('微软雅黑', 12)).pack(pady=20)
        
        edit_window.bind('<Key>', self._on_key_press)
    
    def _on_key_press(self, event):
        key = self._parse_key(event)
        
        if key == '<Escape>':
            self.edit_window.destroy()
            return
        
        if key:
            self.shortcuts[self.editing_action] = key
            self.editing_var.set(self._format_key(key))
            self.config_manager.set_shortcut(self.editing_action, key)
            self.edit_window.destroy()
    
    def on_reset(self):
        if messagebox.askyesno('确认', '确定要恢复所有快捷键为默认值吗？'):
            self.config_manager.reset_shortcuts()
            self.shortcuts = DEFAULT_SHORTCUTS.copy()
            self.destroy()
    
    def on_ok(self):
        self.destroy()