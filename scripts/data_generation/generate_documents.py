# scripts/data_generation/generate_documents.py
"""Generate synthetic unstructured documents using GPT
Path: scripts/data_generation/generate_documents.py
"""

import os
import json
from typing import List, Dict
from openai import OpenAI
from pathlib import Path
import hashlib

class DocumentGenerator:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.brake_articles = self.load_brake_articles()
        
    def load_brake_articles(self) -> List[Dict]:
        """Load brake articles for context"""
        # Implementation same as above
        pass
    
    def generate_technical_manual(self, article: Dict, language: str = 'es') -> str:
        """Generate a technical manual for a brake component"""
        
        prompt = f"""
        Generate a detailed technical manual in {language} for the following brake component:
        
        Product: {article['articleProductName']}
        Article Number: {article['articleNo']}
        Supplier: {article['supplierName']}
        
        The manual should include:
        1. Product description and specifications
        2. Installation instructions (step by step)
        3. Torque specifications
        4. Safety warnings
        5. Maintenance recommendations
        6. Troubleshooting common issues
        7. Compatibility notes
        
        Make it realistic for a Colombian automotive aftermarket context.
        Use technical Spanish automotive terminology.
        Format in markdown.
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a technical writer for automotive parts in Colombia."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        return response.choices[0].message.content
    
    def generate_faq_content(self, language: str = 'es') -> List[Dict]:
        """Generate FAQ content for the aftermarket business"""
        
        prompt = f"""
        Generate 20 frequently asked questions and answers in {language} for a Colombian automotive 
        aftermarket parts supplier specializing in brake components.
        
        Topics should cover:
        - Product compatibility and fitment
        - Pricing and payment methods
        - Shipping and delivery in Colombia
        - Warranty and returns
        - Installation support
        - Store locations and hours
        - Quality certifications
        
        Format as JSON array with 'question', 'answer', and 'category' fields.
        Use Colombian Spanish and local context (cities, payment methods like Nequi/Daviplata, etc.)
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a customer service expert for a Colombian auto parts store."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=3000,
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    
    def generate_policies(self, language: str = 'es') -> Dict[str, str]:
        """Generate policy documents"""
        
        policies = {}
        
        # Return Policy
        return_prompt = f"""
        Generate a comprehensive return and warranty policy in {language} for a Colombian automotive 
        parts supplier. Include:
        - 30-day return policy
        - Warranty terms for different product types
        - Conditions and exclusions
        - Return process steps
        - Refund methods
        - Colombian consumer protection law references
        
        Format in markdown. Make it legally appropriate for Colombia.
        """
        
        # Shipping Policy
        shipping_prompt = f"""
        Generate a shipping policy in {language} for Colombian customers. Include:
        - Shipping zones (major cities)
        - Delivery times
        - Shipping costs
        - Free shipping thresholds
        - Carrier partners
        - Order tracking
        - Remote area surcharges
        
        Reference Colombian cities and regions. Format in markdown.
        """
        
        for policy_type, prompt in [('return_policy', return_prompt), 
                                    ('shipping_policy', shipping_prompt)]:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a legal and business policy writer in Colombia."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=2000
            )
            policies[policy_type] = response.choices[0].message.content
            
        return policies
    
    def save_documents(self, output_dir: str = "data/documents"):
        """Generate and save all documents"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate technical manuals for sample articles
        manuals_dir = os.path.join(output_dir, "manuals")
        os.makedirs(manuals_dir, exist_ok=True)
        
        for article in self.brake_articles[:10]:  # Generate for first 10 articles
            manual = self.generate_technical_manual(article, 'es')
            filename = f"manual_{article['articleNo'].replace(' ', '_')}.md"
            with open(os.path.join(manuals_dir, filename), 'w', encoding='utf-8') as f:
                f.write(manual)
            print(f"Generated manual: {filename}")
        
        # Generate FAQs
        faqs = self.generate_faq_content('es')
        with open(os.path.join(output_dir, "faqs.json"), 'w', encoding='utf-8') as f:
            json.dump(faqs, f, ensure_ascii=False, indent=2)
        print(f"Generated {len(faqs)} FAQs")
        
        # Generate policies
        policies = self.generate_policies('es')
        policies_dir = os.path.join(output_dir, "policies")
        os.makedirs(policies_dir, exist_ok=True)
        
        for policy_name, content in policies.items():
            with open(os.path.join(policies_dir, f"{policy_name}.md"), 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Generated policy: {policy_name}")

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    generator = DocumentGenerator(os.getenv("OPENAI_API_KEY"))
    generator.save_documents()