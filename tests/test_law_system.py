import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.law_system import Law, LawSystem

class TestLaw(unittest.TestCase):
    def test_law_creation(self):
        law = Law('law_001', 'Test Law', 'Content', '刑法', '严重')
        self.assertEqual(law.law_id, 'law_001')
        self.assertEqual(law.title, 'Test Law')
        self.assertEqual(law.category, '刑法')
        self.assertEqual(law.severity, '严重')
    
    def test_law_with_related_articles(self):
        law = Law('law_001', 'Test Law', 'Content', '刑法', '严重', ['第1条', '第2条'])
        self.assertEqual(len(law.related_articles), 2)

class TestLawSystem(unittest.TestCase):
    def setUp(self):
        self.system = LawSystem()
        self.law1 = Law('law_001', 'Computer Crime Act', 'Content about computer crimes', '刑法', '严重')
        self.law2 = Law('law_002', 'Data Protection Act', 'Content about data protection', '行政法', '中等')
        self.system.add_law(self.law1)
        self.system.add_law(self.law2)
    
    def test_add_law(self):
        self.assertEqual(len(self.system.laws), 2)
    
    def test_get_law_by_id(self):
        found = self.system.get_law_by_id('law_001')
        self.assertEqual(found.title, 'Computer Crime Act')
    
    def test_get_laws_by_category(self):
        result = self.system.get_laws_by_category('刑法')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].title, 'Computer Crime Act')
    
    def test_search_laws(self):
        result = self.system.search_laws('computer')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].title, 'Computer Crime Act')
    
    def test_get_all_categories(self):
        categories = self.system.get_all_categories()
        self.assertIn('刑法', categories)
        self.assertIn('行政法', categories)

if __name__ == '__main__':
    unittest.main()