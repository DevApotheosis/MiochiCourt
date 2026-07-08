import json
import os
from .config import LAWS_DIR, MODULES_DIR, MODS_DIR

class Law:
    def __init__(self, law_id, title, content, category, severity, related_articles=None, source=None):
        self.law_id = law_id
        self.title = title
        self.content = content
        self.category = category
        self.severity = severity
        self.related_articles = related_articles or []
        self.source = source or ''
    
    def to_dict(self):
        return {
            'law_id': self.law_id,
            'title': self.title,
            'content': self.content,
            'category': self.category,
            'severity': self.severity,
            'related_articles': self.related_articles,
            'source': self.source
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            data['law_id'],
            data['title'],
            data['content'],
            data['category'],
            data['severity'],
            data.get('related_articles', []),
            data.get('source')
        )

class LawSystem:
    def __init__(self):
        self.laws = {}
        self.categories = set()
    
    def add_law(self, law):
        self.laws[law.law_id] = law
        self.categories.add(law.category)
    
    def get_law_by_id(self, law_id):
        return self.laws.get(law_id)
    
    def get_laws_by_category(self, category):
        return [law for law in self.laws.values() if law.category == category]
    
    def search_laws(self, keyword):
        results = []
        keyword = keyword.lower()
        for law in self.laws.values():
            if keyword in law.title.lower() or keyword in law.content.lower():
                results.append(law)
        return results
    
    def load_laws(self):
        for filename in os.listdir(LAWS_DIR):
            filepath = os.path.join(LAWS_DIR, filename)
            if filename.endswith('.json'):
                self.load_from_json(filepath)
            elif filename.endswith('.txt') or filename.endswith('.md'):
                self.load_from_text(filepath)
        
        self.load_module_laws()
    
    def load_module_laws(self):
        for modules_base_dir in [MODULES_DIR, MODS_DIR]:
            if os.path.exists(modules_base_dir):
                for module_name in os.listdir(modules_base_dir):
                    module_dir = os.path.join(modules_base_dir, module_name)
                    if os.path.isdir(module_dir):
                        laws_dir = os.path.join(module_dir, 'laws')
                        if os.path.exists(laws_dir):
                            for filename in os.listdir(laws_dir):
                                filepath = os.path.join(laws_dir, filename)
                                if filename.endswith('.json'):
                                    self.load_from_json(filepath)
                                elif filename.endswith('.txt') or filename.endswith('.md'):
                                    self.load_from_text(filepath)
    
    def load_from_json(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for law_data in data:
                self.add_law(Law.from_dict(law_data))
    
    def load_from_text(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        law_id = os.path.splitext(os.path.basename(filepath))[0]
        title = ''
        category = '未分类'
        severity = '中'
        source = ''
        law_content = ''
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if line.startswith('## '):
                title = line[3:].strip()
            elif line.startswith('### '):
                category = line[4:].strip()
            elif line.startswith('来源:') or line.startswith('来源：'):
                source = line[3:].strip()
            elif line.startswith('严重程度:') or line.startswith('严重程度：'):
                severity = line[5:].strip()
            elif line:
                law_content += line + '\n'
            
            i += 1
        
        if not title:
            title = law_id
        
        law = Law(
            law_id=law_id,
            title=title,
            content=law_content.strip(),
            category=category,
            severity=severity,
            source=source
        )
        self.add_law(law)
    
    def save_to_json(self, filepath):
        data = [law.to_dict() for law in self.laws.values()]
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def get_all_categories(self):
        return sorted(list(self.categories))