import tkinter as tk
from tkinter import ttk, messagebox

class LawViewer(tk.Toplevel):
    def __init__(self, parent, law_system):
        super().__init__(parent)
        self.parent = parent
        self.law_system = law_system
        self.title('法律条文查询')
        self.geometry('900x650')
        self.minsize(800, 500)
        self._setup_ui()
    
    def _setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        search_frame = ttk.Frame(self, padding=(10, 10, 10, 5))
        search_frame.grid(row=0, column=0, sticky='ew')
        search_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(search_frame, text='搜索法律：').grid(row=0, column=0, sticky='w')
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.grid(row=0, column=1, sticky='ew', padx=(5, 10))
        ttk.Button(search_frame, text='搜索', command=self.on_search).grid(row=0, column=2)
        
        main_frame = ttk.Frame(self)
        main_frame.grid(row=1, column=0, sticky='nsew', padx=10, pady=(0, 10))
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=2)
        main_frame.grid_rowconfigure(0, weight=1)
        
        left_panel = ttk.Frame(main_frame)
        left_panel.grid(row=0, column=0, sticky='nsew', padx=(0, 10))
        left_panel.grid_columnconfigure(0, weight=1)
        left_panel.grid_rowconfigure(0, weight=0)
        left_panel.grid_rowconfigure(1, weight=1)
        
        category_frame = ttk.Frame(left_panel)
        category_frame.grid(row=0, column=0, sticky='ew', pady=(0, 5))
        
        categories = self.law_system.get_all_categories()
        self.category_var = tk.StringVar(value='全部')
        
        ttk.Label(category_frame, text='分类筛选：').pack(side=tk.LEFT, padx=(0, 5))
        ttk.Combobox(category_frame, textvariable=self.category_var, 
                     values=['全部'] + categories, state='readonly', width=15).pack(fill=tk.X)
        self.category_var.trace('w', self.on_category_change)
        
        self.law_listbox = tk.Listbox(left_panel, font=('微软雅黑', 10), selectbackground='#4a90d9', 
                                      selectforeground='white', activestyle='none')
        self.law_listbox.grid(row=1, column=0, sticky='nsew')
        
        scrollbar = ttk.Scrollbar(left_panel, orient=tk.VERTICAL, command=self.law_listbox.yview)
        self.law_listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=1, column=1, sticky='ns')
        
        self.law_listbox.bind('<<ListboxSelect>>', self.on_law_select)
        
        right_panel = ttk.Frame(main_frame)
        right_panel.grid(row=0, column=1, sticky='nsew')
        right_panel.grid_columnconfigure(0, weight=1)
        right_panel.grid_rowconfigure(0, weight=1)
        
        detail_frame = ttk.Frame(right_panel, borderwidth=1, relief=tk.SUNKEN)
        detail_frame.grid(row=0, column=0, sticky='nsew')
        detail_frame.grid_columnconfigure(0, weight=1)
        detail_frame.grid_rowconfigure(0, weight=1)
        
        self.detail_text = tk.Text(detail_frame, wrap=tk.WORD, font=('微软雅黑', 11), 
                                   state=tk.DISABLED, bg='white', padx=15, pady=15)
        self.detail_text.grid(row=0, column=0, sticky='nsew')
        
        text_scrollbar = ttk.Scrollbar(detail_frame, orient=tk.VERTICAL, command=self.detail_text.yview)
        self.detail_text.configure(yscrollcommand=text_scrollbar.set)
        text_scrollbar.grid(row=0, column=1, sticky='ns')
        
        bottom_frame = ttk.Frame(right_panel)
        bottom_frame.grid(row=1, column=0, sticky='ew', pady=(5, 0))
        
        self._load_all_laws()
    
    def _load_all_laws(self):
        self.law_listbox.delete(0, tk.END)
        for law in self.law_system.laws.values():
            self.law_listbox.insert(tk.END, f'{law.title}')
    
    def on_search(self):
        keyword = self.search_var.get().strip()
        if not keyword:
            self._load_all_laws()
            return
        
        results = self.law_system.search_laws(keyword)
        self.law_listbox.delete(0, tk.END)
        for law in results:
            self.law_listbox.insert(tk.END, f'{law.title}')
    
    def on_category_change(self, *args):
        category = self.category_var.get()
        self.law_listbox.delete(0, tk.END)
        
        if category == '全部':
            self._load_all_laws()
        else:
            laws = self.law_system.get_laws_by_category(category)
            for law in laws:
                self.law_listbox.insert(tk.END, f'{law.title}')
    
    def on_law_select(self, event):
        selected = self.law_listbox.curselection()
        if not selected:
            return
        
        law_title = self.law_listbox.get(selected[0])
        for law in self.law_system.laws.values():
            if law.title == law_title:
                self._show_law_detail(law)
                return
    
    def _show_law_detail(self, law):
        self.detail_text.config(state=tk.NORMAL)
        self.detail_text.delete(1.0, tk.END)
        
        self.detail_text.insert(tk.END, f'{law.title}\n\n', 'title')
        
        info_lines = []
        if law.source:
            info_lines.append(f'来源：{law.source}')
        info_lines.append(f'类别：{law.category}')
        info_lines.append(f'严重程度：{law.severity}')
        
        self.detail_text.insert(tk.END, ' | '.join(info_lines) + '\n\n', 'info')
        
        lines = law.content.split('\n')
        for line in lines:
            if line.startswith('## '):
                self.detail_text.insert(tk.END, '\n')
                self.detail_text.insert(tk.END, line[3:] + '\n', 'heading')
            elif line.startswith('### '):
                self.detail_text.insert(tk.END, '\n')
                self.detail_text.insert(tk.END, line[4:] + '\n', 'subheading')
            elif line.startswith('- ') or line.startswith('* '):
                self.detail_text.insert(tk.END, '  ' + line + '\n', 'list')
            elif line.startswith('    ') or line.startswith('\t'):
                self.detail_text.insert(tk.END, line + '\n', 'indent')
            else:
                self.detail_text.insert(tk.END, line + '\n', 'normal')
        
        if law.related_articles:
            self.detail_text.insert(tk.END, f'\n相关条款：{", ".join(law.related_articles)}', 'info')
        
        self.detail_text.tag_configure('title', font=('微软雅黑', 18, 'bold'), foreground='#2c3e50')
        self.detail_text.tag_configure('heading', font=('微软雅黑', 14, 'bold'), foreground='#34495e', spacing1=5)
        self.detail_text.tag_configure('subheading', font=('微软雅黑', 12, 'bold'), foreground='#7f8c8d', spacing1=3)
        self.detail_text.tag_configure('info', font=('微软雅黑', 10), foreground='#95a5a6')
        self.detail_text.tag_configure('list', font=('微软雅黑', 11), foreground='#2c3e50')
        self.detail_text.tag_configure('indent', font=('微软雅黑', 11), foreground='#5d6d7e', lmargin1=20)
        self.detail_text.tag_configure('normal', font=('微软雅黑', 11), foreground='#2c3e50')
        
        self.detail_text.config(state=tk.DISABLED)