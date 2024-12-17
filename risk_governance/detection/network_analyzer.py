import networkx as nx
import numpy as np
from typing import Dict, List, Set, Tuple
from collections import defaultdict
from datetime import datetime
from dataclasses import dataclass
import community  # python-louvain package
from sklearn.preprocessing import StandardScaler
import pandas as pd

@dataclass
class NetworkMetrics:
    """Container for network analysis metrics"""
    centrality_scores: Dict[str, float]
    community_membership: Dict[str, int]
    risk_patterns: List[Dict]
    temporal_patterns: List[Dict]
    suspicious_cycles: List[List[str]]
    anomaly_scores: Dict[str, float]

class NetworkAnalyzer:
    def __init__(self, entity_graph: nx.Graph):
        self.graph = entity_graph
        self.risk_threshold = 0.75
        self.temporal_window_days = 90
        
    def calculate_network_metrics(self) -> NetworkMetrics:
        """Calculate comprehensive network metrics"""
        return NetworkMetrics(
            centrality_scores=self._calculate_centrality_metrics(),
            community_membership=self._detect_communities(),
            risk_patterns=self._identify_risk_patterns(),
            temporal_patterns=self._analyze_temporal_patterns(),
            suspicious_cycles=self._detect_suspicious_cycles(),
            anomaly_scores=self._calculate_anomaly_scores()
        )
    
    def _calculate_centrality_metrics(self) -> Dict[str, Dict[str, float]]:
        """Calculate multiple centrality measures for each node"""
        centrality_metrics = {}
        
        for node in self.graph.nodes():
            metrics = {
                # Basic centrality measures
                'degree': nx.degree_centrality(self.graph)[node],
                'betweenness': nx.betweenness_centrality(self.graph)[node],
                'eigenvector': nx.eigenvector_centrality(self.graph, max_iter=1000)[node],
                'pagerank': nx.pagerank(self.graph)[node],
                
                # Advanced centrality measures
                'load': nx.load_centrality(self.graph)[node],
                'katz': nx.katz_centrality(self.graph)[node],
                
                # Local clustering
                'clustering': nx.clustering(self.graph, node),
                
                # Reach centrality (custom implementation)
                'reach': self._calculate_reach_centrality(node)
            }
            
            centrality_metrics[node] = metrics
            
        return centrality_metrics
    
    def _detect_communities(self) -> Dict[str, int]:
        """Detect communities using multiple algorithms and ensemble the results"""
        # Louvain method
        louvain_communities = community.best_partition(self.graph)
        
        # Label propagation
        label_prop_communities = {node: comm for node, comm in 
                                enumerate(nx.label_propagation_communities(self.graph))}
        
        # Girvan-Newman (for smaller graphs)
        if len(self.graph) < 1000:
            girvan_newman = list(nx.community.girvan_newman(self.graph))
            gn_communities = {node: comm for comm, nodes in enumerate(girvan_newman[0]) 
                            for node in nodes}
        else:
            gn_communities = louvain_communities
        
        # Ensemble the results
        ensemble_communities = {}
        for node in self.graph.nodes():
            communities = [
                louvain_communities.get(node, 0),
                label_prop_communities.get(node, 0),
                gn_communities.get(node, 0)
            ]
            # Use most common community assignment
            ensemble_communities[node] = max(set(communities), key=communities.count)
            
        return ensemble_communities

    def _identify_risk_patterns(self) -> List[Dict]:
        """Identify suspicious network patterns"""
        risk_patterns = []
        
        # Pattern 1: Circular ownership structures
        circular_structures = self._find_circular_ownership()
        if circular_structures:
            risk_patterns.extend([{
                'type': 'circular_ownership',
                'entities': struct,
                'risk_level': 'high'
            } for struct in circular_structures])
        
        # Pattern 2: Hub and spoke structures
        hub_spoke = self._identify_hub_spoke_patterns()
        if hub_spoke:
            risk_patterns.extend([{
                'type': 'hub_spoke',
                'hub': hub,
                'spokes': spokes,
                'risk_level': 'medium'
            } for hub, spokes in hub_spoke.items()])
        
        # Pattern 3: Rapid network growth
        growth_patterns = self._analyze_network_growth()
        if growth_patterns:
            risk_patterns.extend(growth_patterns)
        
        # Pattern 4: Isolated subgroups
        isolated_groups = self._identify_isolated_subgroups()
        if isolated_groups:
            risk_patterns.extend([{
                'type': 'isolated_subgroup',
                'entities': group,
                'risk_level': 'medium'
            } for group in isolated_groups])
        
        return risk_patterns

    def _analyze_temporal_patterns(self) -> List[Dict]:
        """Analyze temporal patterns in entity relationships"""
        temporal_patterns = []
        
        # Group entities by incorporation date
        date_groups = defaultdict(list)
        for node in self.graph.nodes():
            inc_date = self.graph.nodes[node].get('incorporation_date')
            if inc_date:
                date_groups[inc_date].append(node)
        
        # Look for suspicious temporal patterns
        for date, entities in date_groups.items():
            if len(entities) >= 3:  # Three or more entities incorporated on same day
                # Check if entities share directors or addresses
                shared_attributes = self._check_shared_attributes(entities)
                if shared_attributes:
                    temporal_patterns.append({
                        'type': 'bulk_incorporation',
                        'date': date,
                        'entities': entities,
                        'shared_attributes': shared_attributes,
                        'risk_level': 'high'
                    })
                    
        return temporal_patterns

    def _detect_suspicious_cycles(self) -> List[List[str]]:
        """Detect suspicious cycles in the network"""
        suspicious_cycles = []
        
        # Find all cycles in the graph
        simple_cycles = list(nx.simple_cycles(self.graph))
        
        for cycle in simple_cycles:
            if len(cycle) >= 3:  # Consider cycles of length 3 or more
                # Calculate risk metrics for the cycle
                cycle_risk = self._calculate_cycle_risk(cycle)
                
                if cycle_risk > self.risk_threshold:
                    suspicious_cycles.append(cycle)
        
        return suspicious_cycles

    def _calculate_anomaly_scores(self) -> Dict[str, float]:
        """Calculate anomaly scores for each entity based on network features"""
        features = []
        nodes = list(self.graph.nodes())
        
        for node in nodes:
            node_features = [
                nx.degree_centrality(self.graph)[node],
                nx.betweenness_centrality(self.graph)[node],
                nx.eigenvector_centrality(self.graph)[node],
                nx.clustering(self.graph, node),
                self._calculate_reach_centrality(node)
            ]
            features.append(node_features)
        
        # Normalize features
        scaler = StandardScaler()
        normalized_features = scaler.fit_transform(features)
        
        # Calculate Mahalanobis distance as anomaly score
        cov = np.cov(normalized_features.T)
        inv_cov = np.linalg.inv(cov)
        mean = np.mean(normalized_features, axis=0)
        
        anomaly_scores = {}
        for i, node in enumerate(nodes):
            diff = normalized_features[i] - mean
            score = np.sqrt(diff.dot(inv_cov).dot(diff.T))
            anomaly_scores[node] = score
        
        return anomaly_scores

    def get_high_risk_entities(self, risk_threshold: float = 0.8) -> List[Dict]:
        """Get entities with high risk scores and their risk factors"""
        metrics = self.calculate_network_metrics()
        high_risk_entities = []
        
        for node in self.graph.nodes():
            risk_factors = []
            
            # Check centrality metrics
            if metrics.centrality_scores[node]['betweenness'] > risk_threshold:
                risk_factors.append('high_betweenness_centrality')
            if metrics.centrality_scores[node]['pagerank'] > risk_threshold:
                risk_factors.append('high_pagerank')
                
            # Check community isolation
            community_id = metrics.community_membership[node]
            community_size = sum(1 for n, c in metrics.community_membership.items() 
                               if c == community_id)
            if community_size < 3:
                risk_factors.append('isolated_community')
                
            # Check involvement in risk patterns
            for pattern in metrics.risk_patterns:
                if node in pattern.get('entities', []):
                    risk_factors.append(f"involved_in_{pattern['type']}")
                    
            # Check anomaly score
            if metrics.anomaly_scores[node] > risk_threshold:
                risk_factors.append('high_anomaly_score')
                
            if risk_factors:
                high_risk_entities.append({
                    'entity': node,
                    'risk_factors': risk_factors,
                    'anomaly_score': metrics.anomaly_scores[node],
                    'centrality_scores': metrics.centrality_scores[node]
                })
        
        return sorted(high_risk_entities, 
                     key=lambda x: x['anomaly_score'], 
                     reverse=True)