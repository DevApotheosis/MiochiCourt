import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from ..core.module_manager import ModuleManager

class ModuleManagerGUI(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.module_manager = ModuleManager()
        self.module_manager.load_modules()
        self._setup_ui()
    
    def _setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        top_frame = ttk.Frame(self, padding=10)
        top_frame.grid(row=0, column=0, sticky='ew')
        
        ttk.Button(top_frame, text='返回主菜单', command=self.on_back).pack(side=tk.LEFT)
        ttk.Label(top_frame, text='模组管理', style='Subtitle.TLabel').pack(side=tk.RIGHT)
        
        main_frame = ttk.Frame(self, padding=10)
        main_frame.grid(row=1, column=0, sticky='nsew')
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        
        self.module_tree = ttk.Treeview(main_frame, columns=('name', 'version', 'author'), 
                                        show='headings', selectmode='browse')
        self.module_tree.heading('name', text='模组名称')
        self.module_tree.heading('version', text='版本')
        self.module_tree.heading('author', text='作者')
        
        self.module_tree.column('name', width=300)
        self.module_tree.column('version', width=100, anchor='center')
        self.module_tree.column('author', width=150)
        
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.module_tree.yview)
        self.module_tree.configure(yscrollcommand=scrollbar.set)
        
        self.module_tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')
        
        self.module_tree.bind('<<TreeviewSelect>>', self.on_module_select)
        
        bottom_frame = ttk.Frame(self, padding=10)
        bottom_frame.grid(row=2, column=0, sticky='ew')
        
        ttk.Button(bottom_frame, text='安装模组', command=self.on_install_module).pack(side=tk.LEFT, padx=10)
        ttk.Button(bottom_frame, text='卸载模组', command=self.on_uninstall_module).pack(side=tk.LEFT, padx=10)
        ttk.Button(bottom_frame, text='查看详情', command=self.on_view_details).pack(side=tk.LEFT, padx=10)
        
        self._load_modules()
    
    def _load_modules(self):
        for item in self.module_tree.get_children():
            self.module_tree.delete(item)
        
        for module in self.module_manager.get_all_modules():
            self.module_tree.insert('', tk.END, iid=module.module_id, 
                                    values=(module.name, module.version, module.author))
    
    def on_module_select(self, event):
        pass
    
    def on_install_module(self):
        module_path = filedialog.askdirectory(title='选择模组目录')
        if not module_path:
            return
        
        if self.module_manager.install_module(module_path):
            self._load_modules()
            messagebox.showinfo('成功', '模组安装成功')
        else:
            messagebox.showerror('失败', '模组安装失败，请检查模组文件')
    
    def on_uninstall_module(self):
        selected = self.module_tree.selection()
        if not selected:
            messagebox.showwarning('警告', '请先选择一个模组')
            return
        
        module_id = selected[0]
        if messagebox.askyesno('确认', f'确定要卸载该模组吗？'):
            if self.module_manager.uninstall_module(module_id):
                self._load_modules()
                messagebox.showinfo('成功', '模组卸载成功')
            else:
                messagebox.showerror('失败', '模组卸载失败')
    
    def on_view_details(self):
        selected = self.module_tree.selection()
        if not selected:
            messagebox.showwarning('警告', '请先选择一个模组')
            return
        
        module_id = selected[0]
        module = self.module_manager.get_module_by_id(module_id)
        
        if module:
            details = f"""模组名称：{module.name}
版本：{module.version}
作者：{module.author}
描述：{module.description}

包含案件：{len(module.cases)}
包含法律：{len(module.laws)}
包含证据：{len(module.evidence)}
包含对话：{len(module.dialogues)}"""
            messagebox.showinfo('模组详情', details)
    
    def on_back(self):
        from .main_menu import MainMenu
        self.parent.show_view(MainMenu)