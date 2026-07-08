import json
import os

class Skill:
    def __init__(self, skill_id, name, description, level=1, max_level=5):
        self.skill_id = skill_id
        self.name = name
        self.description = description
        self.level = level
        self.max_level = max_level
    
    def upgrade(self):
        if self.level < self.max_level:
            self.level += 1
            return True
        return False
    
    def get_effect(self):
        effects = {
            'investigation': {'evidence_bonus': self.level * 5},
            'persuasion': {'trust_bonus': self.level * 10},
            'analysis': {'analysis_speed': self.level * 15},
            'law_knowledge': {'law_bonus': self.level * 8},
            'tech_skill': {'tech_bonus': self.level * 12}
        }
        return effects.get(self.skill_id, {})
    
    def to_dict(self):
        return {
            'skill_id': self.skill_id,
            'name': self.name,
            'description': self.description,
            'level': self.level,
            'max_level': self.max_level
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            data['skill_id'],
            data['name'],
            data['description'],
            data.get('level', 1),
            data.get('max_level', 5)
        )

class Character:
    LAWYER_LEVELS = [
        {'name': '实习律师', 'min_exp': 0, 'max_exp': 100},
        {'name': '初级律师', 'min_exp': 100, 'max_exp': 300},
        {'name': '三级律师', 'min_exp': 300, 'max_exp': 600},
        {'name': '二级律师', 'min_exp': 600, 'max_exp': 1000},
        {'name': '一级律师', 'min_exp': 1000, 'max_exp': float('inf')}
    ]
    
    def __init__(self, name='玩家', level=1, experience=0, skills=None, stats=None):
        self.name = name
        self.level = level
        self.experience = experience
        self.skills = skills or {}
        self.stats = stats or {}
        
        if not self.skills:
            self._initialize_default_skills()
        
        if not self.stats:
            self._initialize_default_stats()
    
    def _initialize_default_skills(self):
        default_skills = [
            Skill('investigation', '调查技巧', '提高证据收集效率', 1),
            Skill('persuasion', '说服能力', '提高证人信任度获取', 1),
            Skill('analysis', '分析能力', '提高证据分析速度', 1),
            Skill('law_knowledge', '法律知识', '提高法律引用效果', 1),
            Skill('tech_skill', '技术能力', '提高技术证据处理能力', 1)
        ]
        
        for skill in default_skills:
            self.skills[skill.skill_id] = skill
    
    def _initialize_default_stats(self):
        self.stats = {
            'cases_completed': 0,
            'evidence_collected': 0,
            'evidence_analyzed': 0,
            'witnesses_interviewed': 0,
            'laws_referenced': 0,
            'total_game_time': 0
        }
    
    def add_experience(self, amount):
        self.experience += amount
        while self.experience >= self._get_exp_for_next_level():
            self.experience -= self._get_exp_for_next_level()
            self.level += 1
    
    def _get_exp_for_next_level(self):
        return self.level * 100
    
    def get_exp_progress(self):
        return self.experience, self._get_exp_for_next_level()
    
    def get_lawyer_rank(self):
        for rank in self.LAWYER_LEVELS:
            if rank['min_exp'] <= self.experience < rank['max_exp']:
                return rank['name']
        return self.LAWYER_LEVELS[-1]['name']
    
    def get_rank_index(self):
        for i, rank in enumerate(self.LAWYER_LEVELS):
            if rank['min_exp'] <= self.experience < rank['max_exp']:
                return i
        return len(self.LAWYER_LEVELS) - 1
    
    def upgrade_skill(self, skill_id):
        if skill_id in self.skills:
            return self.skills[skill_id].upgrade()
        return False
    
    def get_skill(self, skill_id):
        return self.skills.get(skill_id)
    
    def get_all_skills(self):
        return list(self.skills.values())
    
    def update_stat(self, stat_name, value):
        if stat_name in self.stats:
            self.stats[stat_name] += value
    
    def to_dict(self):
        return {
            'name': self.name,
            'level': self.level,
            'experience': self.experience,
            'skills': {k: v.to_dict() for k, v in self.skills.items()},
            'stats': self.stats
        }
    
    @classmethod
    def from_dict(cls, data):
        skills = {}
        if 'skills' in data:
            for k, v in data['skills'].items():
                skills[k] = Skill.from_dict(v)
        
        return cls(
            data.get('name', '玩家'),
            data.get('level', 1),
            data.get('experience', 0),
            skills,
            data.get('stats', {})
        )