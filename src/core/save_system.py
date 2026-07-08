import json
import os
from datetime import datetime
from .config import SAVES_DIR

class GameSave:
    VALID_STATUSES = ['investigation', 'court', 'completed']
    
    def __init__(self, save_id, player_name, current_case_id, case_status, 
                 evidence_collected, evidence_analyzed, witness_trust, 
                 dialogue_history, game_time, player_data=None, case_progress=None,
                 created_at=None, updated_at=None):
        self._validate_parameters(
            save_id=save_id,
            player_name=player_name,
            case_status=case_status,
            evidence_collected=evidence_collected,
            evidence_analyzed=evidence_analyzed,
            witness_trust=witness_trust,
            dialogue_history=dialogue_history,
            game_time=game_time
        )
        
        self.save_id = save_id
        self.player_name = player_name
        self.current_case_id = current_case_id
        self.case_status = case_status
        self.evidence_collected = evidence_collected or []
        self.evidence_analyzed = evidence_analyzed or []
        self.witness_trust = witness_trust or {}
        self.dialogue_history = dialogue_history or []
        self.game_time = game_time or 0
        self.player_data = player_data or {}
        self.case_progress = case_progress or {}
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at or datetime.now().isoformat()
    
    def _validate_parameters(self, **kwargs):
        if not kwargs.get('save_id'):
            raise ValueError('save_id is required')
        
        player_name = kwargs.get('player_name')
        if player_name is None:
            raise ValueError('player_name is required')
        
        case_status = kwargs.get('case_status')
        if case_status and case_status not in self.VALID_STATUSES:
            raise ValueError(f'case_status must be one of {self.VALID_STATUSES}')
        
        evidence_collected = kwargs.get('evidence_collected')
        if evidence_collected is not None and not isinstance(evidence_collected, list):
            raise TypeError('evidence_collected must be a list')
        
        evidence_analyzed = kwargs.get('evidence_analyzed')
        if evidence_analyzed is not None and not isinstance(evidence_analyzed, list):
            raise TypeError('evidence_analyzed must be a list')
        
        witness_trust = kwargs.get('witness_trust')
        if witness_trust is not None and not isinstance(witness_trust, dict):
            raise TypeError('witness_trust must be a dict')
        
        dialogue_history = kwargs.get('dialogue_history')
        if dialogue_history is not None and not isinstance(dialogue_history, list):
            raise TypeError('dialogue_history must be a list')
        
        game_time = kwargs.get('game_time')
        if game_time is not None and not isinstance(game_time, (int, float)):
            raise TypeError('game_time must be a number')
    
    def update_timestamp(self):
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self):
        return {
            'save_id': self.save_id,
            'player_name': self.player_name,
            'current_case_id': self.current_case_id,
            'case_status': self.case_status,
            'evidence_collected': self.evidence_collected,
            'evidence_analyzed': self.evidence_analyzed,
            'witness_trust': self.witness_trust,
            'dialogue_history': self.dialogue_history,
            'game_time': self.game_time,
            'player_data': self.player_data,
            'case_progress': self.case_progress,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            data['save_id'],
            data.get('player_name', '玩家'),
            data.get('current_case_id'),
            data.get('case_status', 'investigation'),
            data.get('evidence_collected', []),
            data.get('evidence_analyzed', []),
            data.get('witness_trust', {}),
            data.get('dialogue_history', []),
            data.get('game_time', 0),
            data.get('player_data', {}),
            data.get('case_progress', {}),
            data.get('created_at'),
            data.get('updated_at')
        )

class SaveManager:
    AUTO_SAVE_ID = 'auto_save'
    
    def __init__(self):
        self.saves = {}
    
    def create_save(self, player_name, current_case_id=None, case_status='investigation', 
                    player_data=None, case_progress=None):
        save_id = f'save_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        save = GameSave(
            save_id=save_id,
            player_name=player_name,
            current_case_id=current_case_id,
            case_status=case_status,
            evidence_collected=[],
            evidence_analyzed=[],
            witness_trust={},
            dialogue_history=[],
            game_time=0,
            player_data=player_data,
            case_progress=case_progress
        )
        self.saves[save_id] = save
        return save
    
    def auto_save(self, player_name, current_case_id, case_status, 
                  evidence_collected, evidence_analyzed, 
                  witness_trust, dialogue_history, game_time,
                  player_data=None, case_progress=None):
        if self.AUTO_SAVE_ID not in self.saves:
            self.saves[self.AUTO_SAVE_ID] = GameSave(
                save_id=self.AUTO_SAVE_ID,
                player_name=player_name,
                current_case_id=current_case_id,
                case_status=case_status,
                evidence_collected=evidence_collected,
                evidence_analyzed=evidence_analyzed,
                witness_trust=witness_trust,
                dialogue_history=dialogue_history,
                game_time=game_time,
                player_data=player_data,
                case_progress=case_progress
            )
        
        save = self.saves[self.AUTO_SAVE_ID]
        save.player_name = player_name
        save.current_case_id = current_case_id
        save.case_status = case_status
        save.evidence_collected = evidence_collected
        save.evidence_analyzed = evidence_analyzed
        save.witness_trust = witness_trust
        save.dialogue_history = dialogue_history
        save.game_time = game_time
        save.player_data = player_data or {}
        save.case_progress = case_progress or {}
        save.update_timestamp()
        
        return self._save_to_file(save)
    
    def save_game(self, save_id, current_case_id, case_status, 
                  evidence_collected, evidence_analyzed, 
                  witness_trust, dialogue_history, game_time,
                  player_data=None, case_progress=None):
        if save_id not in self.saves:
            save_id = f'save_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
            self.saves[save_id] = GameSave(
                save_id=save_id,
                player_name='player',
                current_case_id=current_case_id,
                case_status=case_status,
                evidence_collected=evidence_collected,
                evidence_analyzed=evidence_analyzed,
                witness_trust=witness_trust,
                dialogue_history=dialogue_history,
                game_time=game_time,
                player_data=player_data,
                case_progress=case_progress
            )
        
        save = self.saves[save_id]
        save.current_case_id = current_case_id
        save.case_status = case_status
        save.evidence_collected = evidence_collected
        save.evidence_analyzed = evidence_analyzed
        save.witness_trust = witness_trust
        save.dialogue_history = dialogue_history
        save.game_time = game_time
        save.player_data = player_data or {}
        save.case_progress = case_progress or {}
        save.update_timestamp()
        
        return self._save_to_file(save)
    
    def _save_to_file(self, save):
        filepath = os.path.join(SAVES_DIR, f'{save.save_id}.json')
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(save.to_dict(), f, ensure_ascii=False, indent=2)
        return True
    
    def load_game(self, save_id):
        filepath = os.path.join(SAVES_DIR, f'{save_id}.json')
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                save = GameSave.from_dict(data)
                self.saves[save_id] = save
                return save
        return None
    
    def delete_save(self, save_id):
        filepath = os.path.join(SAVES_DIR, f'{save_id}.json')
        if os.path.exists(filepath):
            os.remove(filepath)
            if save_id in self.saves:
                del self.saves[save_id]
            return True
        return False
    
    def get_all_saves(self):
        saves = []
        for filename in os.listdir(SAVES_DIR):
            if filename.endswith('.json'):
                save_id = filename[:-5]
                filepath = os.path.join(SAVES_DIR, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        saves.append(GameSave.from_dict(data))
                except:
                    continue
        return sorted(saves, key=lambda x: x.updated_at, reverse=True)
    
    def get_save_by_id(self, save_id):
        if save_id in self.saves:
            return self.saves[save_id]
        return self.load_game(save_id)