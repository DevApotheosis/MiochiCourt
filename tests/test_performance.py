import unittest
import time
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.law_system import LawSystem, Law
from core.evidence import EvidenceManager, Evidence

try:
    import fast_search
    HAS_FAST_SEARCH = True
    print('✅ C扩展模块 fast_search 已加载')
except ImportError:
    HAS_FAST_SEARCH = False
    print('❌ C扩展模块 fast_search 未加载，使用纯Python实现')


class TestPerformance(unittest.TestCase):
    def setUp(self):
        self.law_system = LawSystem()
        self.evidence_manager = EvidenceManager()
        
        for i in range(1000):
            law = Law(
                law_id=f'law_{i}',
                title=f'法律条文第{i}条',
                content=f'这是第{i}条法律条文的详细内容，包含很多文字来测试搜索性能。',
                category=f'类别{i % 10}',
                severity='中'
            )
            self.law_system.add_law(law)
        
        for i in range(1000):
            evidence = Evidence(
                evidence_id=f'ev_{i}',
                name=f'证据{i}',
                evidence_type='physical',
                description=f'这是证据{i}的描述',
                location=f'地点{i % 10}'
            )
            self.evidence_manager.add_evidence(evidence)
        
        if HAS_FAST_SEARCH:
            fast_search.clear_laws()
            fast_search.clear_evidence()
            for i in range(1000):
                fast_search.add_law(
                    f'law_{i}',
                    f'法律条文第{i}条',
                    f'这是第{i}条法律条文的详细内容，包含很多文字来测试搜索性能。',
                    f'类别{i % 10}'
                )
                fast_search.add_evidence(
                    f'ev_{i}',
                    f'证据{i}',
                    'physical',
                    f'这是证据{i}的描述',
                    f'地点{i % 10}'
                )
    
    def test_law_search_performance_python(self):
        start = time.time()
        for _ in range(100):
            results = self.law_system.search_laws('法律')
        end = time.time()
        elapsed = end - start
        print(f'[Python] 法律搜索100次耗时: {elapsed:.4f}秒')
        self.assertTrue(elapsed < 5.0, f'法律搜索性能不佳，耗时{elapsed:.4f}秒')
    
    def test_law_search_performance_c(self):
        if not HAS_FAST_SEARCH:
            self.skipTest('C扩展未加载')
        
        start = time.time()
        for _ in range(100):
            results = fast_search.search_laws('法律')
        end = time.time()
        elapsed = end - start
        print(f'[C扩展] 法律搜索100次耗时: {elapsed:.4f}秒')
        self.assertTrue(elapsed < 5.0, f'C扩展法律搜索性能不佳，耗时{elapsed:.4f}秒')
    
    def test_evidence_lookup_performance_python(self):
        start = time.time()
        for i in range(1000):
            evidence = self.evidence_manager.get_evidence_by_id(f'ev_{i}')
        end = time.time()
        elapsed = end - start
        print(f'[Python] 证据查找1000次耗时: {elapsed:.4f}秒')
        self.assertTrue(elapsed < 1.0, f'证据查找性能不佳，耗时{elapsed:.4f}秒')
    
    def test_evidence_lookup_performance_c(self):
        if not HAS_FAST_SEARCH:
            self.skipTest('C扩展未加载')
        
        start = time.time()
        for i in range(1000):
            evidence = fast_search.get_evidence_by_id(f'ev_{i}')
        end = time.time()
        elapsed = end - start
        print(f'[C扩展] 证据查找1000次耗时: {elapsed:.4f}秒')
        self.assertTrue(elapsed < 1.0, f'C扩展证据查找性能不佳，耗时{elapsed:.4f}秒')
    
    def test_evidence_collection_filter_performance_python(self):
        for i in range(500):
            self.evidence_manager.collect_evidence(f'ev_{i}')
        
        start = time.time()
        for _ in range(100):
            collected = self.evidence_manager.get_collected_evidence()
        end = time.time()
        elapsed = end - start
        print(f'[Python] 收集证据过滤100次耗时: {elapsed:.4f}秒')
        self.assertTrue(elapsed < 1.0, f'证据过滤性能不佳，耗时{elapsed:.4f}秒')
    
    def test_evidence_collection_filter_performance_c(self):
        if not HAS_FAST_SEARCH:
            self.skipTest('C扩展未加载')
        
        for i in range(500):
            fast_search.collect_evidence(f'ev_{i}')
        
        start = time.time()
        for _ in range(100):
            collected = fast_search.get_collected_evidence()
        end = time.time()
        elapsed = end - start
        print(f'[C扩展] 收集证据过滤100次耗时: {elapsed:.4f}秒')
        self.assertTrue(elapsed < 1.0, f'C扩展证据过滤性能不佳，耗时{elapsed:.4f}秒')


if __name__ == '__main__':
    unittest.main()