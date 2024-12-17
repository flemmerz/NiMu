import unittest
import networkx as nx
from datetime import datetime, timedelta
from ..detection.network_analyzer import NetworkAnalyzer, NetworkMetrics

class TestNetworkAnalyzer(unittest.TestCase):
    def setUp(self):
        # Create test graph with known patterns
        self.G = nx.Graph()
        
        # Add nodes with attributes
        self.G.add_node('A', 
            incorporation_date='2023-01-01',
            directors=[{'name': 'John Smith', 'appointment_date': '2023-01-01'}],
            addresses=['123 Test St']
        )
        self.G.add_node('B',
            incorporation_date='2023-01-01',
            directors=[{'name': 'John Smith', 'appointment_date': '2023-01-01'}],
            addresses=['123 Test St']
        )
        self.G.add_node('C',
            incorporation_date='2023-01-02',
            directors=[{'name': 'Jane Doe', 'appointment_date': '2023-01-02'}],
            addresses=['456 Other St']
        )
        self.G.add_node('D',
            incorporation_date='2023-01-02',
            directors=[{'name': 'Jane Doe', 'appointment_date': '2023-01-02'}],
            addresses=['789 Another St']
        )
        
        # Add edges with relationship attributes
        self.G.add_edge('A', 'B', relationship_type='shared_director', strength=0.8)
        self.G.add_edge('B', 'C', relationship_type='shared_address', strength=0.6)
        self.G.add_edge('C', 'D', relationship_type='shared_director', strength=0.7)
        
        # Initialize analyzer
        self.analyzer = NetworkAnalyzer(self.G)

    def test_network_growth(self):
        """Test analysis of network growth patterns"""
        # Add rapidly growing component
        for i in range(5):
            node_name = f'New{i}'
            self.G.add_node(node_name, 
                incorporation_date='2023-02-01',
                directors=[{'name': f'Director{i}', 'appointment_date': '2023-02-01'}],
                addresses=[f'{i} New St']
            )
            if i > 0:
                self.G.add_edge(f'New{i}', f'New{i-1}', 
                               relationship_type='shared_director', 
                               strength=0.9)

        patterns = self.analyzer._analyze_network_growth()
        
        # Should detect rapid growth pattern
        rapid_growth_found = False
        for pattern in patterns:
            if pattern['type'] == 'rapid_growth':
                rapid_growth_found = True
                self.assertGreaterEqual(len(pattern['entities']), 5)
                
        self.assertTrue(rapid_growth_found)

    def test_hub_spoke_detection(self):
        """Test detection of hub and spoke patterns"""
        # Create hub and spoke pattern
        hub = 'Hub'
        self.G.add_node(hub,
            incorporation_date='2023-03-01',
            directors=[{'name': 'Hub Director', 'appointment_date': '2023-03-01'}],
            addresses=['Hub Street']
        )
        
        # Add spokes
        for i in range(5):
            spoke = f'Spoke{i}'
            self.G.add_node(spoke,
                incorporation_date='2023-03-01',
                directors=[{'name': f'Spoke Director {i}', 'appointment_date': '2023-03-01'}],
                addresses=[f'Spoke Street {i}']
            )
            self.G.add_edge(hub, spoke, relationship_type='control', strength=0.9)

        patterns = self.analyzer._identify_hub_spoke_patterns()
        
        self.assertIn(hub, patterns)
        self.assertEqual(len(patterns[hub]), 5)

    def test_isolated_subgroup_detection(self):
        """Test detection of isolated subgroups"""
        # Create isolated subgroup
        for i in range(3):
            node = f'Isolated{i}'
            self.G.add_node(node,
                incorporation_date='2023-04-01',
                directors=[{'name': f'Isolated Director {i}', 'appointment_date': '2023-04-01'}],
                addresses=[f'Isolated Street {i}']
            )
            if i > 0:
                self.G.add_edge(f'Isolated{i}', f'Isolated{i-1}', 
                               relationship_type='shared_director', 
                               strength=0.7)

        isolated_groups = self.analyzer._identify_isolated_subgroups()
        
        isolated_found = False
        for group in isolated_groups:
            if all('Isolated' in node for node in group):
                isolated_found = True
                self.assertEqual(len(group), 3)
                
        self.assertTrue(isolated_found)

    def test_shared_attribute_analysis(self):
        """Test analysis of shared attributes between entities"""
        entities = ['A', 'B']
        shared_attrs = self.analyzer._check_shared_attributes(entities)
        
        self.assertIn('directors', shared_attrs)
        self.assertIn('addresses', shared_attrs)
        self.assertEqual(shared_attrs['directors'][0], 'John Smith')
        self.assertEqual(shared_attrs['addresses'][0], '123 Test St')

    def test_cycle_risk_calculation(self):
        """Test calculation of risk scores for cycles"""
        # Create a high-risk cycle
        cycle_nodes = ['Cycle1', 'Cycle2', 'Cycle3']
        for node in cycle_nodes:
            self.G.add_node(node,
                incorporation_date='2023-05-01',
                directors=[{'name': 'Cycle Director', 'appointment_date': '2023-05-01'}],
                addresses=['Cycle Street']
            )
        
        for i in range(len(cycle_nodes)):
            self.G.add_edge(cycle_nodes[i], cycle_nodes[(i+1)%3], 
                           relationship_type='ownership', 
                           strength=0.9)

        cycle_risk = self.analyzer._calculate_cycle_risk(cycle_nodes)
        
        self.assertGreater(cycle_risk, self.analyzer.risk_threshold)

    def test_network_metrics_integration(self):
        """Test integration of all network metrics"""
        metrics = self.analyzer.calculate_network_metrics()
        
        # Check all components are present and properly calculated
        self.assertIsInstance(metrics, NetworkMetrics)
        self.assertTrue(metrics.centrality_scores)
        self.assertTrue(metrics.community_membership)
        self.assertTrue(metrics.risk_patterns)
        self.assertTrue(metrics.temporal_patterns)
        self.assertTrue(metrics.anomaly_scores)

    def test_risk_threshold_sensitivity(self):
        """Test sensitivity of risk detection to threshold changes"""
        # Test with different risk thresholds
        high_threshold = self.analyzer.get_high_risk_entities(risk_threshold=0.9)
        medium_threshold = self.analyzer.get_high_risk_entities(risk_threshold=0.7)
        low_threshold = self.analyzer.get_high_risk_entities(risk_threshold=0.5)
        
        # Should detect more entities with lower threshold
        self.assertGreaterEqual(len(low_threshold), len(medium_threshold))
        self.assertGreaterEqual(len(medium_threshold), len(high_threshold))

if __name__ == '__main__':
    unittest.main()