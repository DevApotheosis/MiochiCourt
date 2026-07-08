import tkinter as tk
from tkinter import ttk, messagebox
from ..core.case_manager import CaseManager
from ..core.law_system import LawSystem
from ..core.save_system import SaveManager
from ..core.character import Character
from ..core.config_manager import ConfigManager

class CaseSelection(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.case_manager = CaseManager()
        self.case_manager.load_cases()
        self.law_system = LawSystem()
        self.law_system.load_laws()
        self.save_manager = SaveManager()
        self.config_manager = ConfigManager()
        self.character = Character(name=self.config_manager.get_player_name())
        self.player_role = self.config_manager.get_player_role()
        self._setup_ui()
    
    def _setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        top_frame = ttk.Frame(self, padding=10)
        top_frame.grid(row=0, column=0, sticky='ew')
        
        ttk.Button(top_frame, text='返回主菜单', command=self.on_back).pack(side=tk.LEFT)
        
        role_frame = ttk.Frame(top_frame)
        role_frame.pack(side=tk.LEFT, padx=20)
        
        ttk.Label(role_frame, text='身份：', font=('微软雅黑', 10)).pack(side=tk.LEFT)
        
        role_display_value = '被告方律师' if self.player_role == 'defense' else '原告方律师'
        self.role_var = tk.StringVar(value=role_display_value)
        self.role_combobox = ttk.Combobox(role_frame, textvariable=self.role_var, 
                                          values=['被告方律师', '原告方律师'], state='readonly', width=12)
        self.role_combobox.pack(side=tk.LEFT)
        self.role_combobox.bind('<<ComboboxSelected>>', self.on_role_change)
        
        role_color = '#27ae60' if self.player_role == 'defense' else '#c0392b'
        self.role_display_label = ttk.Label(role_frame, text=role_display_value, 
                                           font=('微软雅黑', 10, 'bold'), foreground=role_color)
        self.role_display_label.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(top_frame, text='查看法律', command=self.on_view_laws).pack(side=tk.RIGHT, padx=10)
        ttk.Label(top_frame, text='选择案件', style='Subtitle.TLabel').pack(side=tk.RIGHT)
        
        main_frame = ttk.Frame(self, padding=10)
        main_frame.grid(row=1, column=0, sticky='nsew')
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        
        self.case_tree = ttk.Treeview(main_frame, columns=('title', 'difficulty', 'status'), 
                                      show='headings', selectmode='browse')
        self.case_tree.heading('title', text='案件名称')
        self.case_tree.heading('difficulty', text='难度')
        self.case_tree.heading('status', text='状态')
        
        self.case_tree.column('title', width=400)
        self.case_tree.column('difficulty', width=100, anchor='center')
        self.case_tree.column('status', width=100, anchor='center')
        
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.case_tree.yview)
        self.case_tree.configure(yscrollcommand=scrollbar.set)
        
        self.case_tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')
        
        self.case_tree.bind('<<TreeviewSelect>>', self.on_case_select)
        
        bottom_frame = ttk.Frame(self, padding=10)
        bottom_frame.grid(row=2, column=0, sticky='ew')
        
        ttk.Button(bottom_frame, text='开始案件', style='Large.TButton', 
                   command=self.on_start_case).pack(side=tk.RIGHT, padx=10)
        
        self._load_cases()
    
    def _load_cases(self):
        auto_save = self.save_manager.get_save_by_id(SaveManager.AUTO_SAVE_ID)
        case_progress = {}
        if auto_save and auto_save.case_progress:
            case_progress = auto_save.case_progress
        
        for case in self.case_manager.get_all_cases():
            difficulty_label = {1: '简单', 2: '中等', 3: '困难', 4: '专家'}[case.difficulty]
            
            saved_progress = case_progress.get(case.case_id, {})
            if saved_progress.get('status'):
                case.set_status(saved_progress['status'])
                if saved_progress.get('verdict'):
                    case.verdict_guilt = saved_progress['verdict']
            
            status_label = case.get_status_label()
            self.case_tree.insert('', tk.END, iid=case.case_id, 
                                  values=(case.title, difficulty_label, status_label))
    
    def on_case_select(self, event):
        selected = self.case_tree.selection()
        if selected:
            case_id = selected[0]
            case = self.case_manager.get_case_by_id(case_id)
            if case:
                self.show_case_details(case)
    
    def show_case_details(self, case):
        details = f"""案件：{case.title}
被告：{case.defendant}
原告：{case.plaintiff}
地点：{case.location}
时间：{case.time}
难度：{'简单' if case.difficulty == 1 else '中等' if case.difficulty == 2 else '困难' if case.difficulty == 3 else '专家'}

{case.description}"""
        messagebox.showinfo('案件详情', details)
    
    def on_start_case(self):
        selected = self.case_tree.selection()
        if not selected:
            messagebox.showwarning('警告', '请先选择一个案件')
            return
        
        case_id = selected[0]
        case = self.case_manager.get_case_by_id(case_id)
        
        if case.status == 'completed':
            if not messagebox.askyesno('确认重玩', '该案件已完成，确定要重新开始吗？'):
                return
        
        self.case_manager.set_current_case(case_id)
        
        if case.status == 'completed':
            case.status = 'investigation'
            case.verdict_guilt = None
            case.verdict_reason = None
            case.evidence_manager.reset_evidence()
        
        self.save_manager.auto_save(
            player_name=self.character.name,
            current_case_id=case_id,
            case_status='investigation',
            evidence_collected=[],
            evidence_analyzed=[],
            witness_trust={},
            dialogue_history=[],
            game_time=0,
            player_data=self.character.to_dict(),
            case_progress={case_id: {'status': 'investigation', 'evidence_collected': [], 'evidence_analyzed': []}}
        )
        
        from .investigation_view import InvestigationView
        self.parent.show_view(InvestigationView, case_manager=self.case_manager, 
                              law_system=self.law_system, save_manager=self.save_manager,
                              character=self.character, player_role=self.player_role)
    
    def on_view_laws(self):
        from .law_viewer import LawViewer
        LawViewer(self, self.law_system)
    
    def on_back(self):
        from .main_menu import MainMenu
        self.parent.show_view(MainMenu)
    
    def on_role_change(self, event):
        display_value = self.role_var.get()
        self.player_role = 'defense' if display_value == '被告方律师' else 'prosecution'
        self.config_manager.set_player_role(self.player_role)
        role_color = '#27ae60' if self.player_role == 'defense' else '#c0392b'
        self.role_display_label.config(text=display_value, foreground=role_color)