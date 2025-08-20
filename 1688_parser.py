#!/usr/bin/env python3
"""
1688 Product Parser for Cargo Manager
Scrapes product information from 1688.com (Alibaba B2B platform)
"""

import requests
import json
import time
import re
from urllib.parse import urljoin, urlparse, parse_qs
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import List, Dict, Optional, Any
import csv
import logging
from datetime import datetime
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('1688_parser.log'),
        logging.StreamHandler()
    ]
)

@dataclass
class ProductInfo:
    """Data class for storing product information"""
    product_id: str
    title: str
    price_range: str
    min_order: str
    supplier: str
    supplier_location: str
    product_url: str
    image_url: str
    category: str
    specifications: Dict[str, str]
    description: str
    rating: Optional[float]
    review_count: Optional[int]
    moq: Optional[int]  # Minimum Order Quantity
    unit: str
    shipping_info: str
    lead_time: str
    certification: List[str]
    sample_available: bool
    payment_terms: List[str]
    scraped_at: datetime

class Alibaba1688Parser:
    """Main parser class for 1688.com"""
    
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://1688.com"
        self.search_url = "https://s.1688.com/selloffer/offer_search.htm"
        
        # Headers to mimic a real browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        self.session.headers.update(self.headers)
        
    def search_products(self, keyword: str, max_pages: int = 5) -> List[str]:
        """Search for products and return product URLs"""
        product_urls = []
        
        for page in range(1, max_pages + 1):
            try:
                params = {
                    'keywords': keyword,
                    'beginPage': page,
                    'pageSize': 40,
                    'sortType': 'pop',
                    'uniqfield': 'uniq_offer_id'
                }
                
                response = self.session.get(self.search_url, params=params)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find product links
                product_links = soup.find_all('a', href=re.compile(r'/offer/\d+\.html'))
                
                for link in product_links:
                    product_url = urljoin(self.base_url, link['href'])
                    if product_url not in product_urls:
                        product_urls.append(product_url)
                
                logging.info(f"Page {page}: Found {len(product_links)} products")
                
                # Random delay to avoid being blocked
                time.sleep(random.uniform(1, 3))
                
            except Exception as e:
                logging.error(f"Error searching page {page}: {e}")
                continue
                
        return product_urls
    
    def parse_product_page(self, product_url: str) -> Optional[ProductInfo]:
        """Parse individual product page and extract information"""
        try:
            response = self.session.get(product_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract product ID from URL
            product_id = self._extract_product_id(product_url)
            
            # Extract basic information
            title = self._extract_title(soup)
            price_range = self._extract_price(soup)
            min_order = self._extract_min_order(soup)
            supplier = self._extract_supplier(soup)
            supplier_location = self._extract_supplier_location(soup)
            image_url = self._extract_image(soup)
            category = self._extract_category(soup)
            specifications = self._extract_specifications(soup)
            description = self._extract_description(soup)
            rating = self._extract_rating(soup)
            review_count = self._extract_review_count(soup)
            moq = self._extract_moq(soup)
            unit = self._extract_unit(soup)
            shipping_info = self._extract_shipping_info(soup)
            lead_time = self._extract_lead_time(soup)
            certification = self._extract_certification(soup)
            sample_available = self._extract_sample_availability(soup)
            payment_terms = self._extract_payment_terms(soup)
            
            product_info = ProductInfo(
                product_id=product_id,
                title=title,
                price_range=price_range,
                min_order=min_order,
                supplier=supplier,
                supplier_location=supplier_location,
                product_url=product_url,
                image_url=image_url,
                category=category,
                specifications=specifications,
                description=description,
                rating=rating,
                review_count=review_count,
                moq=moq,
                unit=unit,
                shipping_info=shipping_info,
                lead_time=lead_time,
                certification=certification,
                sample_available=sample_available,
                payment_terms=payment_terms,
                scraped_at=datetime.now()
            )
            
            logging.info(f"Successfully parsed product: {title}")
            return product_info
            
        except Exception as e:
            logging.error(f"Error parsing product page {product_url}: {e}")
            return None
    
    def _extract_product_id(self, url: str) -> str:
        """Extract product ID from URL"""
        match = re.search(r'/offer/(\d+)\.html', url)
        return match.group(1) if match else "unknown"
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract product title"""
        title_elem = soup.find('h1', class_='title') or soup.find('h1')
        return title_elem.get_text(strip=True) if title_elem else "No title"
    
    def _extract_price(self, soup: BeautifulSoup) -> str:
        """Extract price range"""
        price_elem = soup.find('span', class_='price') or soup.find('span', string=re.compile(r'¥'))
        return price_elem.get_text(strip=True) if price_elem else "Price not available"
    
    def _extract_min_order(self, soup: BeautifulSoup) -> str:
        """Extract minimum order quantity"""
        moq_elem = soup.find(string=re.compile(r'最小起订量|MOQ|起订量', re.IGNORECASE))
        if moq_elem:
            parent = moq_elem.parent
            if parent:
                return parent.get_text(strip=True)
        return "MOQ not specified"
    
    def _extract_supplier(self, soup: BeautifulSoup) -> str:
        """Extract supplier name"""
        supplier_elem = soup.find('a', class_='company-name') or soup.find('span', class_='company')
        return supplier_elem.get_text(strip=True) if supplier_elem else "Supplier not specified"
    
    def _extract_supplier_location(self, soup: BeautifulSoup) -> str:
        """Extract supplier location"""
        location_elem = soup.find('span', class_='location') or soup.find(string=re.compile(r'地区|Location'))
        return location_elem.get_text(strip=True) if location_elem else "Location not specified"
    
    def _extract_image(self, soup: BeautifulSoup) -> str:
        """Extract main product image"""
        img_elem = soup.find('img', class_='main-image') or soup.find('img', id='main-image')
        return img_elem.get('src') if img_elem else "No image"
    
    def _extract_category(self, soup: BeautifulSoup) -> str:
        """Extract product category"""
        breadcrumb = soup.find('div', class_='breadcrumb') or soup.find('nav', class_='breadcrumb')
        if breadcrumb:
            categories = [a.get_text(strip=True) for a in breadcrumb.find_all('a')]
            return ' > '.join(categories)
        return "Category not specified"
    
    def _extract_specifications(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract product specifications"""
        specs = {}
        spec_table = soup.find('table', class_='specs') or soup.find('div', class_='specifications')
        
        if spec_table:
            rows = spec_table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    key = cells[0].get_text(strip=True)
                    value = cells[1].get_text(strip=True)
                    if key and value:
                        specs[key] = value
        
        return specs
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract product description"""
        desc_elem = soup.find('div', class_='description') or soup.find('div', class_='detail')
        return desc_elem.get_text(strip=True) if desc_elem else "No description"
    
    def _extract_rating(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract product rating"""
        rating_elem = soup.find('span', class_='rating') or soup.find('div', class_='score')
        if rating_elem:
            rating_text = rating_elem.get_text(strip=True)
            try:
                return float(re.search(r'[\d.]+', rating_text).group())
            except:
                pass
        return None
    
    def _extract_review_count(self, soup: BeautifulSoup) -> Optional[int]:
        """Extract review count"""
        review_elem = soup.find('span', class_='review-count') or soup.find(string=re.compile(r'评价|reviews'))
        if review_elem:
            try:
                count_text = review_elem.get_text(strip=True)
                return int(re.search(r'\d+', count_text).group())
            except:
                pass
        return None
    
    def _extract_moq(self, soup: BeautifulSoup) -> Optional[int]:
        """Extract minimum order quantity as integer"""
        moq_text = self._extract_min_order(soup)
        try:
            return int(re.search(r'\d+', moq_text).group())
        except:
            return None
    
    def _extract_unit(self, soup: BeautifulSoup) -> str:
        """Extract unit of measurement"""
        unit_elem = soup.find(string=re.compile(r'件|个|套|米|公斤|piece|set|meter|kg', re.IGNORECASE))
        return unit_elem.get_text(strip=True) if unit_elem else "Unit not specified"
    
    def _extract_shipping_info(self, soup: BeautifulSoup) -> str:
        """Extract shipping information"""
        shipping_elem = soup.find(string=re.compile(r'运费|shipping|delivery', re.IGNORECASE))
        if shipping_elem:
            parent = shipping_elem.parent
            if parent:
                return parent.get_text(strip=True)
        return "Shipping info not available"
    
    def _extract_lead_time(self, soup: BeautifulSoup) -> str:
        """Extract lead time information"""
        lead_time_elem = soup.find(string=re.compile(r'交期|lead time|delivery time', re.IGNORECASE))
        if lead_time_elem:
            parent = lead_time_elem.parent
            if parent:
                return parent.get_text(strip=True)
        return "Lead time not specified"
    
    def _extract_certification(self, soup: BeautifulSoup) -> List[str]:
        """Extract certification information"""
        cert_elems = soup.find_all(string=re.compile(r'ISO|CE|FDA|RoHS|认证|certification', re.IGNORECASE))
        return [elem.get_text(strip=True) for elem in cert_elems if elem.get_text(strip=True)]
    
    def _extract_sample_availability(self, soup: BeautifulSoup) -> bool:
        """Extract sample availability"""
        sample_elem = soup.find(string=re.compile(r'样品|sample', re.IGNORECASE))
        return bool(sample_elem)
    
    def _extract_payment_terms(self, soup: BeautifulSoup) -> List[str]:
        """Extract payment terms"""
        payment_elems = soup.find_all(string=re.compile(r'付款|payment|T/T|L/C|D/P', re.IGNORECASE))
        return [elem.get_text(strip=True) for elem in payment_elems if elem.get_text(strip=True)]
    
    def save_to_csv(self, products: List[ProductInfo], filename: str = None):
        """Save products to CSV file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"1688_products_{timestamp}.csv"
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'product_id', 'title', 'price_range', 'min_order', 'supplier',
                'supplier_location', 'product_url', 'image_url', 'category',
                'specifications', 'description', 'rating', 'review_count',
                'moq', 'unit', 'shipping_info', 'lead_time', 'certification',
                'sample_available', 'payment_terms', 'scraped_at'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for product in products:
                writer.writerow({
                    'product_id': product.product_id,
                    'title': product.title,
                    'price_range': product.price_range,
                    'min_order': product.min_order,
                    'supplier': product.supplier,
                    'supplier_location': product.supplier_location,
                    'product_url': product.product_url,
                    'image_url': product.image_url,
                    'category': product.category,
                    'specifications': json.dumps(product.specifications, ensure_ascii=False),
                    'description': product.description,
                    'rating': product.rating,
                    'review_count': product.review_count,
                    'moq': product.moq,
                    'unit': product.unit,
                    'shipping_info': product.shipping_info,
                    'lead_time': product.lead_time,
                    'certification': json.dumps(product.certification, ensure_ascii=False),
                    'sample_available': product.sample_available,
                    'payment_terms': json.dumps(product.payment_terms, ensure_ascii=False),
                    'scraped_at': product.scraped_at.isoformat()
                })
        
        logging.info(f"Saved {len(products)} products to {filename}")
    
    def save_to_json(self, products: List[ProductInfo], filename: str = None):
        """Save products to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"1688_products_{timestamp}.json"
        
        # Convert products to dictionaries
        products_data = []
        for product in products:
            product_dict = {
                'product_id': product.product_id,
                'title': product.title,
                'price_range': product.price_range,
                'min_order': product.min_order,
                'supplier': product.supplier,
                'supplier_location': product.supplier_location,
                'product_url': product.product_url,
                'image_url': product.image_url,
                'category': product.category,
                'specifications': product.specifications,
                'description': product.description,
                'rating': product.rating,
                'review_count': product.review_count,
                'moq': product.moq,
                'unit': product.unit,
                'shipping_info': product.shipping_info,
                'lead_time': product.lead_time,
                'certification': product.certification,
                'sample_available': product.sample_available,
                'payment_terms': product.payment_terms,
                'scraped_at': product.scraped_at.isoformat()
            }
            products_data.append(product_dict)
        
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(products_data, jsonfile, ensure_ascii=False, indent=2)
        
        logging.info(f"Saved {len(products)} products to {filename}")

def main():
    """Main function to demonstrate the parser"""
    parser = Alibaba1688Parser()
    
    # Example search
    keyword = input("Enter product keyword to search: ")
    max_pages = int(input("Enter maximum pages to search (default 3): ") or "3")
    
    print(f"Searching for '{keyword}' on 1688.com...")
    
    # Search for products
    product_urls = parser.search_products(keyword, max_pages)
    print(f"Found {len(product_urls)} product URLs")
    
    # Parse product pages
    products = []
    for i, url in enumerate(product_urls[:10]):  # Limit to first 10 for demo
        print(f"Parsing product {i+1}/{min(10, len(product_urls))}...")
        product_info = parser.parse_product_page(url)
        if product_info:
            products.append(product_info)
        
        # Delay between requests
        time.sleep(random.uniform(2, 5))
    
    if products:
        # Save results
        parser.save_to_csv(products)
        parser.save_to_json(products)
        
        print(f"\nSuccessfully parsed {len(products)} products!")
        print("Results saved to CSV and JSON files.")
        
        # Display summary
        print("\nProduct Summary:")
        for product in products[:5]:  # Show first 5
            print(f"- {product.title[:50]}... | {product.price_range} | MOQ: {product.min_order}")
    else:
        print("No products were successfully parsed.")

if __name__ == "__main__":
    main()