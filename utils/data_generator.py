"""Synthetic data generator for UK Tender Scraper."""

from faker import Faker
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any


class TenderDataGenerator:
    """Generate synthetic tender data for testing."""
    
    def __init__(self, seed: int = 42):
        """Initialize the data generator."""
        self.faker = Faker('en_GB')
        Faker.seed(seed)
        random.seed(seed)
        
        self.statuses = ['planned', 'active', 'complete', 'cancelled', 'unsuccessful']
        self.stages = ['planning', 'tender', 'award']
        self.categories = ['goods', 'services', 'works']
        self.cpv_codes = [
            ('03000000', 'Agricultural, farming, fishing, forestry and related products'),
            ('09000000', 'Petroleum products, fuel, electricity and other sources of energy'),
            ('15000000', 'Food, beverages, tobacco and related products'),
            ('18000000', 'Clothing, footwear, luggage articles and accessories'),
            ('22000000', 'Printed matter and related products'),
            ('30000000', 'Office and computing machinery, equipment and supplies'),
            ('31000000', 'Electrical machinery, apparatus, equipment and consumables'),
            ('32000000', 'Radio, television, communication, telecommunication equipment'),
            ('33000000', 'Medical equipments, pharmaceuticals and personal care products'),
            ('34000000', 'Transport equipment and auxiliary products to transportation'),
            ('35000000', 'Security, fire-fighting, police and defence equipment'),
            ('37000000', 'Musical instruments, sport goods, games, toys'),
            ('38000000', 'Laboratory, optical and precision equipments'),
            ('39000000', 'Furniture, furnishings, domestic appliances and cleaning products'),
            ('41000000', 'Collected and purified water'),
            ('42000000', 'Industrial machinery'),
            ('43000000', 'Mining, quarrying and construction machinery'),
            ('44000000', 'Construction structures and materials'),
            ('45000000', 'Construction work'),
            ('48000000', 'Software package and information systems'),
            ('50000000', 'Repair and maintenance services'),
            ('51000000', 'Installation services'),
            ('55000000', 'Hotel, restaurant and retail trade services'),
            ('60000000', 'Transport services'),
            ('63000000', 'Supporting and auxiliary transport services'),
            ('64000000', 'Postal and telecommunications services'),
            ('65000000', 'Public utilities'),
            ('66000000', 'Financial and insurance services'),
            ('70000000', 'Real estate services'),
            ('71000000', 'Architectural, construction, engineering services'),
            ('72000000', 'IT services: consulting, software development'),
            ('73000000', 'Research and development services'),
            ('75000000', 'Administration, defence and social security services'),
            ('76000000', 'Services related to the oil and gas industry'),
            ('77000000', 'Agricultural, forestry, horticultural services'),
            ('79000000', 'Business services: law, marketing, consulting'),
            ('80000000', 'Education and training services'),
            ('85000000', 'Health and social work services'),
            ('90000000', 'Sewage, refuse, cleaning and environmental services'),
            ('92000000', 'Recreational, cultural and sporting services'),
            ('98000000', 'Other community, social and personal services'),
        ]
        
        self.uk_authorities = [
            'Department for Education',
            'Ministry of Defence',
            'Home Office',
            'Department of Health and Social Care',
            'HM Treasury',
            'Cabinet Office',
            'Department for Transport',
            'NHS England',
            'Greater London Authority',
            'Manchester City Council',
            'Birmingham City Council',
            'Leeds City Council',
            'Liverpool City Council',
            'Bristol City Council',
            'Newcastle City Council',
            'Sheffield City Council',
            'Police Service of Scotland',
            'Welsh Government',
            'Scottish Government',
            'Northern Ireland Executive',
        ]
    
    def generate_tender(self, notice_number: int = None) -> Dict[str, Any]:
        """Generate a single synthetic tender."""
        if notice_number is None:
            notice_number = random.randint(1, 999999)
        
        year = random.randint(2023, 2025)
        notice_id = f"{notice_number:06d}-{year}"
        ocid = f"ocds-h6vhtk-{random.randint(0, 0xFFFFFF):06x}"
        
        # Random dates
        days_ago = random.randint(0, 365)
        pub_date = datetime.now() - timedelta(days=days_ago)
        
        # Random classification
        cpv_id, cpv_desc = random.choice(self.cpv_codes)
        
        # Random buyer
        buyer_name = random.choice(self.uk_authorities)
        
        # Random value
        value_amount = round(random.uniform(10000, 10000000), 2)
        
        tender_data = {
            'notice_id': notice_id,
            'ocid': ocid,
            'title': self._generate_title(),
            'description': self.faker.text(max_nb_chars=500),
            'status': random.choice(self.statuses),
            'stage': random.choice(self.stages),
            'publication_date': pub_date.isoformat(),
            'value_amount': value_amount,
            'value_currency': 'GBP',
            'buyer_name': buyer_name,
            'buyer_id': f"GB-GOV-{random.randint(1000, 9999)}",
            'buyer_email': self.faker.company_email(),
            'buyer_address': self._generate_uk_address(),
            'classification_id': cpv_id,
            'classification_description': cpv_desc,
            'main_procurement_category': random.choice(self.categories),
            'legal_basis': random.choice(['32014L0024', '32014L0025', '2023/54']),
        }
        
        # Generate lots (30% chance)
        if random.random() < 0.3:
            tender_data['lots'] = self._generate_lots(1, 3)
        
        # Generate documents (50% chance)
        if random.random() < 0.5:
            tender_data['documents'] = self._generate_documents(1, 3)
        
        return tender_data
    
    def _generate_title(self) -> str:
        """Generate a realistic tender title."""
        templates = [
            "Supply and Delivery of {product}",
            "Provision of {service} Services",
            "{service} Framework Agreement",
            "Construction of {project}",
            "Maintenance and Support for {product}",
            "{service} Consultancy Services",
            "Installation of {product}",
            "Design and Build of {project}",
            "Managed {service} Service",
            "Procurement of {product}",
        ]
        
        products = [
            'IT Equipment', 'Medical Supplies', 'Office Furniture', 
            'Vehicles', 'Catering Equipment', 'Security Systems',
            'Software Licenses', 'Laboratory Equipment', 'Cleaning Products'
        ]
        
        services = [
            'IT Support', 'Facilities Management', 'Consultancy',
            'Training', 'Legal', 'HR', 'Marketing', 'Security',
            'Waste Management', 'Catering', 'Transport'
        ]
        
        projects = [
            'New Office Building', 'School Extension', 'Hospital Wing',
            'Road Infrastructure', 'Community Centre', 'Sports Facility'
        ]
        
        template = random.choice(templates)
        
        if '{product}' in template:
            return template.format(product=random.choice(products))
        elif '{service}' in template:
            return template.format(service=random.choice(services))
        elif '{project}' in template:
            return template.format(project=random.choice(projects))
        
        return template
    
    def _generate_uk_address(self) -> str:
        """Generate a UK address."""
        street = self.faker.street_address()
        city = self.faker.city()
        postcode = self.faker.postcode()
        return f"{street}, {city}, {postcode}, United Kingdom"
    
    def _generate_lots(self, min_lots: int = 1, max_lots: int = 3) -> List[Dict[str, Any]]:
        """Generate lots for a tender."""
        num_lots = random.randint(min_lots, max_lots)
        lots = []
        
        for i in range(num_lots):
            lot = {
                'lot_id': str(i + 1),
                'description': self.faker.text(max_nb_chars=200),
                'value_amount': round(random.uniform(5000, 1000000), 2),
                'value_currency': 'GBP',
                'status': random.choice(self.statuses),
                'duration_days': random.randint(30, 1095),
                'has_renewal': random.choice([True, False]),
                'has_options': random.choice([True, False]),
            }
            
            if lot['has_renewal']:
                lot['renewal_description'] = "Option to extend for additional period"
            
            if lot['has_options']:
                lot['options_description'] = "Additional services may be requested"
            
            lots.append(lot)
        
        return lots
    
    def _generate_documents(self, min_docs: int = 1, max_docs: int = 3) -> List[Dict[str, Any]]:
        """Generate documents for a tender."""
        num_docs = random.randint(min_docs, max_docs)
        documents = []
        
        doc_types = [
            'tenderNotice', 'awardNotice', 'contractNotice',
            'technicalSpecifications', 'evaluationCriteria',
            'contractDraft', 'clarifications'
        ]
        
        for i in range(num_docs):
            doc = {
                'document_id': f"doc-{i+1}",
                'document_type': random.choice(doc_types),
                'description': self.faker.sentence(),
                'url': self.faker.url(),
                'date_published': (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat(),
                'format': random.choice(['application/pdf', 'text/html', 'application/msword']),
            }
            documents.append(doc)
        
        return documents
    
    def generate_tenders(self, count: int = 100) -> List[Dict[str, Any]]:
        """Generate multiple synthetic tenders."""
        tenders = []
        for i in range(count):
            tender = self.generate_tender(notice_number=i + 1)
            tenders.append(tender)
        return tenders
