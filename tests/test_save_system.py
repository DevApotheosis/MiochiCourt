import unittest
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.save_system import GameSave, SaveManager


class TestGameSaveInit(unittest.TestCase):
    def test_init_with_all_parameters(self):
        save = GameSave(
            save_id='test_save',
            player_name='test_player',
            current_case_id='case_001',
            case_status='investigation',
            evidence_collected=['ev_001'],
            evidence_analyzed=['ev_002'],
            witness_trust={'张三': 50},
            dialogue_history=['对话1'],
            game_time=30
        )
        
        self.assertEqual(save.save_id, 'test_save')
        self.assertEqual(save.player_name, 'test_player')
        self.assertEqual(save.current_case_id, 'case_001')
        self.assertEqual(save.case_status, 'investigation')
        self.assertEqual(save.evidence_collected, ['ev_001'])
        self.assertEqual(save.evidence_analyzed, ['ev_002'])
        self.assertEqual(save.witness_trust, {'张三': 50})
        self.assertEqual(save.dialogue_history, ['对话1'])
        self.assertEqual(save.game_time, 30)

    def test_init_missing_required_parameters(self):
        with self.assertRaises(TypeError):
            GameSave(
                save_id='test_save',
                player_name='test_player',
                current_case_id='case_001',
                case_status='investigation'
            )

    def test_init_invalid_case_status(self):
        with self.assertRaises(ValueError):
            GameSave(
                save_id='test_save',
                player_name='test_player',
                current_case_id='case_001',
                case_status='invalid',
                evidence_collected=[],
                evidence_analyzed=[],
                witness_trust={},
                dialogue_history=[],
                game_time=0
            )

    def test_init_invalid_evidence_collected_type(self):
        with self.assertRaises(TypeError):
            GameSave(
                save_id='test_save',
                player_name='test_player',
                current_case_id='case_001',
                case_status='investigation',
                evidence_collected='invalid',
                evidence_analyzed=[],
                witness_trust={},
                dialogue_history=[],
                game_time=0
            )

    def test_init_invalid_witness_trust_type(self):
        with self.assertRaises(TypeError):
            GameSave(
                save_id='test_save',
                player_name='test_player',
                current_case_id='case_001',
                case_status='investigation',
                evidence_collected=[],
                evidence_analyzed=[],
                witness_trust='invalid',
                dialogue_history=[],
                game_time=0
            )


class TestSaveManagerAutoSave(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.original_saves_dir = os.environ.get('SAVES_DIR', '')
        os.environ['SAVES_DIR'] = self.temp_dir
        
        self.save_manager = SaveManager()
        SaveManager.AUTO_SAVE_ID = 'auto_save_test'

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
        if self.original_saves_dir:
            os.environ['SAVES_DIR'] = self.original_saves_dir

    def test_auto_save_first_time(self):
        result = self.save_manager.auto_save(
            player_name='test_player',
            current_case_id='case_001',
            case_status='investigation',
            evidence_collected=['ev_001'],
            evidence_analyzed=[],
            witness_trust={'张三': 50},
            dialogue_history=[],
            game_time=10
        )
        
        self.assertTrue(result)
        self.assertIn('auto_save_test', self.save_manager.saves)
        
        save = self.save_manager.saves['auto_save_test']
        self.assertEqual(save.player_name, 'test_player')
        self.assertEqual(save.current_case_id, 'case_001')
        self.assertEqual(save.evidence_collected, ['ev_001'])
        self.assertEqual(save.witness_trust, {'张三': 50})

    def test_auto_save_overwrites_existing(self):
        self.save_manager.auto_save(
            player_name='player1',
            current_case_id='case_001',
            case_status='investigation',
            evidence_collected=['ev_001'],
            evidence_analyzed=[],
            witness_trust={},
            dialogue_history=[],
            game_time=10
        )
        
        self.save_manager.auto_save(
            player_name='player2',
            current_case_id='case_002',
            case_status='completed',
            evidence_collected=['ev_001', 'ev_002'],
            evidence_analyzed=['ev_001'],
            witness_trust={'李四': 80},
            dialogue_history=['对话记录'],
            game_time=20
        )
        
        save = self.save_manager.saves['auto_save_test']
        self.assertEqual(save.player_name, 'player2')
        self.assertEqual(save.current_case_id, 'case_002')
        self.assertEqual(save.case_status, 'completed')
        self.assertEqual(len(save.evidence_collected), 2)


class TestSaveManagerCreateSave(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.save_manager = SaveManager()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_create_save(self):
        save = self.save_manager.create_save(
            player_name='test_player',
            current_case_id='case_001',
            case_status='investigation'
        )
        
        self.assertIsNotNone(save)
        self.assertEqual(save.player_name, 'test_player')
        self.assertEqual(save.current_case_id, 'case_001')
        self.assertEqual(save.evidence_collected, [])
        self.assertEqual(save.witness_trust, {})


class TestGameSaveToFromDict(unittest.TestCase):
    def test_to_dict(self):
        save = GameSave(
            save_id='test_save',
            player_name='test_player',
            current_case_id='case_001',
            case_status='completed',
            evidence_collected=['ev_001'],
            evidence_analyzed=['ev_001'],
            witness_trust={'张三': 100},
            dialogue_history=['对话内容'],
            game_time=60
        )
        
        data = save.to_dict()
        
        self.assertEqual(data['save_id'], 'test_save')
        self.assertEqual(data['player_name'], 'test_player')
        self.assertEqual(data['case_status'], 'completed')
        self.assertIn('created_at', data)
        self.assertIn('updated_at', data)

    def test_from_dict(self):
        data = {
            'save_id': 'test_save',
            'player_name': 'test_player',
            'current_case_id': 'case_001',
            'case_status': 'completed',
            'evidence_collected': ['ev_001'],
            'evidence_analyzed': ['ev_001'],
            'witness_trust': {'张三': 100},
            'dialogue_history': ['对话内容'],
            'game_time': 60,
            'player_data': {'level': 5},
            'case_progress': {'case_001': {'status': 'completed'}}
        }
        
        save = GameSave.from_dict(data)
        
        self.assertEqual(save.save_id, 'test_save')
        self.assertEqual(save.player_name, 'test_player')
        self.assertEqual(save.case_status, 'completed')
        self.assertEqual(save.player_data, {'level': 5})


if __name__ == '__main__':
    unittest.main()
