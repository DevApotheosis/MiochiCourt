import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
from datetime import datetime


class VerdictView(tk.Toplevel):
    def __init__(self, parent, case, verdict, reason, scores, judge_mood, law_system=None, player_role='defense'):
        super().__init__(parent)
        self.parent = parent
        self.case = case
        self.verdict = verdict
        self.reason = reason
        self.scores = scores
        self.judge_mood = judge_mood
        self.law_system = law_system
        self.player_role = player_role
        self.title('澪地审判庭 - 判决书')
        self.geometry('900x1000')
        self.configure(bg='#f5f5f5')
        self._setup_ui()
    
    def _setup_ui(self):
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL)
        canvas = tk.Canvas(main_frame, yscrollcommand=scrollbar.set, bg='#f5f5f5', highlightthickness=0)
        scrollbar.config(command=canvas.yview)
        
        content_frame = ttk.Frame(canvas)
        
        canvas.create_window((0, 0), window=content_frame, anchor=tk.NW)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        content_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.bind('<MouseWheel>', lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        
        self._generate_verdict_document(content_frame)
        
        button_frame = ttk.Frame(self, padding=10)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text='打印判决书', command=self.on_print).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text='保存为图片', command=self.on_save_image).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text='关闭', command=self.destroy).pack(side=tk.RIGHT, padx=10)
    
    def _generate_verdict_document(self, parent):
        doc_frame = ttk.Frame(parent, padding=40, style='Verdict.TFrame')
        doc_frame.pack(fill=tk.X, pady=20)
        
        title_label = ttk.Label(doc_frame, text='澪地审判庭', font=('宋体', 24, 'bold'), 
                                anchor=tk.CENTER)
        title_label.pack(fill=tk.X, pady=10)
        
        subtitle_label = ttk.Label(doc_frame, text='刑事判决书', font=('宋体', 20, 'bold'),
                                   anchor=tk.CENTER)
        subtitle_label.pack(fill=tk.X, pady=5)
        
        doc_number_label = ttk.Label(doc_frame, text=f'(2026)澪刑初字第{self.case.case_id[-3:]}号',
                                     font=('宋体', 14), anchor=tk.CENTER)
        doc_number_label.pack(fill=tk.X, pady=15)
        
        parties_frame = ttk.Frame(doc_frame)
        parties_frame.pack(fill=tk.X, pady=10)
        
        left_party = ttk.Label(parties_frame, text=f'公诉机关：{self.case.plaintiff}',
                               font=('宋体', 14))
        left_party.pack(side=tk.LEFT)
        
        right_party = ttk.Label(parties_frame, text=f'被告人：{self.case.defendant}',
                                font=('宋体', 14))
        right_party.pack(side=tk.RIGHT)
        
        divider = ttk.Separator(doc_frame, orient=tk.HORIZONTAL)
        divider.pack(fill=tk.X, pady=10)
        
        case_title = ttk.Label(doc_frame, text=f'案    由：{self.case.title}',
                               font=('宋体', 14))
        case_title.pack(fill=tk.X, pady=5)
        
        case_location = ttk.Label(doc_frame, text=f'审理法院：{self.case.location}人民法院',
                                   font=('宋体', 14))
        case_location.pack(fill=tk.X, pady=5)
        
        case_time = ttk.Label(doc_frame, text=f'审理时间：{datetime.now().strftime("%Y年%m月%d日")}',
                               font=('宋体', 14))
        case_time.pack(fill=tk.X, pady=5)
        
        divider2 = ttk.Separator(doc_frame, orient=tk.HORIZONTAL)
        divider2.pack(fill=tk.X, pady=10)
        
        fact_title = ttk.Label(doc_frame, text='一、案件事实', font=('宋体', 16, 'bold'))
        fact_title.pack(fill=tk.X, pady=10)
        
        fact_text = tk.Text(doc_frame, wrap=tk.WORD, font=('宋体', 14), height=6,
                            state=tk.DISABLED, bg='#ffffff', 
                            relief=tk.FLAT, borderwidth=0, padx=5, pady=5)
        fact_text.pack(fill=tk.X, pady=5)
        fact_text.config(state=tk.NORMAL)
        fact_text.insert(tk.END, self.case.description)
        fact_text.config(state=tk.DISABLED)
        
        evidence_title = ttk.Label(doc_frame, text='二、证据采信', font=('宋体', 16, 'bold'))
        evidence_title.pack(fill=tk.X, pady=10)
        
        evidence_frame = ttk.Frame(doc_frame)
        evidence_frame.pack(fill=tk.X, pady=5)
        
        collected_evidence = self.case.evidence_manager.get_collected_evidence()
        seen_ids = set()
        unique_evidence = []
        for ev in collected_evidence:
            if ev.evidence_id not in seen_ids:
                seen_ids.add(ev.evidence_id)
                unique_evidence.append(ev)
        evidence_text = '\n'.join([f'- {ev.name}（{ev.get_type_label()}）' for ev in unique_evidence])
        
        evidence_label = ttk.Label(evidence_frame, text=evidence_text if collected_evidence else '无',
                                   font=('宋体', 14), justify=tk.LEFT, wraplength=600)
        evidence_label.pack(fill=tk.X)
        
        law_title = ttk.Label(doc_frame, text='三、法律适用', font=('宋体', 16, 'bold'))
        law_title.pack(fill=tk.X, pady=10)
        
        law_text = tk.Text(doc_frame, wrap=tk.WORD, font=('宋体', 14), height=4,
                           state=tk.DISABLED, bg='#ffffff', 
                           relief=tk.FLAT, borderwidth=0, padx=5, pady=5)
        law_text.pack(fill=tk.X, pady=5)
        law_text.config(state=tk.NORMAL)
        
        if self.case.key_laws:
            law_titles = []
            for law_id in self.case.key_laws:
                if self.law_system:
                    law = self.law_system.get_law_by_id(law_id)
                    if law and law.title:
                        law_titles.append(law.title)
                    else:
                        law_titles.append(law_id)
                else:
                    law_titles.append(law_id)
            law_text.insert(tk.END, f'依据《中华人民共和国刑法》相关条款及{"、".join(law_titles)}')
        else:
            law_text.insert(tk.END, '依据《中华人民共和国刑法》相关条款')
        law_text.config(state=tk.DISABLED)
        
        divider3 = ttk.Separator(doc_frame, orient=tk.HORIZONTAL)
        divider3.pack(fill=tk.X, pady=10)
        
        verdict_title = ttk.Label(doc_frame, text='四、判决结果', font=('宋体', 16, 'bold'))
        verdict_title.pack(fill=tk.X, pady=10)
        
        verdict_frame = ttk.Frame(doc_frame)
        verdict_frame.pack(fill=tk.X, pady=10)
        
        verdict_result = self._get_verdict_label()
        verdict_color = '#c0392b' if '失败' in verdict_result or '有罪' in verdict_result else '#27ae60'
        
        result_label = ttk.Label(verdict_frame, text=f'判    决：{verdict_result}',
                                 font=('宋体', 24, 'bold'), foreground=verdict_color)
        result_label.pack(fill=tk.X, pady=10)
        
        reason_text = tk.Text(doc_frame, wrap=tk.WORD, font=('宋体', 14), height=8,
                              state=tk.DISABLED, bg='#ffffff', 
                              relief=tk.FLAT, borderwidth=0, padx=5, pady=5)
        reason_text.pack(fill=tk.X, pady=5)
        reason_text.config(state=tk.NORMAL)
        reason_text.insert(tk.END, self.reason)
        reason_text.config(state=tk.DISABLED)
        
        divider4 = ttk.Separator(doc_frame, orient=tk.HORIZONTAL)
        divider4.pack(fill=tk.X, pady=10)
        
        scores_title = ttk.Label(doc_frame, text='五、审判评分', font=('宋体', 16, 'bold'))
        scores_title.pack(fill=tk.X, pady=10)
        
        scores_frame = ttk.Frame(doc_frame)
        scores_frame.pack(fill=tk.X, pady=5)
        
        score_items = [
            ('证据分', self.scores.get('evidence_points', 0)),
            ('法律分', self.scores.get('law_points', 0)),
            ('证言分', self.scores.get('witness_points', 0)),
            ('总分', sum(self.scores.values()))
        ]
        
        for i, (label, value) in enumerate(score_items):
            score_label = ttk.Label(scores_frame, text=f'{label}：{value}',
                                    font=('宋体', 14))
            score_label.pack(side=tk.LEFT, padx=20)
        
        judge_mood_label = ttk.Label(doc_frame, text=f'法官态度：{self._get_mood_text(self.judge_mood)}',
                                      font=('宋体', 14))
        judge_mood_label.pack(fill=tk.X, pady=5)
        
        divider5 = ttk.Separator(doc_frame, orient=tk.HORIZONTAL)
        divider5.pack(fill=tk.X, pady=20)
        
        signature_frame = ttk.Frame(doc_frame)
        signature_frame.pack(fill=tk.X, pady=10)
        
        left_sign = ttk.Label(signature_frame, text='审判长：澪地法官',
                              font=('宋体', 14))
        left_sign.pack(side=tk.LEFT)
        
        right_sign = ttk.Label(signature_frame, text=f'{datetime.now().strftime("%Y年%m月%d日")}',
                               font=('宋体', 14))
        right_sign.pack(side=tk.RIGHT)
        
        seal_frame = ttk.Frame(doc_frame)
        seal_frame.pack(fill=tk.X, pady=10)
        
        seal_label = ttk.Label(seal_frame, text='澪地审判庭',
                               font=('宋体', 16, 'bold'), foreground='#c0392b')
        seal_label.pack(side=tk.RIGHT)
    
    def _get_verdict_label(self):
        if self.player_role == 'defense':
            return '有罪' if self.verdict == 'major' else '无罪'
        else:
            return '被告有罪' if self.verdict == 'major' else '被告无罪'
    
    def _get_mood_text(self, mood):
        if mood >= 80:
            return '✅ 非常有利'
        elif mood >= 60:
            return '😊 有利'
        elif mood >= 40:
            return '😐 中立'
        elif mood >= 20:
            return '😟 不利'
        else:
            return '❌ 非常不利'
    
    def on_print(self):
        messagebox.showinfo('提示', '请使用系统打印功能（Ctrl+P）进行打印')
    
    def on_save_image(self):
        from tkinter import filedialog
        
        filepath = filedialog.asksaveasfilename(
            defaultextension='.png',
            filetypes=[('PNG图片', '*.png'), ('所有文件', '*.*')],
            title='保存判决书'
        )
        
        if filepath:
            try:
                import pyautogui
                
                x = self.winfo_rootx()
                y = self.winfo_rooty()
                width = self.winfo_width()
                height = self.winfo_height()
                
                screenshot = pyautogui.screenshot(region=(x, y, width, height))
                screenshot.save(filepath)
                
                messagebox.showinfo('成功', f'判决书已保存到：{filepath}')
            except ImportError:
                messagebox.showwarning('提示', '请安装 pyautogui 库以保存图片')
            except Exception as e:
                messagebox.showerror('错误', f'保存失败：{str(e)}')
