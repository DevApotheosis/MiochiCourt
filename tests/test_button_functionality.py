import unittest
import os
import sys
import tempfile
import shutil
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.save_system import GameSave, SaveManager
from src.core.case_manager import CaseManager, Case
from src.core.config_manager import ConfigManager, DEFAULT_SHORTCUTS
from src.gui.court_view import CourtView
from src.gui.verdict_view import VerdictView


class TestSaveProgressMerge(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        original_saves_dir = os.environ.get('SAVES_DIR', '')
        os.environ['SAVES_DIR'] = self.temp_dir
        self.save_manager = SaveManager()
        SaveManager.AUTO_SAVE_ID = 'auto_save_test'

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_case_progress_merge_preserves_other_cases(self):
        self.save_manager.auto_save(
            player_name='test_player',
            current_case_id='case_001',
            case_status='completed',
            evidence_collected=['ev_001'],
            evidence_analyzed=['ev_001'],
            witness_trust={'张三': 80},
            dialogue_history=[],
            game_time=60,
            case_progress={'case_001': {'status': 'completed', 'verdict': 'innocent'}}
        )

        existing_save = self.save_manager.get_save_by_id(SaveManager.AUTO_SAVE_ID)
        existing_progress = existing_save.case_progress if existing_save else {}
        existing_progress['case_002'] = {'status': 'investigation', 'evidence_collected': []}

        self.save_manager.auto_save(
            player_name='test_player',
            current_case_id='case_002',
            case_status='investigation',
            evidence_collected=['ev_003'],
            evidence_analyzed=[],
            witness_trust={},
            dialogue_history=[],
            game_time=10,
            case_progress=existing_progress
        )

        loaded_save = self.save_manager.load_game(SaveManager.AUTO_SAVE_ID)
        self.assertIn('case_001', loaded_save.case_progress)
        self.assertIn('case_002', loaded_save.case_progress)
        self.assertEqual(loaded_save.case_progress['case_001']['status'], 'completed')
        self.assertEqual(loaded_save.case_progress['case_002']['status'], 'investigation')

    def test_completed_case_status_preserved_after_other_case_start(self):
        self.save_manager.auto_save(
            player_name='test_player',
            current_case_id='case_001',
            case_status='completed',
            evidence_collected=['ev_001'],
            evidence_analyzed=['ev_001'],
            witness_trust={'张三': 100},
            dialogue_history=[],
            game_time=120,
            case_progress={'case_001': {'status': 'completed', 'verdict': 'innocent'}}
        )

        existing_save = self.save_manager.get_save_by_id(SaveManager.AUTO_SAVE_ID)
        existing_progress = existing_save.case_progress if existing_save else {}
        existing_progress['case_002'] = {'status': 'investigation'}

        self.save_manager.auto_save(
            player_name='test_player',
            current_case_id='case_002',
            case_status='investigation',
            evidence_collected=[],
            evidence_analyzed=[],
            witness_trust={},
            dialogue_history=[],
            game_time=0,
            case_progress=existing_progress
        )

        reloaded_save = self.save_manager.load_game(SaveManager.AUTO_SAVE_ID)
        self.assertEqual(reloaded_save.case_progress['case_001']['status'], 'completed')
        self.assertNotEqual(reloaded_save.case_progress['case_001']['status'], 'investigation')


class TestVerdictRoleBased(unittest.TestCase):
    def test_defense_verdict_mapping(self):
        case = Case(
            case_id='case_001',
            title='测试案件',
            description='测试描述',
            defendant='张三',
            plaintiff='李四',
            location='测试地点',
            time='2026-07-01',
            difficulty=1
        )

        verdict_view = VerdictView(None, case, 'innocent', '测试理由', 
                                   {'evidence_points': 30, 'law_points': 20, 'witness_points': 15},
                                   70, player_role='defense')
        result = verdict_view._get_verdict_label()
        self.assertEqual(result, '无罪')

        verdict_view2 = VerdictView(None, case, 'major', '测试理由', 
                                    {'evidence_points': 10, 'law_points': 5, 'witness_points': 3},
                                    20, player_role='defense')
        result2 = verdict_view2._get_verdict_label()
        self.assertEqual(result2, '有罪')

    def test_prosecution_verdict_mapping(self):
        case = Case(
            case_id='case_002',
            title='测试案件2',
            description='测试描述2',
            defendant='王五',
            plaintiff='赵六',
            location='测试地点2',
            time='2026-07-02',
            difficulty=2
        )

        verdict_view = VerdictView(None, case, 'major', '测试理由', 
                                   {'evidence_points': 30, 'law_points': 25, 'witness_points': 18},
                                   75, player_role='prosecution')
        result = verdict_view._get_verdict_label()
        self.assertEqual(result, '胜诉')

        verdict_view2 = VerdictView(None, case, 'innocent', '测试理由', 
                                    {'evidence_points': 5, 'law_points': 3, 'witness_points': 2},
                                    30, player_role='prosecution')
        result2 = verdict_view2._get_verdict_label()
        self.assertEqual(result2, '败诉')


class TestCourtViewVerdictLogic(unittest.TestCase):
    def test_defense_success_verdict(self):
        mock_case = Mock()
        mock_case.case_id = 'case_001'
        mock_case.title = '测试案件'
        mock_case.defendant = '张三'
        mock_case.plaintiff = '李四'
        mock_case.difficulty = 1
        mock_case.verdict_guilt = None
        mock_case.verdict_reason = None
        mock_case.evidence_manager = Mock()
        mock_case.evidence_manager.get_collected_evidence = Mock(return_value=[])
        mock_case.evidence_manager.get_analyzed_evidence = Mock(return_value=[])
        mock_case.evidence_manager.get_key_evidence = Mock(return_value=[])
        mock_case.required_evidence = []
        mock_case.set_status = Mock()
        mock_case.witnesses = []
        mock_case.key_laws = []

        mock_case_manager = Mock()
        mock_case_manager.get_current_case = Mock(return_value=mock_case)

        mock_law_system = Mock()
        mock_law_system.get_law_by_id = Mock(return_value=None)

        court_view = CourtView(None, mock_case_manager, mock_law_system, player_role='defense')
        court_view.evidence_points = 30
        court_view.law_points = 20
        court_view.witness_points = 15
        court_view.judge_mood = 70
        court_view.current_case = mock_case
        court_view.player_role = 'defense'
        court_view.save_manager = Mock()
        court_view.save_manager.auto_save = Mock()
        court_view.character = Mock()
        court_view.character.name = '测试律师'
        court_view.character.add_experience = Mock()
        court_view.character.update_stat = Mock()
        court_view.character.to_dict = Mock(return_value={})
        court_view.achievement_manager = Mock()
        court_view.achievement_manager.unlock_achievement = Mock()
        court_view.achievement_manager.save_to_file = Mock()
        court_view._generate_success_reason = Mock(return_value='证据充分')
        court_view._generate_failure_reason = Mock(return_value='证据不足')
        court_view._judge_speak = Mock()
        court_view._add_log = Mock()
        court_view._update_mood = Mock()
        court_view.parent = Mock()
        court_view.parent.show_view = Mock()

        with patch('src.gui.court_view.DossierManager'):
            court_view.on_final_statement()

            self.assertEqual(mock_case.verdict_guilt, 'innocent')
            self.assertEqual(mock_case.verdict_reason, '证据充分')

    def test_prosecution_success_verdict(self):
        mock_case = Mock()
        mock_case.case_id = 'case_002'
        mock_case.title = '测试案件2'
        mock_case.defendant = '王五'
        mock_case.plaintiff = '赵六'
        mock_case.difficulty = 2
        mock_case.verdict_guilt = None
        mock_case.verdict_reason = None
        mock_case.evidence_manager = Mock()
        mock_case.evidence_manager.get_collected_evidence = Mock(return_value=[])
        mock_case.evidence_manager.get_analyzed_evidence = Mock(return_value=[])
        mock_case.evidence_manager.get_key_evidence = Mock(return_value=[])
        mock_case.required_evidence = []
        mock_case.set_status = Mock()
        mock_case.witnesses = []
        mock_case.key_laws = []

        mock_case_manager = Mock()
        mock_case_manager.get_current_case = Mock(return_value=mock_case)

        mock_law_system = Mock()
        mock_law_system.get_law_by_id = Mock(return_value=None)

        court_view = CourtView(None, mock_case_manager, mock_law_system, player_role='prosecution')
        court_view.evidence_points = 35
        court_view.law_points = 25
        court_view.witness_points = 18
        court_view.judge_mood = 80
        court_view.current_case = mock_case
        court_view.player_role = 'prosecution'
        court_view.save_manager = Mock()
        court_view.save_manager.auto_save = Mock()
        court_view.character = Mock()
        court_view.character.name = '测试律师'
        court_view.character.add_experience = Mock()
        court_view.character.update_stat = Mock()
        court_view.character.to_dict = Mock(return_value={})
        court_view.achievement_manager = Mock()
        court_view.achievement_manager.unlock_achievement = Mock()
        court_view.achievement_manager.save_to_file = Mock()
        court_view._generate_success_reason = Mock(return_value='证据充分')
        court_view._generate_failure_reason = Mock(return_value='证据不足')
        court_view._judge_speak = Mock()
        court_view._add_log = Mock()
        court_view._update_mood = Mock()
        court_view.parent = Mock()
        court_view.parent.show_view = Mock()

        with patch('src.gui.court_view.DossierManager'):
            court_view.on_final_statement()

            self.assertEqual(mock_case.verdict_guilt, 'major')


class TestShortcutsConfiguration(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.original_config_file = ConfigManager.CONFIG_FILE

    def tearDown(self):
        shutil.rmtree(self.temp_dir)
        ConfigManager.CONFIG_FILE = self.original_config_file

    def test_default_shortcuts_loaded(self):
        ConfigManager.CONFIG_FILE = os.path.join(self.temp_dir, 'player_config.json')
        
        config_manager = ConfigManager()
        shortcuts = config_manager.get_shortcuts()
        
        for action, default_key in DEFAULT_SHORTCUTS.items():
            self.assertIn(action, shortcuts)
            self.assertEqual(shortcuts[action], default_key)

    def test_custom_shortcut_saved_and_loaded(self):
        config_manager = ConfigManager()
        
        config_manager.set_shortcut('collect_evidence', '<Control-x>')
        
        new_config = ConfigManager()
        shortcuts = new_config.get_shortcuts()
        
        self.assertEqual(shortcuts['collect_evidence'], '<Control-x>')
        self.assertEqual(shortcuts['analyze_evidence'], DEFAULT_SHORTCUTS['analyze_evidence'])

    def test_reset_shortcuts_restore_defaults(self):
        config_manager = ConfigManager()
        
        config_manager.set_shortcut('collect_evidence', '<Control-x>')
        config_manager.set_shortcut('back', '<Control-z>')
        
        config_manager.reset_shortcuts()
        
        new_config = ConfigManager()
        shortcuts = new_config.get_shortcuts()
        
        self.assertEqual(shortcuts['collect_evidence'], DEFAULT_SHORTCUTS['collect_evidence'])
        self.assertEqual(shortcuts['back'], DEFAULT_SHORTCUTS['back'])


class TestSaveManagerLoadGame(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        os.environ['SAVES_DIR'] = self.temp_dir
        self.save_manager = SaveManager()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_load_game_preserves_case_status(self):
        save = GameSave(
            save_id='test_save',
            player_name='test_player',
            current_case_id='case_001',
            case_status='completed',
            evidence_collected=['ev_001'],
            evidence_analyzed=['ev_001'],
            witness_trust={'张三': 100},
            dialogue_history=[],
            game_time=120,
            case_progress={'case_001': {'status': 'completed', 'verdict': 'innocent'}}
        )
        
        self.save_manager.saves['test_save'] = save
        self.save_manager._save_to_file(save)

        loaded_save = self.save_manager.load_game('test_save')
        
        self.assertEqual(loaded_save.case_status, 'completed')
        self.assertEqual(loaded_save.case_progress['case_001']['status'], 'completed')
        self.assertEqual(loaded_save.case_progress['case_001']['verdict'], 'innocent')


if __name__ == '__main__':
    unittest.main()