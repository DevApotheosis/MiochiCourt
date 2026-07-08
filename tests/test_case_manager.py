import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.case_manager import Case, CaseManager

class TestCase(unittest.TestCase):
    def test_case_creation(self):
        case = Case(
            case_id='case_001',
            title='Test Case',
            description='Test description',
            defendant='John Doe',
            plaintiff='Jane Doe',
            location='Court Room 1',
            time='2026-01-01',
            difficulty=2
        )
        self.assertEqual(case.case_id, 'case_001')
        self.assertEqual(case.title, 'Test Case')
        self.assertEqual(case.difficulty, 2)
        self.assertEqual(case.status, 'investigation')
    
    def test_set_status(self):
        case = Case(
            case_id='case_001',
            title='Test Case',
            description='Test description',
            defendant='John Doe',
            plaintiff='Jane Doe',
            location='Court Room 1',
            time='2026-01-01',
            difficulty=2
        )
        case.set_status('court')
        self.assertEqual(case.status, 'court')
        self.assertEqual(case.get_status_label(), '庭审中')
    
    def test_get_guilt_label(self):
        case = Case(
            case_id='case_001',
            title='Test Case',
            description='Test description',
            defendant='John Doe',
            plaintiff='Jane Doe',
            location='Court Room 1',
            time='2026-01-01',
            difficulty=2
        )
        case.verdict_guilt = 'innocent'
        self.assertEqual(case.get_guilt_label(), '无罪')

class TestCaseManager(unittest.TestCase):
    def setUp(self):
        self.manager = CaseManager()
    
    def test_add_case(self):
        case = Case(
            case_id='case_001',
            title='Test Case',
            description='Test description',
            defendant='John Doe',
            plaintiff='Jane Doe',
            location='Court Room 1',
            time='2026-01-01',
            difficulty=2
        )
        self.manager.add_case(case)
        self.assertEqual(len(self.manager.cases), 1)
    
    def test_get_case_by_id(self):
        case = Case(
            case_id='case_001',
            title='Test Case',
            description='Test description',
            defendant='John Doe',
            plaintiff='Jane Doe',
            location='Court Room 1',
            time='2026-01-01',
            difficulty=2
        )
        self.manager.add_case(case)
        found = self.manager.get_case_by_id('case_001')
        self.assertEqual(found.title, 'Test Case')
    
    def test_set_current_case(self):
        case = Case(
            case_id='case_001',
            title='Test Case',
            description='Test description',
            defendant='John Doe',
            plaintiff='Jane Doe',
            location='Court Room 1',
            time='2026-01-01',
            difficulty=2
        )
        self.manager.add_case(case)
        self.manager.set_current_case('case_001')
        self.assertEqual(self.manager.get_current_case().title, 'Test Case')

if __name__ == '__main__':
    unittest.main()