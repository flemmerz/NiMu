import os
import json
import networkx as nx
from datetime import datetime
from typing import Dict, List
from ..data_fetchers.companies_house_fetcher import CompaniesHouseFetcher
from ..detection.network_analyzer import NetworkAnalyzer
from ..detection.shell_company_detector import ShellCompanyDetector
from ..detection.uk_shell_detector import UKShellDetector

class RealDataAnalyzer:
    def __init__(self, api_key: str):
        self.fetcher = CompaniesHouseFetcher(api_key)
        self.shell_detector = ShellCompanyDetector()
        self.uk_detector = UKShellDetector(self.shell_detector)
        
    def analyze_2024_companies(self, sample_size: int = 100) -> Dict:
        """Analyze a sample of companies incorporated in 2024"""
        # Fetch company data
        print(f'Fetching data for {sample_size} companies...')
        companies_data = self.fetcher.get_2024_companies_sample(sample_size)
        
        # Build network
        print('Building company network...')
        network = self.fetcher.build_company_network(companies_data)
        
        # Initialize network analyzer
        network_analyzer = NetworkAnalyzer(network)
        
        # Perform analysis
        print('Performing network analysis...')
        network_metrics = network_analyzer.calculate_network_metrics()
        
        print('Detecting shell company patterns...')
        shell_patterns = self.shell_detector.detect_shell_patterns()
        
        print('Performing UK-specific analysis...')
        uk_analysis = self.uk_detector.analyze_uk_specific_patterns()
        
        # Combine results
        results = {
            'summary': self._generate_summary(network_metrics, shell_patterns, uk_analysis),
            'high_risk_entities': network_analyzer.get_high_risk_entities(),
            'risk_patterns': {
                'network_patterns': network_metrics.risk_patterns,
                'shell_patterns': shell_patterns,
                'uk_specific_patterns': uk_analysis
            },
            'network_statistics': self._calculate_network_statistics(network),
            'metadata': {
                'analysis_date': datetime.now().isoformat(),
                'sample_size': sample_size,
                'companies_analyzed': len(network.nodes())
            }
        }
        
        return results
    
    def _identify_major_concerns(self, network_metrics, shell_patterns, uk_analysis) -> List[Dict]:
        """Identify major risk patterns and concerns"""
        concerns = []
        
        # Network-based concerns
        if network_metrics.suspicious_cycles:
            concerns.append({
                'type': 'circular_ownership',
                'severity': 'high',
                'count': len(network_metrics.suspicious_cycles),
                'details': 'Detected circular ownership patterns'
            })
            
        # Shell company concerns
        shell_types = {p['type'] for p in shell_patterns}
        if 'rapid_growth' in shell_types:
            concerns.append({
                'type': 'rapid_growth_pattern',
                'severity': 'high',
                'details': 'Suspicious rapid growth of related companies'
            })
            
        # UK-specific concerns
        if uk_analysis.get('psc_analysis', {}).get('complex_structures', []):
            concerns.append({
                'type': 'complex_ownership',
                'severity': 'high',
                'details': 'Complex ownership structures detected'
            })
            
        if uk_analysis.get('filing_patterns', {}).get('minimal_compliance', []):
            concerns.append({
                'type': 'compliance_issues',
                'severity': 'medium',
                'details': 'Pattern of minimal compliance with filing requirements'
            })
            
        return concerns
    
    def _count_relationship_types(self, network: nx.Graph) -> Dict:
        """Count different types of relationships in the network"""
        counts = defaultdict(int)
        for _, _, data in network.edges(data=True):
            rel_type = data.get('relationship_type')
            if rel_type:
                counts[rel_type] += 1
        return dict(counts)
    
    def generate_report(self, results: Dict, output_file: str = None) -> str:
        """Generate a human-readable report from analysis results"""
        report = []
        report.append('Risk Analysis Report')
        report.append('=' * 50)
        
        # Summary section
        report.append('\nAnalysis Summary:')
        report.append('-' * 20)
        summary = results['summary']
        report.append(f"Total Companies Analyzed: {summary['total_companies_analyzed']}")
        report.append(f"High Risk Entities: {summary['high_risk_count']}")
        
        # Risk Distribution
        report.append('\nRisk Distribution:')
        report.append('-' * 20)
        dist = summary['risk_distribution']
        report.append(f"High Risk: {dist['high_risk']}")
        report.append(f"Medium Risk: {dist['medium_risk']}")
        report.append(f"Low Risk: {dist['low_risk']}")
        
        # Major Concerns
        report.append('\nMajor Concerns:')
        report.append('-' * 20)
        for concern in summary['major_concerns']:
            report.append(f"Type: {concern['type']}")
            report.append(f"Severity: {concern['severity']}")
            report.append(f"Details: {concern['details']}\n")
        
        # Network Statistics
        report.append('\nNetwork Statistics:')
        report.append('-' * 20)
        stats = results['network_statistics']
        report.append(f"Total Connections: {stats['total_edges']}")
        report.append(f"Network Density: {stats['density']:.3f}")
        report.append(f"Average Connections per Company: {stats['average_degree']:.2f}")
        
        # High Risk Entities
        report.append('\nHigh Risk Entities:')
        report.append('-' * 20)
        for entity in results['high_risk_entities'][:10]:  # Top 10
            report.append(f"Company Number: {entity['entity']}")
            report.append(f"Risk Score: {entity['anomaly_score']:.2f}")
            report.append(f"Risk Factors: {', '.join(entity['risk_factors'])}\n")
        
        report_text = '\n'.join(report)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report_text)
        
        return report_text
    
    def save_results(self, results: Dict, output_file: str):
        """Save analysis results to file"""
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)

# Example usage
if __name__ == '__main__':
    api_key = os.environ.get('COMPANIES_HOUSE_API_KEY')
    if not api_key:
        raise ValueError('COMPANIES_HOUSE_API_KEY environment variable not set')
        
    analyzer = RealDataAnalyzer(api_key)
    
    # Analyze sample of 2024 companies
    results = analyzer.analyze_2024_companies(sample_size=100)
    
    # Generate and save report
    report = analyzer.generate_report(results, 'analysis_report.txt')
    print('\nAnalysis Report:')
    print(report)
    
    # Save detailed results
    analyzer.save_results(results, 'detailed_results.json')