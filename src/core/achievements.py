import json
import os
from datetime import datetime
from .config import ACHIEVEMENTS_DIR, ACHIEVEMENT_TYPES

class Achievement:
    def __init__(self, achievement_id, name, description, unlocked=False, unlocked_at=None, icon=None):
        self.achievement_id = achievement_id
        self.name = name
        self.description = description
        self.unlocked = unlocked
        self.unlocked_at = unlocked_at
        self.icon = icon
    
    def unlock(self):
        if not self.unlocked:
            self.unlocked = True
            self.unlocked_at = datetime.now().isoformat()
    
    def to_dict(self):
        return {
            'achievement_id': self.achievement_id,
            'name': self.name,
            'description': self.description,
            'unlocked': self.unlocked,
            'unlocked_at': self.unlocked_at,
            'icon': self.icon
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            data['achievement_id'],
            data['name'],
            data['description'],
            data.get('unlocked', False),
            data.get('unlocked_at'),
            data.get('icon')
        )

class AchievementManager:
    def __init__(self):
        self.achievements = {}
        self._initialize_default_achievements()
    
    def _initialize_default_achievements(self):
        default_achievements = [
            {'achievement_id': 'first_case', 'name': '初出茅庐', 'description': '完成第一个案件的调查'},
            {'achievement_id': 'first_verdict', 'name': '初次裁决', 'description': '在法庭上完成第一次裁决'},
            {'achievement_id': 'all_cases', 'name': '审判大师', 'description': '完成所有案件'},
            {'achievement_id': 'perfect_evidence', 'name': '完美取证', 'description': '在一个案件中收集所有证据'},
            {'achievement_id': 'high_trust', 'name': '心灵捕手', 'description': '将证人信任度提升到100'},
            {'achievement_id': 'law_expert', 'name': '法律专家', 'description': '熟悉所有法律条文'},
            {'achievement_id': 'speed_run', 'name': '神速审判', 'description': '在30分钟内完成一个案件'},
            {'achievement_id': 'key_evidence', 'name': '关键突破', 'description': '发现关键证据'},
            {'achievement_id': 'analyst', 'name': '分析大师', 'description': '分析所有收集的证据'},
            {'achievement_id': 'module_master', 'name': '模组专家', 'description': '安装第一个模组'}
        ]
        
        for ach_data in default_achievements:
            self.add_achievement(Achievement.from_dict(ach_data))
    
    def add_achievement(self, achievement):
        self.achievements[achievement.achievement_id] = achievement
    
    def get_achievement_by_id(self, achievement_id):
        return self.achievements.get(achievement_id)
    
    def unlock_achievement(self, achievement_id):
        achievement = self.get_achievement_by_id(achievement_id)
        if achievement:
            achievement.unlock()
            return True
        return False
    
    def is_unlocked(self, achievement_id):
        achievement = self.get_achievement_by_id(achievement_id)
        return achievement and achievement.unlocked
    
    def get_unlocked_achievements(self):
        return [a for a in self.achievements.values() if a.unlocked]
    
    def get_locked_achievements(self):
        return [a for a in self.achievements.values() if not a.unlocked]
    
    def get_progress(self):
        total = len(self.achievements)
        unlocked = len(self.get_unlocked_achievements())
        return unlocked, total
    
    def save_to_file(self, player_name='player'):
        filepath = os.path.join(ACHIEVEMENTS_DIR, f'{player_name}_achievements.json')
        data = [ach.to_dict() for ach in self.achievements.values()]
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    
    def load_from_file(self, player_name='player'):
        self.achievements = {}
        self._initialize_default_achievements()
        
        filepath = os.path.join(ACHIEVEMENTS_DIR, f'{player_name}_achievements.json')
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for ach_data in data:
                    existing = self.get_achievement_by_id(ach_data['achievement_id'])
                    if existing:
                        existing.unlocked = ach_data.get('unlocked', False)
                        existing.unlocked_at = ach_data.get('unlocked_at')
            return True
        return False