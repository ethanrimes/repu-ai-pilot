# scripts/data_generation/generate_company_data.py
"""Generate synthetic company data using Faker
Path: scripts/data_generation/generate_company_data.py
"""

import json
import random
from datetime import datetime, timedelta
from faker import Faker
from typing import List, Dict
import psycopg2
from psycopg2.extras import Json
import os
from pathlib import Path

fake = Faker(['es_CO', 'es'])  # Colombian Spanish locale

class CompanyDataGenerator:
    def __init__(self, brake_articles_path: str):
        self.fake = fake
        self.brake_articles = self.load_brake_articles(brake_articles_path)
        
    def load_brake_articles(self, base_path: str) -> List[Dict]:
        """Load brake articles from JSON files"""
        articles = []
        brake_files = Path(base_path).glob("*.json")
        
        for file_path in brake_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    if 'articles' in data and data['articles']:
                        articles.extend(data['articles'])
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
                
        return articles
    
    def generate_customers(self, count: int = 100) -> List[Dict]:
        """Generate synthetic customers"""
        customers = []
        customer_types = ['retail', 'wholesale', 'mechanic']
        cities = ['Bogotá', 'Medellín', 'Cali', 'Barranquilla', 'Cartagena', 
                  'Bucaramanga', 'Pereira', 'Manizales']
        
        for _ in range(count):
            customer_type = random.choice(customer_types)
            customer = {
                'firebase_uid': fake.uuid4(),
                'email': fake.email(),
                'phone': fake.phone_number(),
                'whatsapp_number': f"+57{fake.msisdn()[3:]}",
                'name': fake.name(),
                'company_name': fake.company() if customer_type != 'retail' else None,
                'customer_type': customer_type,
                'tax_id': fake.ssn(),  # Using SSN as placeholder for NIT/CC
                'address': fake.address(),
                'city': random.choice(cities),
                'preferred_language': random.choice(['es', 'en']) if random.random() > 0.9 else 'es',
                'created_at': fake.date_time_between(start_date='-2y', end_date='now'),
                'last_active': fake.date_time_between(start_date='-30d', end_date='now')
            }
            customers.append(customer)
            
        return customers
    
    def generate_stock_data(self) -> List[Dict]:
        """Generate stock data for brake articles"""
        stock_data = []
        warehouses = ['BODEGA_NORTE', 'BODEGA_SUR', 'BODEGA_CENTRO', 'PRINCIPAL']
        
        for article in self.brake_articles:
            stock = {
                'article_id': article['articleId'],
                'supplier_id': article.get('supplierId'),
                'quantity_available': random.randint(0, 150),
                'warehouse_location': random.choice(warehouses),
                'min_stock_level': random.randint(5, 20),
                'max_stock_level': random.randint(50, 200),
                'last_restocked': fake.date_time_between(start_date='-60d', end_date='now'),
                'last_updated': datetime.utcnow()
            }
            stock_data.append(stock)
            
        return stock_data
    
    def generate_prices(self) -> List[Dict]:
        """Generate price data for brake articles"""
        prices = []
        
        for article in self.brake_articles:
            # Base price based on product type
            if 'disc' in article['articleProductName'].lower():
                base_price = random.uniform(150000, 800000)  # Brake discs
            elif 'pad' in article['articleProductName'].lower():
                base_price = random.uniform(80000, 350000)   # Brake pads
            elif 'caliper' in article['articleProductName'].lower():
                base_price = random.uniform(250000, 1200000) # Brake calipers
            else:
                base_price = random.uniform(50000, 500000)   # Other parts
            
            # Retail price
            prices.append({
                'article_id': article['articleId'],
                'price_cop': round(base_price, -3),  # Round to nearest 1000
                'cost_cop': round(base_price * 0.6, -3),
                'currency': 'COP',
                'price_type': 'retail',
                'discount_percentage': 0,
                'valid_from': datetime.now().date(),
                'valid_to': (datetime.now() + timedelta(days=365)).date()
            })
            
            # Wholesale price (15% discount)
            prices.append({
                'article_id': article['articleId'],
                'price_cop': round(base_price * 0.85, -3),
                'cost_cop': round(base_price * 0.6, -3),
                'currency': 'COP',
                'price_type': 'wholesale',
                'discount_percentage': 15,
                'valid_from': datetime.now().date(),
                'valid_to': (datetime.now() + timedelta(days=365)).date()
            })
            
        return prices
    
    def generate_orders(self, customers: List[Dict], count: int = 200) -> tuple:
        """Generate orders and order items"""
        orders = []
        order_items = []
        statuses = ['pending', 'confirmed', 'paid', 'shipped', 'delivered', 'cancelled']
        payment_methods = ['cash', 'transfer', 'card', 'nequi', 'daviplata']
        
        for i in range(count):
            customer = random.choice(customers)
            num_items = random.randint(1, 5)
            
            # Create order
            order_date = fake.date_time_between(start_date='-6m', end_date='now')
            order = {
                'customer_id': customers.index(customer) + 1,  # Assuming 1-based IDs
                'order_number': f"ORD-{order_date.year}{order_date.month:02d}-{i+1:04d}",
                'channel': random.choice(['web', 'whatsapp']),
                'status': random.choice(statuses),
                'payment_method': random.choice(payment_methods),
                'subtotal_cop': 0,
                'tax_cop': 0,
                'shipping_cop': random.choice([0, 15000, 25000, 35000]),
                'total_cop': 0,
                'notes': fake.sentence() if random.random() > 0.7 else None,
                'shipping_address': customer['address'],
                'created_at': order_date,
                'updated_at': order_date
            }
            
            # Create order items
            selected_articles = random.sample(self.brake_articles, min(num_items, len(self.brake_articles)))
            subtotal = 0
            
            for article in selected_articles:
                quantity = random.randint(1, 4)
                unit_price = random.uniform(50000, 500000)
                discount = random.choice([0, 0, 0, 5000, 10000, 20000])
                total_price = (unit_price * quantity) - discount
                
                item = {
                    'order_id': i + 1,
                    'article_id': article['articleId'],
                    'article_number': article['articleNo'],
                    'supplier_name': article['supplierName'],
                    'product_name': article['articleProductName'],
                    'quantity': quantity,
                    'unit_price_cop': round(unit_price, -3),
                    'discount_cop': discount,
                    'total_price_cop': round(total_price, -3)
                }
                order_items.append(item)
                subtotal += total_price
            
            # Update order totals
            order['subtotal_cop'] = round(subtotal, -3)
            order['tax_cop'] = round(subtotal * 0.19, -3)  # 19% IVA
            order['total_cop'] = order['subtotal_cop'] + order['tax_cop'] + order['shipping_cop']
            
            orders.append(order)
            
        return orders, order_items
    
    def save_to_json(self, data: Dict, output_dir: str = "data/generated"):
        """Save generated data to JSON files"""
        os.makedirs(output_dir, exist_ok=True)
        
        for key, value in data.items():
            file_path = os.path.join(output_dir, f"{key}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(value, f, ensure_ascii=False, indent=2, default=str)
            print(f"Saved {len(value)} {key} to {file_path}")

if __name__ == "__main__":
    # Initialize generator
    generator = CompanyDataGenerator("/Users/ethankallett/Documents/Projects/repu-data/articles")
    
    # Generate all data
    print("Generating synthetic data...")
    customers = generator.generate_customers(100)
    stock = generator.generate_stock_data()
    prices = generator.generate_prices()
    orders, order_items = generator.generate_orders(customers, 200)
    
    # Save to JSON
    data = {
        'customers': customers,
        'stock': stock,
        'prices': prices,
        'orders': orders,
        'order_items': order_items
    }
    
    generator.save_to_json(data)
    print("Data generation complete!")