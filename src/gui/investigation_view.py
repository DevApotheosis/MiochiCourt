import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
from ..core.dialogue import DialogueManager
from ..core.config import IMAGES_DIR, DEFAULT_EVIDENCE_IMAGE
from ..core.save_system import SaveManager
from ..core.character import Character

class InvestigationView(tk.Frame):
    def __init__(self, parent, case_manager, law_system, save_manager=None, character=None, player_role='defense'):
        super().__init__(parent)
        self.parent = parent
        self.case_manager = case_manager
        self.law_system = law_system
        self.save_manager = save_manager or SaveManager()
        self.character = character or Character()
        self.player_role = player_role
        self.dialogue_manager = DialogueManager()
        self.current_case = case_manager.get_current_case()
        self.current_witness = None
        self.witness_trust = {}
        self.analyzed_evidence_ids = set()
        self.interviewed_witnesses = set()
        self.dialogue_history = {}
        
        if self.current_case:
            self.dialogue_manager.load_dialogues(self.current_case.case_id)
            for witness in self.current_case.witnesses:
                self.witness_trust[witness] = 50
                self.dialogue_history[witness] = []
        
        self._load_progress()
        self._setup_ui()
    
    def _load_progress(self):
        auto_save = self.save_manager.get_save_by_id(SaveManager.AUTO_SAVE_ID)
        if auto_save and auto_save.case_progress:
            case_progress = auto_save.case_progress.get(self.current_case.case_id, {})
            self.analyzed_evidence_ids = set(case_progress.get('analyzed_evidence_ids', []))
            self.interviewed_witnesses = set(case_progress.get('interviewed_witnesses', []))
            self.dialogue_history = case_progress.get('dialogue_history', {})
            
            if self.current_case:
                for witness in self.current_case.witnesses:
                    if witness not in self.dialogue_history:
                        self.dialogue_history[witness] = []
                    if witness not in self.witness_trust:
                        self.witness_trust[witness] = 50
    
    def _save_progress(self):
        if self.current_case:
            case_progress = {
                'status': self.current_case.status,
                'evidence_collected': [e.evidence_id for e in self.current_case.evidence_manager.get_collected_evidence()],
                'evidence_analyzed': [e.evidence_id for e in self.current_case.evidence_manager.get_analyzed_evidence()],
                'analyzed_evidence_ids': list(self.analyzed_evidence_ids),
                'interviewed_witnesses': list(self.interviewed_witnesses),
                'dialogue_history': self.dialogue_history
            }
            
            existing_save = self.save_manager.get_save_by_id(SaveManager.AUTO_SAVE_ID)
            existing_progress = existing_save.case_progress if existing_save else {}
            existing_progress[self.current_case.case_id] = case_progress
            
            self.save_manager.auto_save(
                player_name=self.character.name,
                current_case_id=self.current_case.case_id,
                case_status=self.current_case.status,
                evidence_collected=[e.evidence_id for e in self.current_case.evidence_manager.get_collected_evidence()],
                evidence_analyzed=[e.evidence_id for e in self.current_case.evidence_manager.get_analyzed_evidence()],
                witness_trust=self.witness_trust,
                dialogue_history=[],
                game_time=0,
                player_data=self.character.to_dict(),
                case_progress=existing_progress
            )
    
    def _setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        main_paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_paned.grid(row=0, column=0, sticky='nsew')
        
        left_frame = ttk.Frame(main_paned, width=300)
        right_frame = ttk.Frame(main_paned, width=600)
        
        main_paned.add(left_frame, weight=1)
        main_paned.add(right_frame, weight=2)
        
        self._setup_left_panel(left_frame)
        self._setup_right_panel(right_frame)
        
        self._setup_shortcuts()
    
    def _setup_left_panel(self, parent):
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=1)
        
        notebook = ttk.Notebook(parent)
        notebook.grid(row=0, column=0, sticky='nsew')
        
        evidence_tab = ttk.Frame(notebook)
        witnesses_tab = ttk.Frame(notebook)
        laws_tab = ttk.Frame(notebook)
        
        notebook.add(evidence_tab, text='证据')
        notebook.add(witnesses_tab, text='证人')
        notebook.add(laws_tab, text='法律')
        
        self._setup_evidence_tab(evidence_tab)
        self._setup_witnesses_tab(witnesses_tab)
        self._setup_laws_tab(laws_tab)
    
    def _setup_evidence_tab(self, parent):
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=1)
        
        self.evidence_listbox = tk.Listbox(parent, font=('微软雅黑', 10))
        self.evidence_listbox.grid(row=0, column=0, sticky='nsew')
        
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.evidence_listbox.yview)
        self.evidence_listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky='ns')
        
        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=1, column=0, sticky='ew', pady=5)
        
        ttk.Button(btn_frame, text='收集证据', command=self.on_collect_evidence).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text='分析证据', command=self.on_analyze_evidence).pack(side=tk.LEFT, padx=5)
        
        self._update_evidence_list()
    
    def _update_evidence_list(self):
        self.evidence_listbox.delete(0, tk.END)
        if self.current_case:
            for evidence in self.current_case.evidence_manager.evidence_list:
                status = '[已收集]' if evidence.collected else '[未收集]'
                analyzed = '[已分析]' if evidence.evidence_id in self.analyzed_evidence_ids else ''
                key = '[关键]' if evidence.is_key else ''
                self.evidence_listbox.insert(tk.END, f'{status} {analyzed} {key} {evidence.name}')
    
    def _update_witness_list(self):
        self.witness_listbox.delete(0, tk.END)
        if self.current_case:
            for witness in self.current_case.witnesses:
                interviewed = '[已询问]' if witness in self.interviewed_witnesses else ''
                self.witness_listbox.insert(tk.END, f'{interviewed} {witness}')
    
    def _setup_witnesses_tab(self, parent):
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=1)
        
        self.witness_listbox = tk.Listbox(parent, font=('微软雅黑', 10))
        self.witness_listbox.grid(row=0, column=0, sticky='nsew')
        
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.witness_listbox.yview)
        self.witness_listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky='ns')
        
        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=1, column=0, sticky='ew', pady=5)
        
        ttk.Button(btn_frame, text='询问证人', command=self.on_interview_witness).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text='显示信任度', command=self.on_show_trust).pack(side=tk.LEFT, padx=5)
        
        if self.current_case:
            for witness in self.current_case.witnesses:
                interviewed = '[已询问]' if witness in self.interviewed_witnesses else ''
                self.witness_listbox.insert(tk.END, f'{interviewed} {witness}')
    
    def _setup_laws_tab(self, parent):
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)
        
        search_frame = ttk.Frame(parent)
        search_frame.grid(row=0, column=0, sticky='ew', pady=5)
        
        ttk.Label(search_frame, text='搜索法律：').pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.search_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(search_frame, text='搜索', command=self.on_search_laws).pack(side=tk.RIGHT)
        
        self.laws_listbox = tk.Listbox(parent, font=('微软雅黑', 10))
        self.laws_listbox.grid(row=1, column=0, sticky='nsew')
        
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.laws_listbox.yview)
        self.laws_listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=1, column=1, sticky='ns')
        
        ttk.Button(parent, text='查看详情', command=self.on_view_law_detail).grid(row=2, column=0, sticky='ew', pady=5)
        
        self._load_all_laws()
    
    def _load_all_laws(self):
        self.laws_listbox.delete(0, tk.END)
        for law in self.law_system.laws.values():
            self.laws_listbox.insert(tk.END, f'{law.title} - {law.category}')
    
    def _setup_right_panel(self, parent):
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=4)
        parent.grid_rowconfigure(2, weight=1)
        
        image_frame = ttk.Frame(parent)
        image_frame.grid(row=0, column=0, sticky='nsew', pady=(0, 5))
        image_frame.grid_columnconfigure(0, weight=1)
        image_frame.grid_rowconfigure(0, weight=1)
        
        self.evidence_image_label = ttk.Label(image_frame)
        self.evidence_image_label.grid(row=0, column=0)
        
        self.info_text = tk.Text(parent, wrap=tk.WORD, font=('微软雅黑', 11), state=tk.DISABLED)
        self.info_text.grid(row=1, column=0, sticky='nsew')
        self.info_text.bind('<MouseWheel>', self._on_mouse_wheel)
        
        action_frame = ttk.Frame(parent)
        action_frame.grid(row=2, column=0, sticky='ew', pady=10)
        
        ttk.Button(action_frame, text='返回案件选择', command=self.on_back).pack(side=tk.LEFT, padx=10)
        ttk.Button(action_frame, text='进入法庭', command=self.on_enter_court).pack(side=tk.RIGHT, padx=10)
    
    def _set_info_text(self, text):
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, text)
        self.info_text.config(state=tk.DISABLED)
    
    def _show_evidence_image(self, evidence):
        image_path = evidence.details.get('image_path')
        
        if image_path and os.path.exists(image_path):
            img_path = image_path
        else:
            img_path = DEFAULT_EVIDENCE_IMAGE
        
        if os.path.exists(img_path):
            try:
                image = Image.open(img_path)
                max_width = 580
                max_height = 150
                
                width, height = image.size
                if width > max_width or height > max_height:
                    ratio = min(max_width / width, max_height / height)
                    width = int(width * ratio)
                    height = int(height * ratio)
                    image = image.resize((width, height), Image.Resampling.LANCZOS)
                
                photo = ImageTk.PhotoImage(image)
                self.evidence_image_label.config(image=photo)
                self.evidence_image_label.image = photo
                return
            except Exception as e:
                pass
        
        self.evidence_image_label.config(image='')
        self.evidence_image_label.image = None
    
    def _append_info_text(self, text):
        self.info_text.config(state=tk.NORMAL)
        self.info_text.insert(tk.END, '\n' + text)
        self.info_text.see(tk.END)
        self.info_text.config(state=tk.DISABLED)
    
    def on_collect_evidence(self):
        selected = self.evidence_listbox.curselection()
        if not selected:
            messagebox.showwarning('警告', '请选择要收集的证据')
            return
        
        index = selected[0]
        evidence = self.current_case.evidence_manager.evidence_list[index]
        
        if evidence.collected:
            display_content = self._generate_evidence_display(evidence)
            self._set_info_text(display_content)
            self._show_evidence_image(evidence)
            return
        
        self.current_case.evidence_manager.collect_evidence(evidence.evidence_id)
        self._update_evidence_list()
        
        for i, ev in enumerate(self.current_case.evidence_manager.evidence_list):
            if ev.evidence_id == evidence.evidence_id:
                self.evidence_listbox.selection_clear(0, tk.END)
                self.evidence_listbox.selection_set(i)
                self.evidence_listbox.see(i)
                self.evidence_listbox.focus_set()
                break
        
        self.character.update_stat('evidence_collected', 1)
        self.character.add_experience(10)
        
        existing_save = self.save_manager.get_save_by_id(SaveManager.AUTO_SAVE_ID)
        existing_progress = existing_save.case_progress if existing_save else {}
        existing_progress[self.current_case.case_id] = {
            'status': 'investigation', 
            'evidence_collected': [e.evidence_id for e in self.current_case.evidence_manager.get_collected_evidence()],
            'evidence_analyzed': [e.evidence_id for e in self.current_case.evidence_manager.get_analyzed_evidence()]
        }
        
        self.save_manager.auto_save(
            player_name=self.character.name,
            current_case_id=self.current_case.case_id,
            case_status='investigation',
            evidence_collected=[e.evidence_id for e in self.current_case.evidence_manager.get_collected_evidence()],
            evidence_analyzed=[e.evidence_id for e in self.current_case.evidence_manager.get_analyzed_evidence()],
            witness_trust=self.witness_trust,
            dialogue_history=[],
            game_time=0,
            player_data=self.character.to_dict(),
            case_progress=existing_progress
        )
        
        display_content = self._generate_evidence_display(evidence)
        self._set_info_text(display_content)
        self._show_evidence_image(evidence)
        messagebox.showinfo('成功', f'已收集证据：{evidence.name}')
    
    def _generate_evidence_display(self, evidence):
        base_info = f'【证据详情】\n\n名称：{evidence.name}\n类型：{evidence.get_type_label()}\n发现地点：{evidence.location}\n\n{evidence.description}\n\n'
        
        if evidence.evidence_type == 'document':
            if evidence.details.get('format') == 'CSV':
                base_info += '【数据预览】\n\n'
                base_info += '时间戳,IP地址,操作类型,用户ID\n'
                base_info += '2026-07-15 00:12:34,192.168.1.100,登录,user_001\n'
                base_info += '2026-07-15 00:15:22,192.168.1.100,查询,user_001\n'
                base_info += '2026-07-15 00:18:45,192.168.1.100,转账,user_001\n'
                base_info += '...\n\n【分析提示】查看异常访问模式和时间间隔'
            elif evidence.details.get('format') == 'JSON':
                base_info += '【代码/数据预览】\n\n'
                base_info += '{\n'
                base_info += '  "transaction_id": "TXN_20260715_001",\n'
                base_info += '  "amount": 5000000,\n'
                base_info += '  "currency": "澪币",\n'
                base_info += '  "from_account": "0x7f3a...",\n'
                base_info += '  "to_account": "0x9e2b...",\n'
                base_info += '  "timestamp": "2026-07-15T00:20:00Z",\n'
                base_info += '  "status": "completed"\n'
                base_info += '}\n\n【分析提示】追踪资金流向和交易链'
        
        elif evidence.evidence_type == 'video':
            base_info += '【监控数据预览】\n\n'
            base_info += '摄像头ID: CAM-001\n'
            base_info += '分辨率: 1920x1080\n'
            base_info += '帧率: 25fps\n'
            base_info += '编码: H.264\n\n'
            base_info += '【关键帧分析】\n'
            base_info += '00:00:00 - 正常画面\n'
            base_info += '00:05:32 - 可疑人物进入画面\n'
            base_info += '00:06:15 - 人物接近服务器机柜\n'
            base_info += '00:08:47 - 人物离开画面\n\n'
            base_info += '【分析提示】检查人物特征和行为模式'
        
        elif evidence.evidence_type == 'audio':
            base_info += '【音频分析报告】\n\n'
            base_info += '采样率: 44.1kHz\n'
            base_info += '位深度: 16bit\n'
            base_info += '时长: 30分钟\n\n'
            base_info += '【语音转写摘要】\n'
            base_info += '[00:02:15] 证人：那天晚上我看到有人在服务器机房附近...\n'
            base_info += '[00:05:42] 证人：那个人看起来很熟悉，但我不确定是谁...\n'
            base_info += '[00:12:30] 证人：后来我听到服务器发出异常的嗡嗡声...\n\n'
            base_info += '【分析提示】提取关键词和时间戳'
        
        elif evidence.evidence_type == 'physical':
            base_info += '【物证鉴定报告】\n\n'
            base_info += '物品类型: 存储设备\n'
            base_info += '型号: USB 3.0 Flash Drive\n'
            base_info += '容量: 128GB\n'
            base_info += '序列号: SN-2026-001234\n\n'
            base_info += '【数据恢复结果】\n'
            base_info += '文件数: 156个\n'
            base_info += '包含: 加密文档、源代码、日志文件\n'
            base_info += '最后访问时间: 2026-07-14 23:58:00\n\n'
            base_info += '【分析提示】进行数据取证和来源追踪'
        
        elif evidence.evidence_type == 'testimony':
            base_info += '【证人证言笔录】\n\n'
            base_info += '证人姓名: ' + (self.current_witness or '未知') + '\n'
            base_info += '记录时间: 2026-07-16\n'
            base_info += '记录员: 调查员\n\n'
            base_info += '问：你当时在场吗？\n'
            base_info += '答：是的，我在现场。\n\n'
            base_info += '问：你看到了什么？\n'
            base_info += '答：我看到一个人进入了机房...\n\n'
            base_info += '【分析提示】寻找证言中的矛盾点和关键信息'
        
        return base_info
    
    def on_analyze_evidence(self):
        selected = self.evidence_listbox.curselection()
        if not selected:
            messagebox.showwarning('警告', '请选择要分析的证据')
            return
        
        index = selected[0]
        evidence = self.current_case.evidence_manager.evidence_list[index]
        
        if not evidence.collected:
            messagebox.showwarning('警告', '请先收集该证据')
            return
        
        if evidence.analyzed:
            self._set_info_text(f'证据：{evidence.name}\n分析结果：\n{evidence.analysis_result}')
            return
        
        analysis = self._generate_analysis(evidence)
        
        self.current_case.evidence_manager.analyze_evidence(evidence.evidence_id, analysis)
        self.analyzed_evidence_ids.add(evidence.evidence_id)
        self._update_evidence_list()
        self._save_progress()
        self._set_info_text(analysis)
        messagebox.showinfo('分析完成', '证据分析完成')
    
    def _generate_analysis(self, evidence):
        analysis = f'【分析报告】\n\n证据名称：{evidence.name}\n类型：{evidence.get_type_label()}\n发现地点：{evidence.location}\n\n'
        
        if evidence.evidence_type == 'document':
            analysis += '【深度分析】\n\n'
            analysis += '1. 数据完整性验证：通过哈希校验，数据完整未被篡改\n'
            analysis += '2. 时间线分析：发现异常访问时段为凌晨00:15-00:30\n'
            analysis += '3. IP溯源：访问IP来自境外服务器，已通过VPN跳转\n'
            analysis += '4. 操作模式：与正常用户行为模式存在显著差异\n\n'
            analysis += '【关键发现】\n'
            analysis += '- 在异常访问期间，有一笔大额转账操作\n'
            analysis += '- 操作时间与被告声称的漏洞报告时间存在冲突\n'
        
        elif evidence.evidence_type == 'video':
            analysis += '【视频分析】\n\n'
            analysis += '1. 人脸识别：画面中人物身份已确认\n'
            analysis += '2. 行为分析：人物在机柜前停留约3分钟\n'
            analysis += '3. 时间同步：与服务器日志时间戳一致\n'
            analysis += '4. 环境分析：机房门禁系统显示该时段无合法进入记录\n\n'
            analysis += '【关键发现】\n'
            analysis += '- 人物携带了可疑电子设备\n'
            analysis += '- 离开时手部有明显动作，疑似插入/拔出设备'
        
        elif evidence.evidence_type == 'audio':
            analysis += '【音频分析】\n\n'
            analysis += '1. 声纹识别：已确认说话者身份\n'
            analysis += '2. 情绪分析：证人陈述时存在紧张情绪\n'
            analysis += '3. 内容分析：证言存在前后不一致之处\n'
            analysis += '4. 背景噪音：检测到电子设备运行声音\n\n'
            analysis += '【关键发现】\n'
            analysis += '- 证人提及的时间与其他证据存在矛盾\n'
            analysis += '- 部分陈述存在记忆模糊的情况'
        
        elif evidence.evidence_type == 'physical':
            analysis += '【物证分析】\n\n'
            analysis += '1. 指纹检测：设备表面发现3组指纹\n'
            analysis += '2. 数字取证：已恢复已删除文件\n'
            analysis += '3. 来源追踪：设备购买记录已查明\n'
            analysis += '4. 数据关联：与案件其他证据存在关联\n\n'
            analysis += '【关键发现】\n'
            analysis += '- 设备中包含被删除的敏感数据\n'
            analysis += '- 指纹与嫌疑人部分匹配'
        
        else:
            analysis += '【综合分析】\n\n'
            analysis += '通过技术手段分析，该证据显示了关键信息，可能对案件判决产生重要影响。\n'
        
        analysis += '\n【证据效力】' + ('高' if evidence.is_key else '中') + '\n'
        analysis += '【可信度】待验证'
        
        return analysis
    
    def on_interview_witness(self):
        selected = self.witness_listbox.curselection()
        if not selected:
            messagebox.showwarning('警告', '请选择要询问的证人')
            return
        
        witness_name = self.witness_listbox.get(selected[0]).replace('[已询问]', '').strip()
        self.current_witness = witness_name
        
        self.interviewed_witnesses.add(witness_name)
        self._update_witness_list()
        
        dialogues = self.dialogue_manager.get_dialogues_by_speaker(witness_name)
        if dialogues:
            start_dialogue = None
            if witness_name in self.dialogue_history and self.dialogue_history[witness_name]:
                last_dialogue = self.dialogue_history[witness_name][-1]
                last_id = last_dialogue.get('next_dialogue')
                if last_id:
                    start_dialogue = self.dialogue_manager.get_dialogue_by_id(last_id)
            
            if start_dialogue is None:
                start_dialogue = dialogues[0]
            
            self.dialogue_manager.set_current_dialogue(start_dialogue.dialogue_id)
            self._show_dialogue(start_dialogue)
        else:
            self._show_default_witness_dialogue()
    
    def _show_dialogue(self, dialogue):
        trust_info = f'（信任度: {self.witness_trust.get(dialogue.speaker, 50)}/100）'
        
        content = f'【{dialogue.speaker}】{trust_info}\n\n{dialogue.text}\n\n'
        
        if dialogue.has_choices():
            content += '请选择回应方式：\n\n'
            for i, choice in enumerate(dialogue.choices):
                content += f'{i+1}. {choice["text"]}\n'
        
        self._set_info_text(content)
        
        if dialogue.has_choices():
            self._show_dialogue_choices(dialogue)
    
    def _show_dialogue_choices(self, dialogue):
        choice_window = tk.Toplevel(self)
        choice_window.title(f'询问 {dialogue.speaker}')
        choice_window.geometry('400x300')
        
        ttk.Label(choice_window, text=f'【{dialogue.speaker}】\n\n{dialogue.text}', 
                  wraplength=380, font=('微软雅黑', 11)).pack(pady=10)
        
        for i, choice in enumerate(dialogue.choices):
            btn = ttk.Button(choice_window, text=choice['text'], 
                             command=lambda idx=i, c=choice, d=dialogue, win=choice_window: 
                             self._handle_choice(idx, c, d, win))
            btn.pack(fill=tk.X, padx=20, pady=5)
    
    def _handle_choice(self, choice_index, choice, dialogue, window):
        window.destroy()
        
        if dialogue.speaker not in self.dialogue_history:
            self.dialogue_history[dialogue.speaker] = []
        self.dialogue_history[dialogue.speaker].append({
            'speaker': dialogue.speaker,
            'text': dialogue.text,
            'choice': choice['text']
        })
        
        effect = choice.get('effect', {})
        if 'trust' in effect:
            self.witness_trust[dialogue.speaker] = max(0, min(100, 
                self.witness_trust.get(dialogue.speaker, 50) + effect['trust']))
        
        next_dialogue_id = choice.get('next_dialogue')
        if next_dialogue_id:
            next_dialogue = self.dialogue_manager.get_dialogue_by_id(next_dialogue_id)
            if next_dialogue:
                self._show_dialogue(next_dialogue)
            else:
                self._save_progress()
                self._set_info_text(f'对话结束。当前信任度: {self.witness_trust.get(dialogue.speaker, 50)}/100')
        else:
            self._save_progress()
            self._set_info_text(f'对话结束。当前信任度: {self.witness_trust.get(dialogue.speaker, 50)}/100')
    
    def _show_default_witness_dialogue(self):
        content = f'【{self.current_witness}】\n\n'
        content += '我可以提供一些关于案件的信息。你想了解什么？\n\n'
        content += '可选问题：\n\n'
        content += '1. 案发当天你在哪里？\n'
        content += '2. 你是否认识被告？\n'
        content += '3. 你看到了什么异常情况？\n'
        content += '4. 你对案件有什么看法？\n'
        
        self._set_info_text(content)
        
        choice_window = tk.Toplevel(self)
        choice_window.title(f'询问 {self.current_witness}')
        choice_window.geometry('400x350')
        
        questions = [
            '案发当天你在哪里？',
            '你是否认识被告？',
            '你看到了什么异常情况？',
            '你对案件有什么看法？'
        ]
        
        answers = {
            0: f'{self.current_witness}：案发当天我在公司加班，直到晚上11点才离开。',
            1: f'{self.current_witness}：我和被告只是认识，不算很熟。我们在同一个行业工作。',
            2: f'{self.current_witness}：那天晚上我确实注意到服务器机房的灯亮着，但我没有在意。',
            3: f'{self.current_witness}：我觉得这个案件很复杂，需要更多证据才能下结论。'
        }
        
        for i, q in enumerate(questions):
            btn = ttk.Button(choice_window, text=q,
                             command=lambda idx=i, ans=answers, win=choice_window, w=self.current_witness:
                             self._handle_default_choice(idx, ans, win, w))
            btn.pack(fill=tk.X, padx=20, pady=5)
    
    def _handle_default_choice(self, idx, answers, window, witness):
        window.destroy()
        self._set_info_text(answers[idx])
        
        if idx == 0 or idx == 2:
            self.witness_trust[witness] = min(100, self.witness_trust.get(witness, 50) + 5)
    
    def on_show_trust(self):
        trust_text = '【证人信任度】\n\n'
        for witness, trust in self.witness_trust.items():
            trust_text += f'{witness}: {trust}/100 {"⭐" * (trust // 20)}\n'
        messagebox.showinfo('信任度', trust_text)
    
    def on_search_laws(self):
        keyword = self.search_var.get().strip()
        if not keyword:
            self._load_all_laws()
            return
        
        results = self.law_system.search_laws(keyword)
        self.laws_listbox.delete(0, tk.END)
        for law in results:
            self.laws_listbox.insert(tk.END, f'{law.title} - {law.category}')
    
    def on_view_law_detail(self):
        selected = self.laws_listbox.curselection()
        if not selected:
            messagebox.showwarning('警告', '请选择法律')
            return
        
        law_title = self.laws_listbox.get(selected[0]).split(' - ')[0]
        for law in self.law_system.laws.values():
            if law.title == law_title:
                self._set_info_text(f'【法律条文】\n\n名称：{law.title}\n类别：{law.category}\n严重程度：{law.severity}\n\n内容：\n{law.content}\n\n相关条款：{", ".join(law.related_articles)}')
                return
    
    def on_enter_court(self):
        collected_count = len(self.current_case.evidence_manager.get_collected_evidence())
        total_count = len(self.current_case.evidence_manager.evidence_list)
        
        if collected_count == 0:
            messagebox.showwarning('警告', '请先收集至少一项证据')
            return
        
        from .court_view import CourtView
        self.parent.show_view(CourtView, case_manager=self.case_manager, law_system=self.law_system,
                              save_manager=self.save_manager, character=self.character, 
                              player_role=self.player_role)
    
    def on_back(self):
        from .case_selection import CaseSelection
        self.parent.show_view(CaseSelection)
    
    def _on_mouse_wheel(self, event):
        self.info_text.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def _setup_shortcuts(self):
        from ..core.config_manager import ConfigManager
        config_manager = ConfigManager()
        shortcuts = config_manager.get_shortcuts()
        
        root = self.winfo_toplevel()
        root.bind(shortcuts['collect_evidence'], lambda e: self.on_collect_evidence())
        root.bind(shortcuts['analyze_evidence'], lambda e: self.on_analyze_evidence())
        root.bind(shortcuts['interview_witness'], lambda e: self.on_interview_witness())
        root.bind(shortcuts['search_laws'], lambda e: self.on_search_laws())
        root.bind(shortcuts['back'], lambda e: self.on_back())
        root.bind(shortcuts['enter_court'], lambda e: self.on_enter_court())
        root.bind(shortcuts['escape'], lambda e: self.on_back())