import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os

class CompaniesHouseFetcher:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = 'https://api.company-information.service.gov.uk'
        self.session = requests.Session()
        self.session.auth = (self.api_key, '')

    def get_company_profile(self, company_number: str) -> Dict:
        """Fetch full company profile"""
        url = f'{self.base_url}/company/{company_number}'
        response = self.session.get(url)
        if response.status_code == 200:
            return response.json()
        return None

    def get_officers(self, company_number: str) -> List[Dict]:
        """Fetch company officers"""
        url = f'{self.base_url}/company/{company_number}/officers'
        response = self.session.get(url)
        if response.status_code == 200:
            return response.json().get('items', [])
        return []

    def get_persons_with_significant_control(self, company_number: str) -> List[Dict]:
        """Fetch PSC data"""
        url = f'{self.base_url}/company/{company_number}/persons-with-significant-control'
        response = self.session.get(url)
        if response.status_code == 200:
            return response.json().get('items', [])
        return []

    def get_filing_history(self, company_number: str) -> List[Dict]:
        """Fetch filing history"""
        url = f'{self.base_url}/company/{company_number}/filing-history'
        response = self.session.get(url)
        if response.status_code == 200:
            return response.json().get('items', [])
        return []

    def search_companies(self, 
                        incorporated_from: str,
                        incorporated_to: Optional[str] = None,
                        size: int = 100) -> List[Dict]:
        """Search for companies within incorporation date range"""
        url = f'{self.base_url}/advanced-search/companies'
        
        params = {
            'incorporated_from': incorporated_from,
            'size': size
        }
        if incorporated_to:
            params['incorporated_to'] = incorporated_to

        response = self.session.get(url, params=params)
        if response.status_code == 200:
            return response.json().get('items', [])
        return []

    def get_complete_company_data(self, company_number: str) -> Dict:
        """Fetch all available data for a company"""
        data = {
            'profile': self.get_company_profile(company_number),
            'officers': self.get_officers(company_number),
            'psc': self.get_persons_with_significant_control(company_number),
            'filing_history': self.get_filing_history(company_number)
        }
        return data

    def get_2024_companies_sample(self, sample_size: int = 100) -> List[Dict]:
        """Get a sample of companies incorporated in 2024"""
        companies = self.search_companies(
            incorporated_from='2024-01-01',
            incorporated_to='2024-12-31',
            size=sample_size
        )
        
        complete_data = []
        for company in companies:
            company_number = company['company_number']
            data = self.get_complete_company_data(company_number)
            complete_data.append(data)
            
        return complete_data

    def build_company_network(self, companies_data: List[Dict]) -> nx.Graph:
        """Build network from companies data"""
        G = nx.Graph()
        
        # Add nodes (companies)
        for data in companies_data:
            profile = data['profile']
            if profile:
                company_number = profile['company_number']
                G.add_node(company_number, 
                          incorporation_date=profile.get('date_of_creation'),
                          company_type=profile.get('type'),
                          company_status=profile.get('company_status'),
                          sic_codes=profile.get('sic_codes', []),
                          registered_office=profile.get('registered_office_address'),
                          directors=data['officers'],
                          psc=data['psc'],
                          filing_history=data['filing_history'])
        
        # Add edges based on relationships
        self._add_director_relationships(G, companies_data)
        self._add_address_relationships(G, companies_data)
        self._add_psc_relationships(G, companies_data)
        
        return G

    def _add_director_relationships(self, G: nx.Graph, companies_data: List[Dict]):
        """Add edges for shared directors"""
        director_companies = {}
        
        for data in companies_data:
            profile = data['profile']
            if not profile:
                continue
                
            company_number = profile['company_number']
            for officer in data['officers']:
                director_key = (officer.get('name'), 
                              officer.get('date_of_birth', {}).get('month'),
                              officer.get('date_of_birth', {}).get('year'))
                if director_key not in director_companies:
                    director_companies[director_key] = set()
                director_companies[director_key].add(company_number)
        
        # Add edges for shared directors
        for companies in director_companies.values():
            if len(companies) > 1:
                companies = list(companies)
                for i in range(len(companies)):
                    for j in range(i+1, len(companies)):
                        G.add_edge(companies[i], companies[j], 
                                  relationship_type='shared_director',
                                  strength=0.7)

    def _add_address_relationships(self, G: nx.Graph, companies_data: List[Dict]):
        """Add edges for shared addresses"""
        address_companies = {}
        
        for data in companies_data:
            profile = data['profile']
            if not profile:
                continue
                
            company_number = profile['company_number']
            address = profile.get('registered_office_address')
            if address:
                address_key = (address.get('address_line_1'),
                             address.get('postal_code'))
                if address_key not in address_companies:
                    address_companies[address_key] = set()
                address_companies[address_key].add(company_number)
        
        # Add edges for shared addresses
        for companies in address_companies.values():
            if len(companies) > 1:
                companies = list(companies)
                for i in range(len(companies)):
                    for j in range(i+1, len(companies)):
                        G.add_edge(companies[i], companies[j],
                                  relationship_type='shared_address',
                                  strength=0.6)

    def _add_psc_relationships(self, G: nx.Graph, companies_data: List[Dict]):
        """Add edges for PSC relationships"""
        psc_companies = {}
        
        for data in companies_data:
            profile = data['profile']
            if not profile:
                continue
                
            company_number = profile['company_number']
            for psc in data['psc']:
                if psc.get('kind') == 'corporate-entity':
                    psc_key = psc.get('name')
                    if psc_key not in psc_companies:
                        psc_companies[psc_key] = set()
                    psc_companies[psc_key].add(company_number)
        
        # Add edges for shared PSCs
        for companies in psc_companies.values():
            if len(companies) > 1:
                companies = list(companies)
                for i in range(len(companies)):
                    for j in range(i+1, len(companies)):
                        G.add_edge(companies[i], companies[j],
                                  relationship_type='shared_psc',
                                  strength=0.8)