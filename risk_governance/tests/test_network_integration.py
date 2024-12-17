import unittest
import networkx as nx
from datetime import datetime, timedelta
from .test_helpers import TestDataGenerator
from ..detection.network_analyzer import NetworkAnalyzer
from ..detection.shell_company_detector import ShellCompanyDetector
from ..detection.uk_shell_detector import UKShellDetector

class TestNetworkIntegration(unittest.TestCase):
    def setUp(self):
        """Initialize test cases with different network characteristics"""
        self.test_cases = TestDataGenerator.get_test_cases()
        self.analyzers = {}
        for case_name, graph in self.test_cases.items():
            self.analyzers[case_name] = NetworkAnalyzer(graph)

    def test_shell_company_integration(self):
        """Test integration between network analysis and shell company detection"""
        # Set up shell company detector
        for case_name, graph in self.test_cases.items():
            shell_detector = ShellCompanyDetector()
            network_analyzer = self.analyzers[case_name]
            
            # Get network metrics
            network_metrics = network_analyzer.calculate_network_metrics()
            
            # Get shell company patterns
            shell_patterns = shell_detector.detect_shell_patterns()
            
            # Verify correlation between high-risk entities
            high_risk_network = set(
                e['entity'] for e in network_analyzer.get_high_risk_entities()
            )
            shell_company_risks = set(
                pattern['entities'][0] for pattern in shell_patterns
                if pattern['risk_score'] > 0.7
            )
            
            # There should be some overlap between high-risk entities
            overlap = high_risk_network.intersection(shell_company_risks)
            self.assertGreater(len(overlap), 0)

    def test_uk_specific_integration(self):
        """Test integration with UK-specific detection rules"""
        for case_name, graph in self.test_cases.items():
            network_analyzer = self.analyzers[case_name]
            uk_detector = UKShellDetector(ShellCompanyDetector())
            
            # Get network analysis results
            network_metrics = network_analyzer.calculate_network_metrics()
            
            # Get UK-specific analysis
            uk_analysis = uk_detector.analyze_uk_specific_patterns()
            
            # Check correlation between network centrality and Companies House flags
            for node, centrality in network_metrics.centrality_scores.items():
                if centrality['betweenness'] > 0.7:
                    # High centrality nodes should have more scrutiny in UK analysis
                    self.assertTrue(
                        any(flag['company'] == node 
                            for flag in uk_analysis['companies_house_flags'])
                    )

    def test_temporal_correlation(self):
        """Test correlation between temporal patterns across different analyses"""
        for case_name, graph in self.test_cases.items():
            network_analyzer = self.analyzers[case_name]
            shell_detector = ShellCompanyDetector()
            
            # Get temporal patterns from network analysis
            network_temporal = network_analyzer._analyze_temporal_patterns()
            
            # Get shell company temporal patterns
            shell_temporal = shell_detector._analyze_formation_patterns()
            
            # Compare temporal pattern detection
            network_dates = set(p['date'] for p in network_temporal)
            shell_dates = set(p['date'] for p in shell_temporal)
            
            # Dates of interest should overlap
            self.assertTrue(network_dates.intersection(shell_dates))

    def test_risk_score_consistency(self):
        """Test consistency of risk scoring across different components"""
        for case_name, graph in self.test_cases.items():
            network_analyzer = self.analyzers[case_name]
            shell_detector = ShellCompanyDetector()
            uk_detector = UKShellDetector(shell_detector)
            
            # Get risk scores from each component
            network_risks = network_analyzer.get_high_risk_entities()
            shell_risks = shell_detector.detect_shell_patterns()
            uk_risks = uk_detector.analyze_uk_specific_patterns()
            
            # Create combined risk assessment
            combined_risks = self._combine_risk_scores(
                network_risks, shell_risks, uk_risks
            )
            
            # Verify risk score consistency
            self._verify_risk_consistency(combined_risks)

    def test_pattern_detection_consistency(self):
        """Test consistency of pattern detection across components"""
        for case_name, graph in self.test_cases.items():
            network_analyzer = self.analyzers[case_name]
            
            # Get patterns from different detection methods
            network_patterns = network_analyzer._identify_risk_patterns()
            structural_patterns = network_analyzer._detect_suspicious_cycles()
            temporal_patterns = network_analyzer._analyze_temporal_patterns()
            
            # Verify pattern consistency
            self._verify_pattern_consistency(
                network_patterns,
                structural_patterns,
                temporal_patterns
            )

    def _combine_risk_scores(self, network_risks, shell_risks, uk_risks):
        """Combine risk scores from different components"""
        combined = {}
        
        # Combine network risks
        for risk in network_risks:
            entity = risk['entity']
            if entity not in combined:
                combined[entity] = {'risk_scores': []}
            combined[entity]['risk_scores'].append({
                'source': 'network',
                'score': risk['anomaly_score']
            })
        
        # Add shell company risks
        for risk in shell_risks:
            for entity in risk['entities']:
                if entity not in combined:
                    combined[entity] = {'risk_scores': []}
                combined[entity]['risk_scores'].append({
                    'source': 'shell',
                    'score': risk['risk_score']
                })
        
        # Add UK-specific risks
        if 'uk_risk_score' in uk_risks:
            for entity in combined:
                combined[entity]['risk_scores'].append({
                    'source': 'uk',
                    'score': uk_risks['uk_risk_score']
                })
        
        return combined

    def _verify_risk_consistency(self, combined_risks):
        """Verify that risk scores are consistent across components"""
        for entity, risks in combined_risks.items():
            scores = [r['score'] for r in risks['risk_scores']]
            
            # Check score variance
            if len(scores) > 1:
                variance = np.var(scores)
                # Scores should not vary too widely for the same entity
                self.assertLess(variance, 0.25)

    def _verify_pattern_consistency(self, network_patterns, structural_patterns, 
                                  temporal_patterns):
        """Verify that pattern detection is consistent across methods"""
        # Extract entities involved in each type of pattern
        network_entities = set()
        for pattern in network_patterns:
            if 'entities' in pattern:
                network_entities.update(pattern['entities'])
            
        structural_entities = set()
        for cycle in structural_patterns:
            structural_entities.update(cycle)
            
        temporal_entities = set()
        for pattern in temporal_patterns:
            if 'entities' in pattern:
                temporal_entities.update(pattern['entities'])
        
        # Check for reasonable overlap between different pattern types
        total_entities = network_entities.union(structural_entities).union(temporal_entities)
        overlap_count = len(network_entities.intersection(structural_entities).intersection(temporal_entities))
        
        # At least some entities should be detected by multiple methods
        self.assertGreater(overlap_count / len(total_entities), 0.1)

if __name__ == '__main__':
    unittest.main()