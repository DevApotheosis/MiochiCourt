import tkinter as tk
from tkinter import ttk, messagebox
from ..core.law_system import LawSystem
from ..core.achievements import AchievementManager
from ..core.character import Character
from ..core.save_system import SaveManager
from ..core.config_manager import ConfigManager

class MainMenu(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.law_system = LawSystem()
        self.law_system.load_laws()
        self.achievement_manager = AchievementManager()
        self.save_manager = SaveManager()
        self.config_manager = ConfigManager()
        
        saved_name = self.config_manager.get_player_name()
        self.character = Character(name=saved_name)
        self.achievement_manager.load_from_file(saved_name)
        
        self._setup_ui()
    
    def _setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        top_bar = ttk.Frame(self, padding=10)
        top_bar.grid(row=0, column=0, sticky='ew')
        top_bar.grid_columnconfigure(0, weight=1)
        top_bar.grid_columnconfigure(1, weight=0)
        
        ttk.Label(top_bar, text='澪地审判庭', style='Title.TLabel').grid(row=0, column=0, sticky='w')
        
        user_frame = ttk.Frame(top_bar)
        user_frame.grid(row=0, column=1, sticky='e')
        
        ttk.Button(user_frame, text='🏆 成就', command=self.on_view_achievements).pack(side=tk.LEFT, padx=5)
        ttk.Button(user_frame, text='👤 个人中心', command=self.on_view_profile).pack(side=tk.LEFT, padx=5)
        
        content_frame = ttk.Frame(self, padding=50)
        content_frame.grid(row=1, column=0, sticky='nsew')
        content_frame.grid_columnconfigure(0, weight=1)
        
        subtitle_label = ttk.Label(content_frame, text='白帽黑客的法庭之战', style='Subtitle.TLabel')
        subtitle_label.grid(row=0, column=0, pady=(0, 50))
        
        button_frame = ttk.Frame(content_frame)
        button_frame.grid(row=1, column=0)
        button_frame.grid_columnconfigure(0, weight=1)
        
        btn_start = ttk.Button(button_frame, text='开始游戏', style='Large.TButton', 
                               command=self.on_start_game)
        btn_start.grid(row=0, column=0, pady=10, sticky='ew')
        
        btn_modules = ttk.Button(button_frame, text='加载模组', style='Large.TButton', 
                                 command=self.on_load_modules)
        btn_modules.grid(row=1, column=0, pady=10, sticky='ew')
        
        btn_laws = ttk.Button(button_frame, text='查看法律', style='Large.TButton', 
                               command=self.on_view_laws)
        btn_laws.grid(row=2, column=0, pady=10, sticky='ew')
        
        btn_about = ttk.Button(button_frame, text='关于游戏', style='Large.TButton', 
                               command=self.on_about)
        btn_about.grid(row=3, column=0, pady=10, sticky='ew')
        
        btn_exit = ttk.Button(button_frame, text='退出游戏', style='Large.TButton', 
                              command=self.on_exit)
        btn_exit.grid(row=4, column=0, pady=10, sticky='ew')
    
    def on_start_game(self):
        saved_name = self.config_manager.get_player_name()
        if saved_name:
            self.character.name = saved_name
        else:
            self.character.name = '玩家'
            self.config_manager.set_player_name('玩家')
        
        self.achievement_manager.load_from_file(self.character.name)
        
        existing_save = self.save_manager.get_save_by_id(SaveManager.AUTO_SAVE_ID)
        existing_progress = existing_save.case_progress if existing_save else {}
        
        self.save_manager.auto_save(
            player_name=self.character.name,
            current_case_id=None,
            case_status='investigation',
            evidence_collected=[],
            evidence_analyzed=[],
            witness_trust={},
            dialogue_history=[],
            game_time=0,
            player_data=self.character.to_dict(),
            case_progress=existing_progress
        )
        
        from .case_selection import CaseSelection
        self.parent.show_view(CaseSelection)
    
    def on_load_modules(self):
        from .module_manager_gui import ModuleManagerGUI
        self.parent.show_view(ModuleManagerGUI)
    
    def on_view_laws(self):
        from .law_viewer import LawViewer
        LawViewer(self, self.law_system)
    
    def on_view_achievements(self):
        from .achievement_view import AchievementView
        AchievementView(self, self.achievement_manager)
    
    def on_view_profile(self):
        from .profile_view import ProfileView
        ProfileView(self)
    
    def on_about(self):
        about_text = """
澪地审判庭

通过收集证据（实物、文档、音频、视频、证言），
在澪地审判庭依据相关法律法规，
顺利完成辩护或诉讼。

Copyright©️2026 DevApotheosis
        """
        messagebox.showinfo('关于游戏', about_text)
    
    def on_exit(self):
        if messagebox.askyesno('退出游戏', '确定要退出游戏吗？'):
            self.parent.destroy()