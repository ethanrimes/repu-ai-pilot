# scripts/data_generation/load_brake_articles.py
# Path: scripts/data_generation/load_brake_articles.py

import os
import sys
import json
import random
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict

sys.path.append(str(Path(__file__).parent.parent.parent / 'backend'))

import click
import psycopg2
from dotenv import load_dotenv

# Get paths relative to the script
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent  # Adjust based on your script location
backend_dir = project_root / 'backend'

# Add backend to path
sys.path.append(str(backend_dir))

# Load root .env first (base configuration)
root_env = project_root / '.env'
if root_env.exists():
    print(f"Loading root .env from: {root_env.absolute()}")
    load_dotenv(root_env)

# Load backend .env second (overrides root values)
backend_env = backend_dir / '.env'
if backend_env.exists():
    print(f"Loading backend .env from: {backend_env.absolute()}")
    load_dotenv(backend_env, override=True)  # override=True means backend values take precedence


load_dotenv()

class BrakeArticleLoader:
    """Load brake articles and generate related data only"""
    
    def __init__(self, articles_path: str):
        self.articles_path = Path(articles_path)
        self.database_url = os.getenv('DATABASE_URL')
        self.brake_articles = []
        
        # Colombian context
        self.warehouses = ['BODEGA_NORTE', 'BODEGA_SUR', 'BODEGA_CENTRO', 
                          'BODEGA_PRINCIPAL', 'BODEGA_AEROPUERTO']
    
    def load_articles(self) -> List[Dict]:
        """Load brake articles from JSON files"""
        click.echo(f"📂 Loading brake articles from {self.articles_path}")
        
        articles = []
        json_files = list(self.articles_path.glob("*.json"))
        
        for file_path in json_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    if isinstance(data, dict) and 'articles' in data:
                        if data['articles']:
                            articles.extend(data['articles'])
                            click.echo(f"  ✅ Loaded {len(data['articles'])} from {file_path.name}")
                        else:
                            click.echo(f"  ⚠️  Empty articles in {file_path.name}")
                    elif isinstance(data, list):
                        articles.extend(data)
            except Exception as e:
                click.echo(f"  ❌ Error loading {file_path.name}: {e}")
        
        self.brake_articles = articles
        click.echo(f"📊 Total articles loaded: {len(articles)}")
        return articles
    
    def generate_stock(self) -> List[Dict]:
        """Generate stock data for articles"""
        click.echo("📦 Generating stock data...")
        
        stock_data = []
        for article in self.brake_articles:
            product_name = article.get('articleProductName', '').lower()
            
            # Determine stock levels based on product type
            is_popular = any(term in product_name 
                           for term in ['pad', 'disc', 'pastilla', 'disco'])
            
            if random.random() < 0.1:  # 10% out of stock
                quantity = 0
            elif is_popular:
                quantity = random.randint(50, 150)
            else:
                quantity = random.randint(5, 30)
            
            stock_data.append({
                'article_id': article['articleId'],
                'supplier_id': article.get('supplierId'),
                'quantity_available': quantity,
                'warehouse_location': random.choice(self.warehouses),
                'min_stock_level': 5 if is_popular else 2,
                'max_stock_level': 200 if is_popular else 50,
                'last_restocked': datetime.now() - timedelta(days=random.randint(1, 60)) if quantity > 0 else None
            })
        
        return stock_data
    
    def generate_prices(self) -> List[Dict]:
        """Generate pricing data for articles"""
        click.echo("💰 Generating price data...")
        
        prices = []
        for article in self.brake_articles:
            product_name = article.get('articleProductName', '').lower()
            
            # Base price by product type
            if 'disc' in product_name or 'disco' in product_name:
                base_price = random.uniform(150000, 800000)
            elif 'pad' in product_name or 'pastilla' in product_name:
                base_price = random.uniform(80000, 350000)
            elif 'caliper' in product_name or 'mordaza' in product_name:
                base_price = random.uniform(250000, 1200000)
            else:
                base_price = random.uniform(50000, 300000)
            
            base_price = round(base_price, -3)
            
            # Retail price
            prices.append({
                'article_id': article['articleId'],
                'price_cop': base_price,
                'cost_cop': round(base_price * 0.6, -3),
                'currency': 'COP',
                'price_type': 'retail',
                'discount_percentage': 0,
                'valid_from': datetime.now().date(),
                'valid_to': (datetime.now() + timedelta(days=365)).date()
            })
            
            # Wholesale price
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
    
    def insert_to_database(self, stock_data: List[Dict], price_data: List[Dict]):
        """Insert data into database"""
        if not self.database_url:
            click.echo("❌ DATABASE_URL not configured")
            return
        
        click.echo("🗄️ Inserting data into database...")
        
        # Parse database URL
        import re
        pattern = r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)'
        match = re.match(pattern, self.database_url)
        
        if not match:
            click.echo("❌ Invalid DATABASE_URL format")
            return
        
        db_params = {
            'user': match.group(1),
            'password': match.group(2),
            'host': match.group(3),
            'port': match.group(4),
            'database': match.group(5)
        }
        
        try:
            conn = psycopg2.connect(**db_params)
            cur = conn.cursor()
            
            # Insert stock
            click.echo("  📥 Inserting stock...")
            for stock in stock_data:
                cur.execute("""
                    INSERT INTO stock (article_id, supplier_id, quantity_available,
                                     warehouse_location, min_stock_level, max_stock_level,
                                     last_restocked)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (article_id) DO UPDATE SET
                        quantity_available = EXCLUDED.quantity_available,
                        last_updated = CURRENT_TIMESTAMP
                """, (stock['article_id'], stock['supplier_id'], 
                     stock['quantity_available'], stock['warehouse_location'],
                     stock['min_stock_level'], stock['max_stock_level'],
                     stock['last_restocked']))
            
            # Insert prices
            click.echo("  📥 Inserting prices...")
            for price in price_data:
                cur.execute("""
                    INSERT INTO prices (article_id, price_cop, cost_cop, currency,
                                      price_type, discount_percentage, valid_from, valid_to)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (article_id, price_type) DO UPDATE SET
                        price_cop = EXCLUDED.price_cop,
                        cost_cop = EXCLUDED.cost_cop,
                        valid_to = EXCLUDED.valid_to
                """, (price['article_id'], price['price_cop'], price['cost_cop'],
                     price['currency'], price['price_type'], 
                     price['discount_percentage'], price['valid_from'], 
                     price['valid_to']))
            
            conn.commit()
            click.echo("  ✅ Data inserted successfully")
            
        except Exception as e:
            click.echo(f"  ❌ Database error: {e}")
            conn.rollback()
        finally:
            cur.close()
            conn.close()

