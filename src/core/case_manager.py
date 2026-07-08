import json
import os
from .config import CASES_DIR, CASE_STATUS, GUILT_LEVELS, MODULES_DIR, MODS_DIR
from .evidence import EvidenceManager

class Case:
    def __init__(self, case_id, title, description, defendant, plaintiff, location, time, difficulty, 
                 required_evidence=None, key_laws=None, witnesses=None, verdict_guilt=None, 
                 verdict_reason=None, background=None, parties=None, tags=None, allow_roles=None):
        self.case_id = case_id
        self.title = title
        self.description = description
        self.defendant = defendant
        self.plaintiff = plaintiff
        self.location = location
        self.time = time
        self.difficulty = difficulty
        self.required_evidence = required_evidence or []
        self.key_laws = key_laws or []
        self.witnesses = witnesses or []
        self.verdict_guilt = verdict_guilt
        self.verdict_reason = verdict_reason
        self.status = 'investigation'
        self.background = background or ''
        self.parties = parties or {}
        self.tags = tags or []
        self.allow_roles = allow_roles or ['defense', 'prosecution']
        self.evidence_manager = EvidenceManager()
        self.evidence_manager.load_case_evidence(case_id)
    
    def set_status(self, status):
        if status in CASE_STATUS:
            self.status = status
    
    def get_status_label(self):
        return CASE_STATUS.get(self.status, self.status)
    
    def get_guilt_label(self):
        return GUILT_LEVELS.get(self.verdict_guilt, self.verdict_guilt)
    
    def is_role_allowed(self, role):
        return role in self.allow_roles
    
    def get_allowed_roles(self):
        return self.allow_roles.copy()
    
    def to_dict(self):
        return {
            'case_id': self.case_id,
            'title': self.title,
            'description': self.description,
            'defendant': self.defendant,
            'plaintiff': self.plaintiff,
            'location': self.location,
            'time': self.time,
            'difficulty': self.difficulty,
            'required_evidence': self.required_evidence,
            'key_laws': self.key_laws,
            'witnesses': self.witnesses,
            'verdict_guilt': self.verdict_guilt,
            'verdict_reason': self.verdict_reason,
            'status': self.status,
            'background': self.background,
            'parties': self.parties,
            'tags': self.tags,
            'allow_roles': self.allow_roles
        }
    
    @classmethod
    def from_dict(cls, data):
        case = cls(
            data['case_id'],
            data['title'],
            data['description'],
            data['defendant'],
            data['plaintiff'],
            data['location'],
            data['time'],
            data['difficulty'],
            data.get('required_evidence', []),
            data.get('key_laws', []),
            data.get('witnesses', []),
            data.get('verdict_guilt'),
            data.get('verdict_reason'),
            data.get('background'),
            data.get('parties'),
            data.get('tags'),
            data.get('allow_roles')
        )
        case.status = data.get('status', 'investigation')
        return case

class CaseManager:
    def __init__(self):
        self.cases = {}
        self.current_case = None
    
    def add_case(self, case):
        self.cases[case.case_id] = case
    
    def get_case_by_id(self, case_id):
        return self.cases.get(case_id)
    
    def set_current_case(self, case_id):
        self.current_case = self.get_case_by_id(case_id)
    
    def get_current_case(self):
        return self.current_case
    
    def load_cases(self):
        for filename in os.listdir(CASES_DIR):
            if filename.endswith('.json'):
                filepath = os.path.join(CASES_DIR, filename)
                case = self.load_from_json(filepath)
                if case:
                    self.add_case(case)
        
        self.load_module_cases()
    
    def load_module_cases(self):
        for modules_base_dir in [MODULES_DIR, MODS_DIR]:
            if os.path.exists(modules_base_dir):
                for module_name in os.listdir(modules_base_dir):
                    module_dir = os.path.join(modules_base_dir, module_name)
                    if os.path.isdir(module_dir):
                        cases_dir = os.path.join(module_dir, 'cases')
                        if os.path.exists(cases_dir):
                            for filename in os.listdir(cases_dir):
                                if filename.endswith('.json'):
                                    filepath = os.path.join(cases_dir, filename)
                                    case = self.load_from_json(filepath)
                                    if case:
                                        self.add_case(case)
    
    def load_from_json(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return Case.from_dict(data)
        except Exception as e:
            print(f'Failed to load case: {e}')
            return None
    
    def save_to_json(self, case, filepath):
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(case.to_dict(), f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f'Failed to save case: {e}')
            return False
    
    def get_all_cases(self):
        return sorted(self.cases.values(), key=lambda x: x.difficulty)
    
    def get_cases_by_difficulty(self, difficulty):
        return [case for case in self.cases.values() if case.difficulty == difficulty]