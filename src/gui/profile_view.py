import tkinter as tk
from tkinter import ttk, messagebox
from ..core.save_system import SaveManager
from ..core.character import Character
from ..core.achievements import AchievementManager
from ..core.dossier_system import DossierManager
from ..core.config_manager import ConfigManager

class ProfileView(tk.Toplevel):
    def __init__(self, parent, character=None):
        super().__init__(parent)
        self.parent = parent
        self.title('用户中心')
        self.geometry('800x600')
        self.save_manager = SaveManager()
        self.config_manager = ConfigManager()
        self.character = character or Character(name=self.config_manager.get_player_name())
        self.achievement_manager = AchievementManager()
        self.achievement_manager.load_from_file(self.character.name)
        self._setup_ui()
    
    def _setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        notebook = ttk.Notebook(self)
        notebook.grid(row=0, column=0, sticky='nsew')
        
        profile_tab = ttk.Frame(notebook)
        saves_tab = ttk.Frame(notebook)
        dossiers_tab = ttk.Frame(notebook)
        
        notebook.add(profile_tab, text='个人信息')
        notebook.add(saves_tab, text='存档管理')
        notebook.add(dossiers_tab, text='卷宗管理')
        
        self._setup_profile_tab(profile_tab)
        self._setup_saves_tab(saves_tab)
        self._setup_dossiers_tab(dossiers_tab)
    
    def _setup_profile_tab(self, parent):
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=0)
        parent.grid_rowconfigure(1, weight=0)
        parent.grid_rowconfigure(2, weight=1)
        
        header_frame = ttk.Frame(parent, padding=20)
        header_frame.grid(row=0, column=0, sticky='nsew')
        
        name_frame = ttk.Frame(header_frame)
        name_frame.pack(side=tk.LEFT)
        
        ttk.Label(name_frame, text='玩家：', style='Title.TLabel').pack(side=tk.LEFT)
        self.name_var = tk.StringVar(value=self.character.name)
        self.name_entry = ttk.Entry(name_frame, textvariable=self.name_var, font=('微软雅黑', 14), width=15)
        self.name_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(name_frame, text='修改', command=self._change_name).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(header_frame, text=f'等级：{self.character.level}', style='Subtitle.TLabel').pack(side=tk.RIGHT)
        
        rank_frame = ttk.Frame(parent, padding=(20, 0, 20, 10))
        rank_frame.grid(row=1, column=0, sticky='nsew')
        
        rank = self.character.get_lawyer_rank()
        rank_index = self.character.get_rank_index()
        rank_names = [r['name'] for r in self.character.LAWYER_LEVELS]
        ttk.Label(rank_frame, text=f'律师等级：{rank}', font=('微软雅黑', 12, 'bold'), foreground='#2c3e50').pack(side=tk.LEFT)
        ttk.Label(rank_frame, text=f'（{rank_index + 1}/{len(rank_names)}）', font=('微软雅黑', 10), foreground='#7f8c8d').pack(side=tk.LEFT, padx=5)
        
        exp_current, exp_total = self.character.get_exp_progress()
        exp_frame = ttk.Frame(parent, padding=(20, 0, 20, 20))
        exp_frame.grid(row=2, column=0, sticky='nsew')
        
        ttk.Label(exp_frame, text=f'经验值：{exp_current}/{exp_total}').pack(side=tk.LEFT)
        progress_bar = ttk.Progressbar(exp_frame, length=200, mode='determinate')
        progress_bar['value'] = (exp_current / exp_total) * 100 if exp_total > 0 else 0
        progress_bar.pack(side=tk.RIGHT, padx=10)
        
        skills_frame = ttk.Frame(parent, padding=(20, 0, 20, 20))
        skills_frame.grid(row=3, column=0, sticky='nsew')
        
        ttk.Label(skills_frame, text='技能等级', style='Subtitle.TLabel').pack(pady=(0, 10))
        
        skill_grid = ttk.Frame(skills_frame)
        skill_grid.pack(fill=tk.BOTH, expand=True)
        
        for i, skill in enumerate(self.character.get_all_skills()):
            skill_frame = ttk.Frame(skill_grid, borderwidth=1, relief=tk.SUNKEN, padding=10)
            skill_frame.grid(row=i // 2, column=i % 2, padx=10, pady=5, sticky='ew')
            
            ttk.Label(skill_frame, text=f'{skill.name}', font=('微软雅黑', 11, 'bold')).pack(side=tk.LEFT)
            ttk.Label(skill_frame, text=f'Lv.{skill.level}/{skill.max_level}', font=('微软雅黑', 11)).pack(side=tk.RIGHT)
            
            effect = skill.get_effect()
            effect_text = ', '.join([f'{k}: +{v}' for k, v in effect.items()])
            ttk.Label(skill_frame, text=effect_text, font=('微软雅黑', 9), foreground='#7f8c8d').pack(side=tk.BOTTOM, pady=(5, 0))
        
        stats_frame = ttk.Frame(parent, padding=(20, 0, 20, 20))
        stats_frame.grid(row=3, column=0, sticky='nsew')
        
        ttk.Label(stats_frame, text='游戏统计', style='Subtitle.TLabel').pack(pady=(0, 10))
        
        stats = [
            ('已完成案件', self.character.stats.get('cases_completed', 0)),
            ('收集证据', self.character.stats.get('evidence_collected', 0)),
            ('分析证据', self.character.stats.get('evidence_analyzed', 0)),
            ('询问证人', self.character.stats.get('witnesses_interviewed', 0)),
            ('引用法律', self.character.stats.get('laws_referenced', 0)),
            ('游戏时长', f'{self.character.stats.get("total_game_time", 0)}分钟')
        ]
        
        for stat_name, stat_value in stats:
            stat_frame = ttk.Frame(stats_frame)
            stat_frame.pack(fill=tk.X, pady=3)
            ttk.Label(stat_frame, text=stat_name, width=15).pack(side=tk.LEFT)
            ttk.Label(stat_frame, text=str(stat_value), font=('微软雅黑', 11, 'bold')).pack(side=tk.RIGHT)
    
    def _setup_saves_tab(self, parent):
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=0)
        
        save_tree = ttk.Treeview(parent, columns=('id', 'case', 'status', 'updated'), 
                                  show='headings', selectmode='browse')
        save_tree.heading('id', text='存档ID')
        save_tree.heading('case', text='案件')
        save_tree.heading('status', text='状态')
        save_tree.heading('updated', text='更新时间')
        
        save_tree.column('id', width=150)
        save_tree.column('case', width=200)
        save_tree.column('status', width=100)
        save_tree.column('updated', width=200)
        
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=save_tree.yview)
        save_tree.configure(yscrollcommand=scrollbar.set)
        
        save_tree.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        scrollbar.grid(row=0, column=1, sticky='ns')
        
        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=1, column=0, sticky='ew', padx=10, pady=10)
        
        ttk.Button(btn_frame, text='读取存档', command=lambda: self._load_save(save_tree)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text='删除存档', command=lambda: self._delete_save(save_tree)).pack(side=tk.LEFT, padx=5)
        
        self._load_saves(save_tree)
    
    def _load_saves(self, tree):
        for item in tree.get_children():
            tree.delete(item)
        
        saves = self.save_manager.get_all_saves()
        for save in saves:
            case_name = save.current_case_id if save.current_case_id else '无'
            status = {'investigation': '调查中', 'court': '庭审中', 'completed': '已完成'}.get(save.case_status, save.case_status)
            tree.insert('', tk.END, iid=save.save_id, 
                         values=(save.save_id, case_name, status, save.updated_at))
    
    def _load_save(self, tree):
        selected = tree.selection()
        if selected:
            save_id = selected[0]
            save = self.save_manager.load_game(save_id)
            if save:
                messagebox.showinfo('读取成功', f'已读取存档：{save_id}')
            else:
                messagebox.showwarning('警告', '读取存档失败')
    
    def _delete_save(self, tree):
        selected = tree.selection()
        if selected:
            save_id = selected[0]
            if messagebox.askyesno('确认删除', f'确定要删除存档 {save_id} 吗？'):
                if self.save_manager.delete_save(save_id):
                    self._load_saves(tree)
                    messagebox.showinfo('删除成功', '存档已删除')
                else:
                    messagebox.showwarning('警告', '删除存档失败')
    
    def _setup_dossiers_tab(self, parent):
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=0)
        
        self.dossier_tree = ttk.Treeview(parent, columns=('id', 'case', 'verdict', 'date'), 
                                           show='headings', selectmode='browse')
        self.dossier_tree.heading('id', text='卷宗编号')
        self.dossier_tree.heading('case', text='案件名称')
        self.dossier_tree.heading('verdict', text='判决结果')
        self.dossier_tree.heading('date', text='创建时间')
        
        self.dossier_tree.column('id', width=150)
        self.dossier_tree.column('case', width=250)
        self.dossier_tree.column('verdict', width=100)
        self.dossier_tree.column('date', width=200)
        
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.dossier_tree.yview)
        self.dossier_tree.configure(yscrollcommand=scrollbar.set)
        
        self.dossier_tree.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        scrollbar.grid(row=0, column=1, sticky='ns')
        
        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=1, column=0, sticky='ew', padx=10, pady=10)
        
        ttk.Button(btn_frame, text='查看详情', command=self._view_dossier).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text='删除卷宗', command=self._delete_dossier).pack(side=tk.LEFT, padx=5)
        
        self._load_dossiers()
    
    def _load_dossiers(self):
        for item in self.dossier_tree.get_children():
            self.dossier_tree.delete(item)
        
        dossier_manager = DossierManager()
        dossiers = dossier_manager.get_dossiers_by_player(self.character.name)
        
        for dossier in dossiers:
            verdict = '无罪' if dossier.verdict == 'innocent' else '有罪'
            verdict_color = '#27ae60' if dossier.verdict == 'innocent' else '#c0392b'
            
            self.dossier_tree.insert('', tk.END, iid=dossier.dossier_id,
                                     values=(dossier.dossier_id, dossier.case_title, verdict, dossier.created_at))
            self.dossier_tree.tag_configure(dossier.dossier_id, foreground=verdict_color)
    
    def _view_dossier(self):
        selected = self.dossier_tree.selection()
        if not selected:
            messagebox.showwarning('警告', '请先选择一个卷宗')
            return
        
        dossier_id = selected[0]
        dossier_manager = DossierManager()
        dossier = dossier_manager.load_dossier(dossier_id)
        
        if dossier:
            details = f"""卷宗编号：{dossier.dossier_id}
案件名称：{dossier.case_title}
案件ID：{dossier.case_id}
判决结果：{'无罪' if dossier.verdict == 'innocent' else '有罪'}
法官态度：{dossier.judge_mood}/100

【审判评分】
证据分：{dossier.trial_scores.get('evidence_points', 0)}
法律分：{dossier.trial_scores.get('law_points', 0)}
证言分：{dossier.trial_scores.get('witness_points', 0)}
总分：{dossier.trial_scores.get('total', 0)}

【证据链】
"""
            for ev in dossier.evidence_chain:
                details += f"- {ev['name']} {'(已分析)' if ev.get('analyzed') else ''}\n"
            
            details += f"""
【判决理由】
{dossier.verdict_reason}

创建时间：{dossier.created_at}"""
            
            messagebox.showinfo('卷宗详情', details)
        else:
            messagebox.showwarning('警告', '无法加载卷宗')
    
    def _delete_dossier(self):
        selected = self.dossier_tree.selection()
        if not selected:
            messagebox.showwarning('警告', '请先选择一个卷宗')
            return
        
        dossier_id = selected[0]
        if messagebox.askyesno('确认删除', f'确定要删除卷宗 {dossier_id} 吗？'):
            dossier_manager = DossierManager()
            if dossier_manager.delete_dossier(dossier_id):
                self._load_dossiers()
                messagebox.showinfo('删除成功', '卷宗已删除')
            else:
                messagebox.showwarning('警告', '删除卷宗失败')
    
    def _change_name(self):
        new_name = self.name_var.get().strip()
        if new_name and new_name != self.character.name:
            old_name = self.character.name
            self.character.name = new_name
            self.config_manager.set_player_name(new_name)
            messagebox.showinfo('成功', f'名称已修改为：{new_name}')
        elif not new_name:
            messagebox.showwarning('警告', '名称不能为空')
        else:
            messagebox.showinfo('提示', '名称未变化')