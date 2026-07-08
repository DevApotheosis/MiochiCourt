import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import random
from PIL import Image, ImageTk
import os
from ..core.config import GUILT_LEVELS, IMAGES_DIR
from ..core.achievements import AchievementManager
from ..core.save_system import SaveManager
from ..core.character import Character
from ..core.dossier_system import DossierManager

class CourtView(tk.Frame):
    def __init__(self, parent, case_manager, law_system, save_manager=None, character=None, player_role='defense'):
        super().__init__(parent)
        self.parent = parent
        self.case_manager = case_manager
        self.law_system = law_system
        self.save_manager = save_manager or SaveManager()
        self.character = character or Character()
        self.player_role = player_role
        self.current_case = case_manager.get_current_case()
        self.court_log = []
        self.judge_mood = 50
        self.evidence_points = 0
        self.law_points = 0
        self.witness_points = 0
        self.total_actions = 0
        self.used_evidence = []
        self.used_laws = []
        self.witness_trust = {}
        self.achievement_manager = AchievementManager()
        self.achievement_manager.load_from_file(self.character.name)
        
        self.opponent_lawyer_statements = {
            'opening': [
                '尊敬的审判长，各位陪审员，我代表原告方提出指控。本案事实清楚，证据确凿，被告的行为已构成违法。',
                '审判长，我是被告的辩护律师。我的当事人是无辜的，控方的指控缺乏事实依据，请求法庭依法作出公正裁决。',
                '根据刑事诉讼法的规定，控方必须提供充分的证据证明被告有罪。我们将向法庭展示完整的证据链。',
                '我的当事人坚决否认所有指控。控方所谓的"证据"存在严重缺陷，无法证明任何犯罪行为。',
                '尊敬的审判长，本案涉及重大的法律原则问题。我们恳请法庭审慎审理，维护司法公正。',
                '作为原告方律师，我将向法庭陈述案件事实，并提供确凿的证据支持我们的主张。'
            ],
            'evidence_response': [
                '对方律师提出的这份证据，其真实性和关联性都存在严重问题。我们强烈质疑该证据的合法性。',
                '这份证据是在非法的情况下获取的，根据证据规则，应当予以排除。',
                '对方提供的证据无法证明其主张，证据链断裂，不能作为定案的依据。',
                '我们对这份证据的来源和真实性表示严重怀疑。控方（辩方）有责任证明证据的合法性。',
                '这份证据与本案无关，不能证明被告（原告）的任何行为。请法庭不予采纳。',
                '对方律师似乎忽略了证据中的关键细节。这份证据恰恰证明了我方的观点。'
            ],
            'law_response': [
                '对方律师引用的法律条文与本案事实不符，属于法律适用错误。',
                '根据最新的司法解释，本案应当适用另一项法律条款。对方的法律依据已经过时。',
                '对方律师对法律条文的理解存在偏差，该条款并不适用于本案的具体情况。',
                '我们提请法庭注意，对方引用的法律条文存在例外情形，而本案恰恰属于该例外。',
                '法律的基本原则是"以事实为依据，以法律为准绳"。对方的法律分析脱离了案件事实。',
                '对方律师选择性地引用法律条文，忽略了与之相关的其他条款，这种做法是片面的。'
            ],
            'witness_response': [
                '这位证人与本案存在直接的利害关系，其证言的可信度令人怀疑。',
                '证人的陈述前后矛盾，无法自圆其说。这样的证言不应被法庭采信。',
                '我们有充分的理由相信，这位证人受到了不当影响，其证言缺乏客观性。',
                '证人的记忆力存在问题，对关键事实的陈述模糊不清。这样的证言证明力有限。',
                '对方律师诱导证人作出有利于己方的陈述，这种询问方式是不恰当的。',
                '我们提请法庭注意，证人的证言与物证之间存在无法解释的矛盾。'
            ],
            'counter_attack': [
                '对方的辩护（指控）完全站不住脚。我们有新的证据可以证明被告（原告）的行为。',
                '让我们看看真正的事实。对方律师试图混淆视听，但证据不会说谎。',
                '对方的论点存在根本性的错误。我们将向法庭展示无可辩驳的证据。',
                '事实真相即将浮出水面。对方律师的狡辩无法掩盖事实。',
                '我们相信，法庭会根据证据和法律作出公正的判断，而不是被对方的言辞所迷惑。',
                '对方律师的陈述漏洞百出，我们可以逐一指出其中的错误。'
            ],
            'final': [
                '综上所述，被告（原告）的行为已经构成犯罪（违法行为），证据确凿，事实清楚。请法庭依法作出有罪（支持原告诉求）的判决。',
                '我们坚信正义终将得到伸张。',
                '请法庭根据事实和法律作出公正的判决。',
                '本案事实清楚，证据确凿，应依法严惩（支持诉求）。'
            ]
        }
        
        self.judge_statements = {
            'start': [
                '肃静！现在开庭审理本案。',
                '本庭现在开始审理，请双方陈述各自立场。',
                '请控辩双方注意法庭秩序，开始本案审理。',
                '现在开庭，请原告方陈述诉讼请求。'
            ],
            'evidence_good': [
                '这个证据很有说服力，请继续。',
                '嗯，这个证据指向性很强。',
                '很好，这个证据对案件很重要。',
                '有价值的证据，本庭予以记录。'
            ],
            'evidence_bad': [
                '这个证据关联性不足，请提供更有力的证据。',
                '本庭认为这个证据的证明力有限。',
                '请说明此证据与本案的直接关系。',
                '这个证据需要进一步验证。'
            ],
            'law_good': [
                '引用法律得当，请继续陈述。',
                '法律适用正确，本庭予以认可。',
                '很好，法律依据充分。',
                '法律条文引用恰当，继续。'
            ],
            'law_bad': [
                '请确认法律条文的适用性。',
                '这个法律条文与本案关联性不强。',
                '请重新考虑法律适用。',
                '法律引用需要更精确。'
            ],
            'witness_good': [
                '证人证词清晰，请继续盘问。',
                '证人陈述有说服力。',
                '很好，证人证言很有价值。',
                '证人回答条理清晰。'
            ],
            'witness_bad': [
                '证人证词存在矛盾，请进一步核实。',
                '本庭对证人证词存疑。',
                '请继续追问以澄清疑点。',
                '证人陈述不够明确。'
            ],
            'final_success': [
                '经过审理，本庭认为证据充分，被告无罪释放！',
                '根据现有证据和法律规定，本庭宣判被告无罪。',
                '辩方提供的证据和法律依据充分，被告无罪。',
                '综合全案证据，本庭认定被告不构成犯罪。'
            ],
            'final_failure': [
                '经过审理，本庭认为证据不足，被告有罪！',
                '控方指控成立，本庭宣判被告有罪。',
                '现有证据无法证明被告清白，判决有罪。',
                '综合全案证据，本庭认定被告构成犯罪。'
            ],
            'neutral': [
                '请继续陈述。',
                '本庭正在听取，请继续。',
                '请提供更多证据支持你的主张。',
                '双方可以继续辩论。'
            ]
        }
        
        self._setup_ui()
        self._setup_shortcuts()
        self._judge_speak('start')
    
    def _setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        main_frame = ttk.Frame(self, padding=10)
        main_frame.grid(row=0, column=0, sticky='nsew')
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        title_frame.grid_columnconfigure(0, weight=1)
        title_frame.grid_columnconfigure(1, weight=1)
        title_frame.grid_columnconfigure(2, weight=1)
        
        ttk.Button(title_frame, text='返回调查', command=self.on_back).grid(row=0, column=0, sticky='w')
        
        role_label = '被告方律师' if self.player_role == 'defense' else '原告方律师'
        role_color = '#27ae60' if self.player_role == 'defense' else '#c0392b'
        self.role_label = ttk.Label(title_frame, text=f'{self.character.name} - {role_label}', 
                                   font=('微软雅黑', 12, 'bold'), foreground=role_color)
        self.role_label.grid(row=0, column=1)
        
        self.mood_label = ttk.Label(title_frame, text=f'法官态度: {self._get_mood_text()}', style='Subtitle.TLabel')
        self.mood_label.grid(row=0, column=2, sticky='e')
        
        court_area = ttk.Frame(main_frame, style='Court.TFrame')
        court_area.grid(row=1, column=0, sticky='nsew')
        court_area.grid_columnconfigure(0, weight=3)
        court_area.grid_columnconfigure(1, weight=1)
        court_area.grid_rowconfigure(0, weight=1)
        
        log_frame = ttk.Frame(court_area)
        log_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 10))
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_rowconfigure(0, weight=1)
        log_frame.grid_rowconfigure(1, weight=0)
        
        self.log_text = tk.Text(log_frame, wrap=tk.WORD, font=('微软雅黑', 10), 
                                state=tk.DISABLED, bg='#f8fafc')
        self.log_text.grid(row=0, column=0, sticky='nsew')
        
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        log_scrollbar.grid(row=0, column=1, sticky='ns')
        
        score_frame = ttk.Frame(log_frame)
        score_frame.grid(row=1, column=0, sticky='ew', pady=(5, 0))
        
        ttk.Label(score_frame, text=f'证据分: {self.evidence_points}').pack(side=tk.LEFT, padx=10)
        ttk.Label(score_frame, text=f'法律分: {self.law_points}').pack(side=tk.LEFT, padx=10)
        ttk.Label(score_frame, text=f'证言分: {self.witness_points}').pack(side=tk.LEFT, padx=10)
        
        right_panel = ttk.Frame(court_area)
        right_panel.grid(row=0, column=1, sticky='nsew')
        right_panel.grid_columnconfigure(0, weight=1)
        
        ttk.Label(right_panel, text='可用证据', style='Subtitle.TLabel').pack(pady=(0, 5))
        
        self.evidence_listbox = tk.Listbox(right_panel, font=('微软雅黑', 9), height=8)
        self.evidence_listbox.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        ttk.Label(right_panel, text='诉讼操作', style='Subtitle.TLabel').pack(pady=(0, 5))
        
        btn_frame = ttk.Frame(right_panel)
        btn_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Button(btn_frame, text='提出证据', command=self.on_present_evidence).pack(fill=tk.X, pady=2)
        ttk.Button(btn_frame, text='引用法律', command=self.on_cite_law).pack(fill=tk.X, pady=2)
        ttk.Button(btn_frame, text='盘问证人', command=self.on_examine_witness).pack(fill=tk.X, pady=2)
        ttk.Button(btn_frame, text='最终陈述', command=self.on_final_statement).pack(fill=tk.X, pady=2)
        
        self._load_evidence()
    
    def _get_mood_text(self):
        if self.judge_mood >= 80:
            return '✅ 非常有利'
        elif self.judge_mood >= 60:
            return '😊 有利'
        elif self.judge_mood >= 40:
            return '😐 中立'
        elif self.judge_mood >= 20:
            return '😟 不利'
        else:
            return '❌ 非常不利'
    
    def _update_mood(self):
        self.mood_label.config(text=f'法官态度: {self._get_mood_text()}')
    
    def _load_evidence(self):
        self.evidence_listbox.delete(0, tk.END)
        if self.current_case:
            for evidence in self.current_case.evidence_manager.get_collected_evidence():
                self.evidence_listbox.insert(tk.END, evidence.name)
    
    def _add_log(self, text, speaker=''):
        self.court_log.append(text)
        self.log_text.config(state=tk.NORMAL)
        if speaker:
            self.log_text.insert(tk.END, f'【{speaker}】', 'speaker')
        self.log_text.insert(tk.END, f'{text}\n', 'normal')
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        self.log_text.tag_configure('speaker', font=('微软雅黑', 10, 'bold'), foreground='#2c3e50')
        self.log_text.tag_configure('normal', font=('微软雅黑', 10), foreground='#4a5568')
    
    def _judge_speak(self, category):
        statements = self.judge_statements.get(category, self.judge_statements['neutral'])
        statement = random.choice(statements)
        self._add_log(statement, '法官')
    
    def _opponent_speak(self, category):
        statements = self.opponent_lawyer_statements.get(category, self.opponent_lawyer_statements['counter_attack'])
        statement = random.choice(statements)
        
        opponent_role = '原告方律师' if self.player_role == 'defense' else '被告方律师'
        self._add_log(statement, opponent_role)
    
    def _call_ai(self, prompt):
        try:
            response = requests.post(
                'https://api.example.com/chat',
                json={'prompt': prompt},
                timeout=10
            )
            if response.status_code == 200:
                return response.json().get('response', '')
        except Exception:
            pass
        return None
    
    def on_present_evidence(self):
        selected = self.evidence_listbox.curselection()
        if not selected:
            messagebox.showwarning('警告', '请选择要提出的证据')
            return
        
        index = selected[0]
        evidence_list = self.current_case.evidence_manager.get_collected_evidence()
        evidence = evidence_list[index]
        
        if evidence.evidence_id in self.used_evidence:
            messagebox.showwarning('警告', '该证据已提出过')
            return
        
        self.used_evidence.append(evidence.evidence_id)
        self.total_actions += 1
        
        ai_response = self._call_ai(f'作为法官，对证据"{evidence.name}"进行评价，案件是"{self.current_case.title}"')
        
        if ai_response:
            self._add_log(f'【提出证据】{evidence.name}', '辩方')
            self._add_log(ai_response, '法官')
            self._opponent_speak('evidence_response')
            if '有说服力' in ai_response or '重要' in ai_response or '认可' in ai_response:
                points = 15 if evidence.is_key else 10
                self.evidence_points += points
                self.judge_mood = min(100, self.judge_mood + 10)
            else:
                self.judge_mood = max(0, self.judge_mood - 5)
        else:
            self._add_log(f'【提出证据】{evidence.name} - {evidence.description}', '辩方')
            
            if evidence.is_key:
                self._judge_speak('evidence_good')
                self.evidence_points += 15
                self.judge_mood = min(100, self.judge_mood + 10)
            else:
                self._judge_speak('evidence_bad')
                self.evidence_points += 5
                self.judge_mood = max(0, self.judge_mood - 5)
            
            self._opponent_speak('evidence_response')
            self._update_mood()
        
        if evidence.is_key:
            self.achievement_manager.unlock_achievement('key_evidence')
            self.achievement_manager.save_to_file()
    
    def on_cite_law(self):
        laws = list(self.law_system.laws.values())
        if not laws:
            messagebox.showwarning('警告', '暂无可用法律条文')
            return
        
        cite_window = tk.Toplevel(self)
        cite_window.title('选择法律')
        cite_window.geometry('500x400')
        cite_window.grid_columnconfigure(0, weight=1)
        cite_window.grid_rowconfigure(0, weight=1)
        
        listbox = tk.Listbox(cite_window, font=('微软雅黑', 10))
        for law in laws:
            listbox.insert(tk.END, f'{law.title} - {law.category}')
        listbox.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(cite_window, orient=tk.VERTICAL, command=listbox.yview)
        listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky='ns')
        
        def confirm():
            selected = listbox.curselection()
            if selected:
                law = laws[selected[0]]
                
                if law.law_id in self.used_laws:
                    messagebox.showwarning('警告', '该法律已引用过')
                    return
                
                self.used_laws.append(law.law_id)
                self.total_actions += 1
                
                ai_response = self._call_ai(f'作为法官，评价引用法律"{law.title}"的适用性，案件是"{self.current_case.title}"')
                
                if ai_response:
                    self._add_log(f'【引用法律】{law.title}', '辩方')
                    self._add_log(ai_response, '法官')
                    self._opponent_speak('law_response')
                    if '适用' in ai_response or '正确' in ai_response or '充分' in ai_response:
                        self.law_points += 15
                        self.judge_mood = min(100, self.judge_mood + 10)
                    else:
                        self.judge_mood = max(0, self.judge_mood - 5)
                else:
                    self._add_log(f'【引用法律】{law.title} - {law.category}', '辩方')
                    self._judge_speak('law_good')
                    self._opponent_speak('law_response')
                    self.law_points += 15
                    self.judge_mood = min(100, self.judge_mood + 5)
                
                self._update_mood()
            
            cite_window.destroy()
        
        ttk.Button(cite_window, text='确认', command=confirm).grid(row=1, column=0, pady=10)
    
    def on_examine_witness(self):
        if not self.current_case.witnesses:
            messagebox.showwarning('警告', '没有可用的证人')
            return
        
        witness_window = tk.Toplevel(self)
        witness_window.title('盘问证人')
        witness_window.geometry('700x500')
        witness_window.grid_columnconfigure(0, weight=1)
        witness_window.grid_rowconfigure(0, weight=1)
        
        main_paned = ttk.PanedWindow(witness_window, orient=tk.HORIZONTAL)
        main_paned.grid(row=0, column=0, sticky='nsew')
        
        left_frame = ttk.Frame(main_paned, width=200)
        right_frame = ttk.Frame(main_paned, width=500)
        
        main_paned.add(left_frame, weight=1)
        main_paned.add(right_frame, weight=3)
        
        left_frame.grid_columnconfigure(0, weight=1)
        
        self.witness_image_label = ttk.Label(left_frame)
        self.witness_image_label.grid(row=0, column=0, pady=10)
        
        witness_list = ttk.Combobox(left_frame, values=self.current_case.witnesses, 
                                    state='readonly', width=15)
        witness_list.grid(row=1, column=0, pady=10)
        
        def select_witness(event):
            witness = witness_list.get()
            self._show_witness_image(witness)
        
        witness_list.bind('<<ComboboxSelected>>', select_witness)
        
        if self.current_case.witnesses:
            witness_list.current(0)
            self._show_witness_image(self.current_case.witnesses[0])
        
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(0, weight=1)
        right_frame.grid_rowconfigure(1, weight=0)
        
        self.witness_text = tk.Text(right_frame, wrap=tk.WORD, font=('微软雅黑', 11), 
                                    state=tk.DISABLED, bg='white')
        self.witness_text.grid(row=0, column=0, sticky='nsew')
        
        question_frame = ttk.Frame(right_frame)
        question_frame.grid(row=1, column=0, sticky='ew', pady=10)
        
        questions = [
            '请描述案发当天的情况',
            '你是否认识被告？',
            '你当时在场吗？',
            '你能提供更多细节吗？'
        ]
        
        for q in questions:
            ttk.Button(question_frame, text=q, command=lambda text=q: self._ask_witness(text, witness_list.get())).pack(fill=tk.X, pady=2)
    
    def _show_witness_image(self, witness_name):
        image_path = os.path.join(IMAGES_DIR, f'witness_{witness_name}.png')
        
        if not os.path.exists(image_path):
            image_path = os.path.join(IMAGES_DIR, 'default_witness.png')
        
        if os.path.exists(image_path):
            try:
                image = Image.open(image_path)
                image = image.resize((150, 150), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                self.witness_image_label.config(image=photo)
                self.witness_image_label.image = photo
                return
            except Exception:
                pass
        
        self.witness_image_label.config(image='')
        self.witness_image_label.image = None
    
    def _ask_witness(self, question, witness):
        self.total_actions += 1
        
        ai_response = self._call_ai(f'作为证人"{witness}"，回答问题："{question}"，案件是"{self.current_case.title}"')
        
        if ai_response:
            response = ai_response
        else:
            responses = {
                '请描述案发当天的情况': f'{witness}：那天晚上我看到有人在服务器机房附近，但我不确定是谁。',
                '你是否认识被告？': f'{witness}：我和被告只是工作上认识，不算很熟。',
                '你当时在场吗？': f'{witness}：是的，我当时在公司加班。',
                '你能提供更多细节吗？': f'{witness}：那个人穿着黑色外套，戴着帽子，看不清楚长相。'
            }
            response = responses.get(question, f'{witness}：我不太清楚。')
        
        self.witness_text.config(state=tk.NORMAL)
        self.witness_text.delete(1.0, tk.END)
        self.witness_text.insert(tk.END, f'【{witness}】\n\n问：{question}\n\n答：{response}', 'normal')
        self.witness_text.config(state=tk.DISABLED)
        
        self.witness_points += 10
        self._judge_speak('witness_good')
    
    def on_final_statement(self):
        total_score = self.evidence_points + self.law_points + self.witness_points
        key_collected = len(self.current_case.evidence_manager.get_key_evidence())
        total_key = len(self.current_case.required_evidence)
        
        success_threshold = 40
        if key_collected >= total_key // 2:
            success_threshold = 30
        
        if total_score >= success_threshold and self.judge_mood >= 40:
            verdict = 'innocent' if self.player_role == 'defense' else 'major'
            reason = self._generate_success_reason()
            outcome_type = 'defense_success' if self.player_role == 'defense' else 'prosecution_success'
        else:
            verdict = 'major' if self.player_role == 'defense' else 'innocent'
            reason = self._generate_failure_reason()
            outcome_type = 'defense_failure' if self.player_role == 'defense' else 'prosecution_failure'
        
        self.current_case.verdict_guilt = verdict
        self.current_case.verdict_reason = reason
        self.current_case.set_status('completed')
        
        exp_reward = 50 if verdict == 'innocent' else 25
        exp_reward += self.current_case.difficulty * 10
        self.character.add_experience(exp_reward)
        self.character.update_stat('cases_completed', 1)
        self.character.update_stat('evidence_analyzed', len(self.current_case.evidence_manager.get_analyzed_evidence()))
        
        existing_save = self.save_manager.get_save_by_id(SaveManager.AUTO_SAVE_ID)
        existing_progress = existing_save.case_progress if existing_save else {}
        
        existing_progress[self.current_case.case_id] = {
            'status': 'completed',
            'verdict': verdict,
            'reason': reason,
            'evidence_collected': [e.evidence_id for e in self.current_case.evidence_manager.get_collected_evidence()],
            'evidence_analyzed': [e.evidence_id for e in self.current_case.evidence_manager.get_analyzed_evidence()]
        }
        
        self.save_manager.auto_save(
            player_name=self.character.name,
            current_case_id=self.current_case.case_id,
            case_status='completed',
            evidence_collected=[e.evidence_id for e in self.current_case.evidence_manager.get_collected_evidence()],
            evidence_analyzed=[e.evidence_id for e in self.current_case.evidence_manager.get_analyzed_evidence()],
            witness_trust={},
            dialogue_history=self.court_log,
            game_time=0,
            player_data=self.character.to_dict(),
            case_progress=existing_progress
        )
        
        if verdict == 'innocent':
            self._judge_speak('final_success')
        else:
            self._judge_speak('final_failure')
        
        self._add_log(f'判决结果：{GUILT_LEVELS[verdict]}')
        self._add_log(f'判决理由：{reason}')
        
        self.achievement_manager.unlock_achievement('first_verdict')
        
        if verdict == 'innocent':
            self.achievement_manager.unlock_achievement('all_cases')
        
        self.achievement_manager.save_to_file(self.character.name)
        
        evidence_chain = [{'evidence_id': e.evidence_id, 'name': e.name, 
                           'analyzed': e.analyzed} for e in self.current_case.evidence_manager.get_collected_evidence()]
        
        trial_scores = {
            'evidence_points': self.evidence_points,
            'law_points': self.law_points,
            'witness_points': self.witness_points,
            'total': self.evidence_points + self.law_points + self.witness_points
        }
        
        dossier_manager = DossierManager()
        dossier = dossier_manager.create_dossier(
            player_name=self.character.name,
            case=self.current_case,
            verdict=verdict,
            verdict_reason=reason,
            evidence_chain=evidence_chain,
            witness_statements=self.witness_trust,
            trial_scores=trial_scores,
            judge_mood=self.judge_mood
        )
        dossier_manager.save_dossier(dossier)
        
        from .verdict_view import VerdictView
        verdict_view = VerdictView(self, self.current_case, verdict, reason, trial_scores, self.judge_mood, 
                                   law_system=self.law_system, player_role=self.player_role)
        verdict_view.wait_window()
        
        from .case_selection import CaseSelection
        self.parent.show_view(CaseSelection)
    
    def _generate_success_reason(self):
        reasons = [
            '证据链完整，能够证明被告无罪。',
            '辩方提供的证据和法律依据充分，足以推翻指控。',
            '证人证言与物证相互印证，形成完整的证据体系。',
            '控方证据存在重大瑕疵，无法排除合理怀疑。',
            '被告的行为符合法律规定的免责情形。'
        ]
        return random.choice(reasons)
    
    def _generate_failure_reason(self):
        reasons = [
            '现有证据无法证明被告无罪，存在重大嫌疑。',
            '辩方未能提供充分证据反驳控方指控。',
            '证人证言存在矛盾，可信度不足。',
            '法律适用不当，未能有效辩护。',
            '综合全案证据，无法排除被告作案嫌疑。'
        ]
        return random.choice(reasons)
    
    def _setup_shortcuts(self):
        from ..core.config_manager import ConfigManager
        config_manager = ConfigManager()
        shortcuts = config_manager.get_shortcuts()
        
        self.bind(shortcuts['back'], lambda e: self.on_back())
        self.bind(shortcuts['escape'], lambda e: self.on_back())
    
    def on_back(self):
        from .investigation_view import InvestigationView
        self.parent.show_view(InvestigationView, case_manager=self.case_manager, 
                              law_system=self.law_system)