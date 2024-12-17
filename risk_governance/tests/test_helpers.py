import networkx as nx
from datetime import datetime, timedelta
import random

class TestDataGenerator:
    @staticmethod
    def generate_test_network(num_nodes=10, risk_level='medium'):
        """Generate a test network with specified characteristics
        
        Args:
            num_nodes (int): Number of nodes in the network
            risk_level (str): 'low', 'medium', or 'high' - affects pattern frequency
        
        Returns:
            nx.Graph: Graph with test data
        """
        G = nx.Graph()
        
        # Risk level parameters
        risk_params = {
            'low': {
                'shared_director_prob': 0.1,
                'shared_address_prob': 0.1,
                'ownership_prob': 0.05,
                'suspicious_pattern_prob': 0.1
            },
            'medium': {
                'shared_director_prob': 0.3,
                'shared_address_prob': 0.3,
                'ownership_prob': 0.15,
                'suspicious_pattern_prob': 0.3
            },
            'high': {
                'shared_director_prob': 0.5,
                'shared_address_prob': 0.5,
                'ownership_prob': 0.25,
                'suspicious_pattern_prob': 0.5
            }
        }[risk_level]
        
        # Generate nodes
        for i in range(num_nodes):
            node_name = f'Company{i}'
            G.add_node(node_name, **TestDataGenerator._generate_company_data(i))
            
        # Generate edges based on risk parameters
        for i in range(num_nodes):
            for j in range(i+1, num_nodes):
                if random.random() < risk_params['shared_director_prob']:
                    G.add_edge(f'Company{i}', f'Company{j}',
                              relationship_type='shared_director',
                              strength=random.uniform(0.6, 0.9))
                    
                if random.random() < risk_params['shared_address_prob']:
                    G.add_edge(f'Company{i}', f'Company{j}',
                              relationship_type='shared_address',
                              strength=random.uniform(0.6, 0.9))
                    
                if random.random() < risk_params['ownership_prob']:
                    G.add_edge(f'Company{i}', f'Company{j}',
                              relationship_type='ownership',
                              strength=random.uniform(0.7, 1.0))
                    
        # Add suspicious patterns based on risk level
        if random.random() < risk_params['suspicious_pattern_prob']:
            TestDataGenerator._add_circular_ownership(G)
        if random.random() < risk_params['suspicious_pattern_prob']:
            TestDataGenerator._add_hub_spoke_pattern(G)
            
        return G
    
    @staticmethod
    def _generate_company_data(index):
        """Generate realistic company data"""
        return {
            'incorporation_date': (datetime.now() - 
                                  timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d'),
            'directors': [{
                'name': f'Director{random.randint(1, 20)}',
                'appointment_date': (datetime.now() - 
                                   timedelta(days=random.randint(0, 180))).strftime('%Y-%m-%d'),
                'nationality': random.choice(['British', 'American', 'French', 'German'])
            } for _ in range(random.randint(1, 3))],
            'addresses': [f'{random.randint(1, 999)} {random.choice(["Business St", "Commerce Rd", "Industry Ave"])}'],
            'sic_codes': [str(random.randint(10000, 99999)) for _ in range(random.randint(1, 3))],
            'company_type': random.choice(['Private Limited Company', 'LLP', 'Public Limited Company'])
        }
    
    @staticmethod
    def _add_circular_ownership(G):
        """Add a circular ownership pattern to the graph"""
        nodes = list(G.nodes())
        if len(nodes) >= 3:
            cycle = random.sample(nodes, 3)
            for i in range(len(cycle)):
                G.add_edge(cycle[i], cycle[(i+1)%3],
                          relationship_type='ownership',
                          strength=random.uniform(0.8, 1.0))
    
    @staticmethod
    def _add_hub_spoke_pattern(G):
        """Add a hub and spoke pattern to the graph"""
        nodes = list(G.nodes())
        if len(nodes) >= 4:
            hub = random.choice(nodes)
            spokes = random.sample([n for n in nodes if n != hub], 3)
            for spoke in spokes:
                G.add_edge(hub, spoke,
                          relationship_type='control',
                          strength=random.uniform(0.8, 1.0))

# Example usage in tests:
def get_test_cases():
    """Generate a set of test cases with different characteristics"""
    return {
        'low_risk': TestDataGenerator.generate_test_network(num_nodes=10, risk_level='low'),
        'medium_risk': TestDataGenerator.generate_test_network(num_nodes=15, risk_level='medium'),
        'high_risk': TestDataGenerator.generate_test_network(num_nodes=20, risk_level='high'),
        'large_network': TestDataGenerator.generate_test_network(num_nodes=50, risk_level='medium')
    }