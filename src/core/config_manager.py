import json
import os
from .config import DATA_DIR


class ConfigManager:
    CONFIG_FILE = os.path.join(DATA_DIR, 'player_config.json')
    
    def __init__(self):
        self.config = self._load_config()
    
    def _load_config(self):
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_config(self):
        with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
    
    def get_player_name(self):
        return self.config.get('player_name', '')
    
    def set_player_name(self, name):
        self.config['player_name'] = name
        self._save_config()
    
    def get_player_role(self):
        return self.config.get('player_role', 'defense')
    
    def set_player_role(self, role):
        if role in ['defense', 'prosecution']:
            self.config['player_role'] = role
            self._save_config()
    
    def get_all_config(self):
        return self.config.copy()
    
    def clear_config(self):
        self.config = {}
        if os.path.exists(self.CONFIG_FILE):
            os.remove(self.CONFIG_FILE)
