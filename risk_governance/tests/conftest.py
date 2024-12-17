import pytest
import networkx as nx
from .test_helpers import TestDataGenerator

@pytest.fixture(scope='session')
def test_networks():
    """Fixture providing test networks with different characteristics"""
    return TestDataGenerator.get_test_cases()

@pytest.fixture(scope='session')
def test_network_small():
    """Small test network for basic functionality testing"""
    return TestDataGenerator.generate_test_network(num_nodes=5, risk_level='medium')

@pytest.fixture(scope='session')
def test_network_large():
    """Large test network for performance testing"""
    return TestDataGenerator.generate_test_network(num_nodes=100, risk_level='medium')

@pytest.fixture(scope='session')
def test_network_high_risk():
    """High-risk test network with many suspicious patterns"""
    return TestDataGenerator.generate_test_network(num_nodes=20, risk_level='high')