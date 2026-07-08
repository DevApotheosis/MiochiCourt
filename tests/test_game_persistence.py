import unittest
import os
import sys
import tempfile
import shutil
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.save_system import GameSave, SaveManager
from src.core.config_manager import ConfigManager, DEFAULT_SHORTCUTS
from src.core.case_manager import Case


class TestGamePersistence(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        
        os.makedirs(os.path.join(self.temp_dir, 'saves'), exist_ok=True)
        os.makedirs(os.path.join(self.temp_dir, 'cases'), exist_ok=True)
        
        self.original_config_file = ConfigManager.CONFIG_FILE
        ConfigManager.CONFIG_FILE = os.path.join(self.temp_dir, 'player_config.json')
        
        self.save_manager = SaveManager()
        self.config_manager = ConfigManager()
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
        ConfigManager.CONFIG_FILE = self.original_config_file
    
    def test_player_name_not_required_on_start(self):
        saved_name = self.config_manager.get_player_name()
        self.assertEqual(saved_name, '')
        
        self.config_manager.set_player_name('')
        self.assertEqual(self.config_manager.get_player_name(), '')
        
        saved_name = self.config_manager.get_player_name()
        if not saved_name:
            self.config_manager.set_player_name('玩家')
        
        self.assertEqual(self.config_manager.get_player_name(), '玩家')
    
    def test_player_name_persists_after_relaunch(self):
        self.config_manager.set_player_name('测试律师')
        
        new_config = ConfigManager()
        self.assertEqual(new_config.get_player_name(), '测试律师')
    
    def test_case_progress_persists_after_relaunch(self):
        case_progress = {
            'case_001': {'status': 'completed', 'verdict': 'innocent', 'reason': '证据充分'},
            'case_002': {'status': 'investigation', 'evidence_collected': ['ev_001']}
        }
        
        self.save_manager.auto_save(
            player_name='测试律师',
            current_case_id='case_001',
            case_status='completed',
            evidence_collected=['ev_001', 'ev_002'],
            evidence_analyzed=['ev_001'],
            witness_trust={},
            dialogue_history=[],
            game_time=30,
            player_data={'level': 2, 'experience': 100},
            case_progress=case_progress
        )
        
        new_save_manager = SaveManager()
        loaded_save = new_save_manager.get_save_by_id(SaveManager.AUTO_SAVE_ID)
        
        self.assertIsNotNone(loaded_save)
        self.assertEqual(loaded_save.player_name, '测试律师')
        self.assertEqual(loaded_save.case_progress['case_001']['status'], 'completed')
        self.assertEqual(loaded_save.case_progress['case_001']['verdict'], 'innocent')
        self.assertEqual(loaded_save.case_progress['case_002']['status'], 'investigation')
        self.assertEqual(loaded_save.player_data['level'], 2)
        self.assertEqual(loaded_save.player_data['experience'], 100)
    
    def test_case_progress_merge_preserves_existing_data(self):
        initial_progress = {
            'case_001': {'status': 'completed', 'verdict': 'innocent'}
        }
        
        self.save_manager.auto_save(
            player_name='测试律师',
            current_case_id='case_001',
            case_status='completed',
            evidence_collected=[],
            evidence_analyzed=[],
            witness_trust={},
            dialogue_history=[],
            game_time=0,
            player_data={},
            case_progress=initial_progress
        )
        
        new_progress = {
            'case_002': {'status': 'completed', 'verdict': 'major'}
        }
        
        existing_save = self.save_manager.get_save_by_id(SaveManager.AUTO_SAVE_ID)
        existing_progress = existing_save.case_progress if existing_save else {}
        existing_progress.update(new_progress)
        
        self.save_manager.auto_save(
            player_name='测试律师',
            current_case_id='case_002',
            case_status='completed',
            evidence_collected=[],
            evidence_analyzed=[],
            witness_trust={},
            dialogue_history=[],
            game_time=0,
            player_data={},
            case_progress=existing_progress
        )
        
        loaded_save = self.save_manager.get_save_by_id(SaveManager.AUTO_SAVE_ID)
        
        self.assertIn('case_001', loaded_save.case_progress)
        self.assertEqual(loaded_save.case_progress['case_001']['status'], 'completed')
        self.assertIn('case_002', loaded_save.case_progress)
        self.assertEqual(loaded_save.case_progress['case_002']['status'], 'completed')
    
    def test_completed_case_status_remains_after_main_menu_return(self):
        case_progress = {
            'case_001': {'status': 'completed', 'verdict': 'innocent', 'reason': '证据充分'}
        }
        
        self.save_manager.auto_save(
            player_name='测试律师',
            current_case_id='case_001',
            case_status='completed',
            evidence_collected=['ev_001'],
            evidence_analyzed=['ev_001'],
            witness_trust={},
            dialogue_history=[],
            game_time=30,
            player_data={},
            case_progress=case_progress
        )
        
        loaded_save = self.save_manager.get_save_by_id(SaveManager.AUTO_SAVE_ID)
        self.assertEqual(loaded_save.case_progress['case_001']['status'], 'completed')
        
        self.save_manager.auto_save(
            player_name='测试律师',
            current_case_id=None,
            case_status='investigation',
            evidence_collected=[],
            evidence_analyzed=[],
            witness_trust={},
            dialogue_history=[],
            game_time=0,
            player_data={},
            case_progress=loaded_save.case_progress
        )
        
        reloaded_save = self.save_manager.get_save_by_id(SaveManager.AUTO_SAVE_ID)
        self.assertEqual(reloaded_save.case_progress['case_001']['status'], 'completed')
    
    def test_player_role_persists_after_relaunch(self):
        self.config_manager.set_player_role('prosecution')
        
        new_config = ConfigManager()
        self.assertEqual(new_config.get_player_role(), 'prosecution')
        
        self.config_manager.set_player_role('defense')
        new_config2 = ConfigManager()
        self.assertEqual(new_config2.get_player_role(), 'defense')
    
    def test_shortcuts_persist_after_relaunch(self):
        self.config_manager.set_shortcut('collect_evidence', '<Control-x>')
        
        new_config = ConfigManager()
        shortcuts = new_config.get_shortcuts()
        
        self.assertEqual(shortcuts['collect_evidence'], '<Control-x>')
        self.assertEqual(shortcuts['analyze_evidence'], DEFAULT_SHORTCUTS['analyze_evidence'])


class TestCaseStatusConsistency(unittest.TestCase):
    def setUp(self):
        self.case = Case(
            case_id='test_case',
            title='测试案件',
            description='测试描述',
            defendant='张三',
            plaintiff='李四',
            location='北京',
            time='2026-07-08',
            difficulty=1
        )
    
    def test_case_status_transitions(self):
        self.assertEqual(self.case.status, 'investigation')
        
        self.case.set_status('court')
        self.assertEqual(self.case.status, 'court')
        
        self.case.set_status('completed')
        self.assertEqual(self.case.status, 'completed')
        
        self.case.set_status('invalid')
        self.assertEqual(self.case.status, 'completed')
    
    def test_case_status_label(self):
        self.assertEqual(self.case.get_status_label(), '调查中')
        
        self.case.set_status('court')
        self.assertEqual(self.case.get_status_label(), '庭审中')
        
        self.case.set_status('completed')
        self.assertEqual(self.case.get_status_label(), '已完成')
    
    def test_verdict_persistence(self):
        self.case.verdict_guilt = 'innocent'
        self.case.verdict_reason = '证据充分'
        
        case_dict = self.case.to_dict()
        restored_case = Case.from_dict(case_dict)
        
        self.assertEqual(restored_case.verdict_guilt, 'innocent')
        self.assertEqual(restored_case.verdict_reason, '证据充分')


if __name__ == '__main__':
    unittest.main()