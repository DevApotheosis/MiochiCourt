import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.evidence import Evidence, EvidenceManager

class TestEvidence(unittest.TestCase):
    def test_evidence_creation(self):
        evidence = Evidence('ev_001', 'Test Evidence', 'document', 'Test description', 'Test location')
        self.assertEqual(evidence.evidence_id, 'ev_001')
        self.assertEqual(evidence.name, 'Test Evidence')
        self.assertEqual(evidence.evidence_type, 'document')
        self.assertEqual(evidence.description, 'Test description')
        self.assertEqual(evidence.location, 'Test location')
        self.assertFalse(evidence.collected)
        self.assertFalse(evidence.analyzed)
    
    def test_collect_evidence(self):
        evidence = Evidence('ev_001', 'Test Evidence', 'document', 'Test description', 'Test location')
        evidence.collect()
        self.assertTrue(evidence.collected)
    
    def test_analyze_evidence(self):
        evidence = Evidence('ev_001', 'Test Evidence', 'document', 'Test description', 'Test location')
        evidence.collect()
        analysis = 'Test analysis result'
        evidence.analyze(analysis)
        self.assertTrue(evidence.analyzed)
        self.assertEqual(evidence.analysis_result, analysis)
    
    def test_get_type_label(self):
        evidence = Evidence('ev_001', 'Test Evidence', 'document', 'Test description', 'Test location')
        self.assertEqual(evidence.get_type_label(), '文档证据')

class TestEvidenceManager(unittest.TestCase):
    def setUp(self):
        self.manager = EvidenceManager()
        self.evidence1 = Evidence('ev_001', 'Evidence 1', 'document', 'Desc 1', 'Loc 1', is_key=True)
        self.evidence2 = Evidence('ev_002', 'Evidence 2', 'physical', 'Desc 2', 'Loc 2')
        self.manager.add_evidence(self.evidence1)
        self.manager.add_evidence(self.evidence2)
    
    def test_add_evidence(self):
        self.assertEqual(len(self.manager.evidence_list), 2)
    
    def test_get_evidence_by_id(self):
        found = self.manager.get_evidence_by_id('ev_001')
        self.assertEqual(found.name, 'Evidence 1')
    
    def test_collect_evidence(self):
        self.manager.collect_evidence('ev_001')
        self.assertTrue(self.evidence1.collected)
    
    def test_get_collected_evidence(self):
        self.manager.collect_evidence('ev_001')
        collected = self.manager.get_collected_evidence()
        self.assertEqual(len(collected), 1)
        self.assertEqual(collected[0].name, 'Evidence 1')
    
    def test_get_key_evidence(self):
        self.manager.collect_evidence('ev_001')
        key = self.manager.get_key_evidence()
        self.assertEqual(len(key), 1)
        self.assertEqual(key[0].name, 'Evidence 1')

if __name__ == '__main__':
    unittest.main()