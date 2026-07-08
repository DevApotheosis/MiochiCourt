import tkinter as tk
from tkinter import ttk, messagebox

class AchievementView(tk.Toplevel):
    def __init__(self, parent, achievement_manager):
        super().__init__(parent)
        self.parent = parent
        self.achievement_manager = achievement_manager
        self.title('成就系统')
        self.geometry('600x500')
        self._setup_ui()
    
    def _setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        
        header_frame = ttk.Frame(self, padding=10)
        header_frame.grid(row=0, column=0, sticky='ew')
        
        unlocked, total = self.achievement_manager.get_progress()
        ttk.Label(header_frame, text=f'成就进度：{unlocked}/{total}', style='Title.TLabel').pack(side=tk.LEFT)
        
        progress_bar = ttk.Progressbar(header_frame, length=200, mode='determinate')
        progress_bar['value'] = (unlocked / total) * 100 if total > 0 else 0
        progress_bar.pack(side=tk.RIGHT, padx=10)
        
        main_frame = ttk.Frame(self)
        main_frame.grid(row=1, column=0, sticky='nsew', padx=10, pady=10)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        
        self.achievement_tree = ttk.Treeview(main_frame, columns=('name', 'description', 'status'), 
                                              show='headings', selectmode='browse')
        self.achievement_tree.heading('name', text='成就名称')
        self.achievement_tree.heading('description', text='描述')
        self.achievement_tree.heading('status', text='状态')
        
        self.achievement_tree.column('name', width=150)
        self.achievement_tree.column('description', width=300)
        self.achievement_tree.column('status', width=100, anchor='center')
        
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.achievement_tree.yview)
        self.achievement_tree.configure(yscrollcommand=scrollbar.set)
        
        self.achievement_tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')
        
        self._load_achievements()
    
    def _load_achievements(self):
        for item in self.achievement_tree.get_children():
            self.achievement_tree.delete(item)
        
        for achievement in self.achievement_manager.achievements.values():
            status = '✅ 已解锁' if achievement.unlocked else '🔒 未解锁'
            tags = ('unlocked',) if achievement.unlocked else ('locked',)
            
            self.achievement_tree.insert('', tk.END, 
                                         values=(achievement.name, 
                                                 achievement.description, 
                                                 status),
                                         tags=tags)
        
        self.achievement_tree.tag_configure('unlocked', foreground='#27ae60')
        self.achievement_tree.tag_configure('locked', foreground='#95a5a6')