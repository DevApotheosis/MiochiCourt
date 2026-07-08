import json
import os
from .config import DIALOGUES_DIR, MODULES_DIR, MODS_DIR

class Dialogue:
    def __init__(self, dialogue_id, speaker, text, choices=None, next_dialogue=None, 
                 trigger_evidence=None, required_evidence=None, effect=None):
        self.dialogue_id = dialogue_id
        self.speaker = speaker
        self.text = text
        self.choices = choices or []
        self.next_dialogue = next_dialogue
        self.trigger_evidence = trigger_evidence
        self.required_evidence = required_evidence
        self.effect = effect or {}
    
    def has_choices(self):
        return len(self.choices) > 0
    
    def to_dict(self):
        return {
            'dialogue_id': self.dialogue_id,
            'speaker': self.speaker,
            'text': self.text,
            'choices': self.choices,
            'next_dialogue': self.next_dialogue,
            'trigger_evidence': self.trigger_evidence,
            'required_evidence': self.required_evidence,
            'effect': self.effect
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            data['dialogue_id'],
            data['speaker'],
            data['text'],
            data.get('choices', []),
            data.get('next_dialogue'),
            data.get('trigger_evidence'),
            data.get('required_evidence'),
            data.get('effect', {})
        )

class DialogueManager:
    def __init__(self):
        self.dialogues = {}
        self.current_dialogue = None
        self.dialogue_history = []
    
    def add_dialogue(self, dialogue):
        self.dialogues[dialogue.dialogue_id] = dialogue
    
    def get_dialogue_by_id(self, dialogue_id):
        return self.dialogues.get(dialogue_id)
    
    def set_current_dialogue(self, dialogue_id):
        self.current_dialogue = self.get_dialogue_by_id(dialogue_id)
    
    def get_current_dialogue(self):
        return self.current_dialogue
    
    def advance_dialogue(self, choice_index=None):
        if not self.current_dialogue:
            return None
        
        self.dialogue_history.append(self.current_dialogue)
        
        if choice_index is not None and self.current_dialogue.has_choices():
            if 0 <= choice_index < len(self.current_dialogue.choices):
                choice = self.current_dialogue.choices[choice_index]
                next_id = choice.get('next_dialogue')
                if next_id:
                    self.current_dialogue = self.get_dialogue_by_id(next_id)
                    return self.current_dialogue, choice.get('effect')
        elif self.current_dialogue.next_dialogue:
            self.current_dialogue = self.get_dialogue_by_id(self.current_dialogue.next_dialogue)
            return self.current_dialogue, None
        
        return None, None
    
    def load_dialogues(self, case_id):
        dialogue_file = os.path.join(DIALOGUES_DIR, f'{case_id}.json')
        if os.path.exists(dialogue_file):
            self.load_from_json(dialogue_file)
        
        for modules_base_dir in [MODULES_DIR, MODS_DIR]:
            if os.path.exists(modules_base_dir):
                for module_name in os.listdir(modules_base_dir):
                    module_dir = os.path.join(modules_base_dir, module_name)
                    if os.path.isdir(module_dir):
                        dialogues_dir = os.path.join(module_dir, 'dialogues')
                        if os.path.exists(dialogues_dir):
                            module_dialogue_file = os.path.join(dialogues_dir, f'{case_id}.json')
                            if os.path.exists(module_dialogue_file):
                                self.load_from_json(module_dialogue_file)
    
    def load_from_json(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for dialogue_data in data:
                self.add_dialogue(Dialogue.from_dict(dialogue_data))
    
    def save_to_json(self, filepath):
        data = [dialogue.to_dict() for dialogue in self.dialogues.values()]
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def get_speakers(self):
        speakers = set()
        for dialogue in self.dialogues.values():
            speakers.add(dialogue.speaker)
        return sorted(list(speakers))
    
    def get_dialogues_by_speaker(self, speaker):
        return [d for d in self.dialogues.values() if d.speaker == speaker]
    
    def reset(self):
        self.current_dialogue = None
        self.dialogue_history = []