@click.command()
@click.option('--articles-path', required=True, help='Path to brake articles JSON files')
@click.option('--generate-stock/--no-stock', default=True, help='Generate stock data')
@click.option('--generate-prices/--no-prices', default=True, help='Generate price data')
@click.option('--save-json/--no-json', default=False, help='Save to JSON files')
def main(articles_path, generate_stock, generate_prices, save_json):
    """Load brake articles and generate related data"""
    
    loader = BrakeArticleLoader(articles_path)
    
    # Load articles
    if not loader.load_articles():
        click.echo("❌ No articles found")
        return
    
    stock_data = []
    price_data = []
    
    # Generate data
    if generate_stock:
        stock_data = loader.generate_stock()
        click.echo(f"  Generated {len(stock_data)} stock records")
    
    if generate_prices:
        price_data = loader.generate_prices()
        click.echo(f"  Generated {len(price_data)} price records")
    
    # Save to JSON if requested
    if save_json:
        output_dir = Path("data/generated")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if stock_data:
            with open(output_dir / "stock.json", 'w') as f:
                json.dump(stock_data, f, indent=2, default=str)
        
        if price_data:
            with open(output_dir / "prices.json", 'w') as f:
                json.dump(price_data, f, indent=2, default=str)
    
    # Insert to database
    loader.insert_to_database(stock_data, price_data)
    
    click.echo("✨ Complete!")

if __name__ == "__main__":
    main()