import json
import os
from .config import EVIDENCE_DIR, MODULES_DIR, MODS_DIR, EVIDENCE_TYPES

class Evidence:
    def __init__(self, evidence_id, name, evidence_type, description, location, is_key=False, details=None):
        self.evidence_id = evidence_id
        self.name = name
        self.evidence_type = evidence_type
        self.description = description
        self.location = location
        self.is_key = is_key
        self.details = details or {}
        self.collected = False
        self.analyzed = False
        self.analysis_result = None
    
    def collect(self):
        self.collected = True
    
    def analyze(self, analysis_result=None):
        self.analyzed = True
        self.analysis_result = analysis_result
    
    def get_type_label(self):
        return EVIDENCE_TYPES.get(self.evidence_type, self.evidence_type)
    
    def to_dict(self):
        return {
            'evidence_id': self.evidence_id,
            'name': self.name,
            'evidence_type': self.evidence_type,
            'description': self.description,
            'location': self.location,
            'is_key': self.is_key,
            'details': self.details,
            'collected': self.collected,
            'analyzed': self.analyzed,
            'analysis_result': self.analysis_result
        }
    
    @classmethod
    def from_dict(cls, data):
        evidence = cls(
            data['evidence_id'],
            data['name'],
            data['evidence_type'],
            data['description'],
            data['location'],
            data.get('is_key', False),
            data.get('details', {})
        )
        evidence.collected = data.get('collected', False)
        evidence.analyzed = data.get('analyzed', False)
        evidence.analysis_result = data.get('analysis_result')
        return evidence

class EvidenceManager:
    def __init__(self):
        self.evidence_list = []
    
    def add_evidence(self, evidence):
        existing = self.get_evidence_by_id(evidence.evidence_id)
        if existing is None:
            self.evidence_list.append(evidence)
    
    def get_evidence_by_id(self, evidence_id):
        for ev in self.evidence_list:
            if ev.evidence_id == evidence_id:
                return ev
        return None
    
    def get_collected_evidence(self):
        return [ev for ev in self.evidence_list if ev.collected]
    
    def get_uncollected_evidence(self):
        return [ev for ev in self.evidence_list if not ev.collected]
    
    def get_key_evidence(self):
        return [ev for ev in self.evidence_list if ev.is_key and ev.collected]
    
    def collect_evidence(self, evidence_id):
        evidence = self.get_evidence_by_id(evidence_id)
        if evidence:
            evidence.collect()
            return True
        return False
    
    def analyze_evidence(self, evidence_id, analysis_result):
        evidence = self.get_evidence_by_id(evidence_id)
        if evidence:
            evidence.analyze(analysis_result)
            return True
        return False
    
    def load_from_json(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for ev_data in data:
                self.add_evidence(Evidence.from_dict(ev_data))
    
    def save_to_json(self, filepath):
        data = [ev.to_dict() for ev in self.evidence_list]
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def get_analyzed_evidence(self):
        return [ev for ev in self.evidence_list if ev.analyzed]
    
    def reset_evidence(self):
        for ev in self.evidence_list:
            ev.collected = False
            ev.analyzed = False
            ev.analysis_result = None
    
    def load_case_evidence(self, case_id):
        evidence_file = os.path.join(EVIDENCE_DIR, f'{case_id}.json')
        if os.path.exists(evidence_file):
            self.load_from_json(evidence_file)
        
        for modules_base_dir in [MODULES_DIR, MODS_DIR]:
            if os.path.exists(modules_base_dir):
                for module_name in os.listdir(modules_base_dir):
                    module_dir = os.path.join(modules_base_dir, module_name)
                    if os.path.isdir(module_dir):
                        evidence_dir = os.path.join(module_dir, 'evidence')
                        if os.path.exists(evidence_dir):
                            module_evidence_file = os.path.join(evidence_dir, f'{case_id}.json')
                            if os.path.exists(module_evidence_file):
                                self.load_from_json(module_evidence_file)