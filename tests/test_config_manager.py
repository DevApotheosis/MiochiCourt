import sys
import os
import unittest
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.config_manager import ConfigManager


class TestConfigManager(unittest.TestCase):
    def setUp(self):
        self.config_manager = ConfigManager()
        self.config_manager.clear_config()
        self.config_manager = ConfigManager()
        self.test_config = {
            'player_name': 'TestPlayer',
            'player_role': 'defense'
        }
    
    def test_get_player_name_default(self):
        config_manager = ConfigManager()
        result = config_manager.get_player_name()
        self.assertIsInstance(result, str)
    
    def test_set_and_get_player_name(self):
        self.config_manager.set_player_name('TestLawyer')
        result = self.config_manager.get_player_name()
        self.assertEqual(result, 'TestLawyer')
    
    def test_get_player_role_default(self):
        result = self.config_manager.get_player_role()
        self.assertEqual(result, 'defense')
    
    def test_set_player_role_defense(self):
        self.config_manager.set_player_role('defense')
        result = self.config_manager.get_player_role()
        self.assertEqual(result, 'defense')
    
    def test_set_player_role_prosecution(self):
        self.config_manager.set_player_role('prosecution')
        result = self.config_manager.get_player_role()
        self.assertEqual(result, 'prosecution')
    
    def test_set_player_role_invalid(self):
        self.config_manager.set_player_role('invalid')
        result = self.config_manager.get_player_role()
        self.assertNotEqual(result, 'invalid')
    
    def test_get_all_config(self):
        config = self.config_manager.get_all_config()
        self.assertIsInstance(config, dict)
    
    def test_config_persistence(self):
        test_name = 'PersistentPlayer'
        self.config_manager.set_player_name(test_name)
        new_manager = ConfigManager()
        result = new_manager.get_player_name()
        self.assertEqual(result, test_name)


if __name__ == '__main__':
    unittest.main()
