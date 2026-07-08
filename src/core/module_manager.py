import json
import os
import shutil
from .config import MODULES_DIR

class Module:
    def __init__(self, module_id, name, version, author, description, 
                 cases=None, laws=None, evidence=None, dialogues=None):
        self.module_id = module_id
        self.name = name
        self.version = version
        self.author = author
        self.description = description
        self.cases = cases or []
        self.laws = laws or []
        self.evidence = evidence or []
        self.dialogues = dialogues or []
    
    def to_dict(self):
        return {
            'module_id': self.module_id,
            'name': self.name,
            'version': self.version,
            'author': self.author,
            'description': self.description,
            'cases': self.cases,
            'laws': self.laws,
            'evidence': self.evidence,
            'dialogues': self.dialogues
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            data['module_id'],
            data['name'],
            data['version'],
            data['author'],
            data['description'],
            data.get('cases', []),
            data.get('laws', []),
            data.get('evidence', []),
            data.get('dialogues', [])
        )

class ModuleManager:
    def __init__(self):
        self.modules = {}
        self.installed_modules = []
    
    def add_module(self, module):
        self.modules[module.module_id] = module
    
    def get_module_by_id(self, module_id):
        return self.modules.get(module_id)
    
    def install_module(self, module_path):
        try:
            module_dir = os.path.basename(module_path)
            target_dir = os.path.join(MODULES_DIR, module_dir)
            
            if os.path.exists(target_dir):
                shutil.rmtree(target_dir)
            
            shutil.copytree(module_path, target_dir)
            
            config_file = os.path.join(target_dir, 'module.json')
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    module = Module.from_dict(data)
                    self.add_module(module)
                    self.installed_modules.append(module.module_id)
                    return True
            
            return False
        except Exception as e:
            print(f'Failed to install module: {e}')
            return False
    
    def uninstall_module(self, module_id):
        try:
            module = self.get_module_by_id(module_id)
            if module:
                module_dir = os.path.join(MODULES_DIR, module_id)
                if os.path.exists(module_dir):
                    shutil.rmtree(module_dir)
                del self.modules[module_id]
                self.installed_modules.remove(module_id)
                return True
            return False
        except Exception as e:
            print(f'Failed to uninstall module: {e}')
            return False
    
    def load_modules(self):
        for dirname in os.listdir(MODULES_DIR):
            module_dir = os.path.join(MODULES_DIR, dirname)
            if os.path.isdir(module_dir):
                config_file = os.path.join(module_dir, 'module.json')
                if os.path.exists(config_file):
                    try:
                        with open(config_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            module = Module.from_dict(data)
                            self.add_module(module)
                            self.installed_modules.append(module.module_id)
                    except Exception as e:
                        print(f'Failed to load module {dirname}: {e}')
    
    def get_all_modules(self):
        return list(self.modules.values())
    
    def get_installed_modules(self):
        return [self.modules[mid] for mid in self.installed_modules]