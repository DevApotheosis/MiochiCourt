import json
import os
import hashlib
from datetime import datetime
from .config import DOSSIER_DIR


class Dossier:
    def __init__(self, dossier_id, player_name, case_id, case_title, 
                 verdict, verdict_reason, evidence_chain, 
                 witness_statements, trial_scores, judge_mood,
                 created_at=None):
        self.dossier_id = dossier_id
        self.player_name = player_name
        self.case_id = case_id
        self.case_title = case_title
        self.verdict = verdict
        self.verdict_reason = verdict_reason
        self.evidence_chain = evidence_chain or []
        self.witness_statements = witness_statements or {}
        self.trial_scores = trial_scores or {}
        self.judge_mood = judge_mood
        self.created_at = created_at or datetime.now().isoformat()
        self.encrypted = False
    
    def to_dict(self):
        return {
            'dossier_id': self.dossier_id,
            'player_name': self.player_name,
            'case_id': self.case_id,
            'case_title': self.case_title,
            'verdict': self.verdict,
            'verdict_reason': self.verdict_reason,
            'evidence_chain': self.evidence_chain,
            'witness_statements': self.witness_statements,
            'trial_scores': self.trial_scores,
            'judge_mood': self.judge_mood,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            data['dossier_id'],
            data['player_name'],
            data['case_id'],
            data['case_title'],
            data['verdict'],
            data['verdict_reason'],
            data.get('evidence_chain', []),
            data.get('witness_statements', {}),
            data.get('trial_scores', {}),
            data.get('judge_mood', 50),
            data.get('created_at')
        )


class DossierManager:
    def __init__(self):
        self.dossiers = {}
    
    def _generate_checksum(self, data):
        json_data = json.dumps(data, ensure_ascii=False, sort_keys=True)
        return hashlib.md5(json_data.encode()).hexdigest()
    
    def create_dossier(self, player_name, case, verdict, verdict_reason, 
                       evidence_chain, witness_statements, trial_scores, judge_mood):
        dossier_id = f'dossier_{case.case_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        
        dossier = Dossier(
            dossier_id=dossier_id,
            player_name=player_name,
            case_id=case.case_id,
            case_title=case.title,
            verdict=verdict,
            verdict_reason=verdict_reason,
            evidence_chain=evidence_chain,
            witness_statements=witness_statements,
            trial_scores=trial_scores,
            judge_mood=judge_mood
        )
        
        self.dossiers[dossier_id] = dossier
        return dossier
    
    def save_dossier(self, dossier):
        filepath = os.path.join(DOSSIER_DIR, f'{dossier.dossier_id}.json')
        
        data = dossier.to_dict()
        data['checksum'] = self._generate_checksum(data)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return True
    
    def load_dossier(self, dossier_id):
        filepath = os.path.join(DOSSIER_DIR, f'{dossier_id}.json')
        
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                stored_checksum = data.pop('checksum', '')
                calculated_checksum = self._generate_checksum(data)
                
                if stored_checksum and stored_checksum != calculated_checksum:
                    return None
                
                dossier = Dossier.from_dict(data)
                self.dossiers[dossier_id] = dossier
                return dossier
        
        return None
    
    def delete_dossier(self, dossier_id):
        filepath = os.path.join(DOSSIER_DIR, f'{dossier_id}.json')
        
        if os.path.exists(filepath):
            os.remove(filepath)
            if dossier_id in self.dossiers:
                del self.dossiers[dossier_id]
            return True
        
        return False
    
    def get_all_dossiers(self):
        dossiers = []
        for filename in os.listdir(DOSSIER_DIR):
            if filename.endswith('.json'):
                dossier_id = filename[:-5]
                dossier = self.load_dossier(dossier_id)
                if dossier:
                    dossiers.append(dossier)
        
        return sorted(dossiers, key=lambda x: x.created_at, reverse=True)
    
    def get_dossiers_by_player(self, player_name):
        all_dossiers = self.get_all_dossiers()
        return [d for d in all_dossiers if d.player_name == player_name]
    
    def get_dossiers_by_case(self, case_id):
        all_dossiers = self.get_all_dossiers()
        return [d for d in all_dossiers if d.case_id == case_id]
    
    def get_success_rate(self, player_name=None):
        if player_name:
            dossiers = self.get_dossiers_by_player(player_name)
        else:
            dossiers = self.get_all_dossiers()
        
        if not dossiers:
            return 0
        
        success_count = sum(1 for d in dossiers if d.verdict == 'innocent')
        return (success_count / len(dossiers)) * 100
