#!/usr/bin/env python3
"""
1688 (Alibaba) Product Parser for Cargo Manager
A comprehensive parser to extract product information from 1688.com product cards
"""

import requests
import json
import csv
import time
import re
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class Product:
    """Data class for product information"""
    id: str
    title: str
    price: str
    price_range: str
    min_order_quantity: str
    supplier_name: str
    supplier_location: str
    supplier_rating: str
    product_url: str
    image_urls: List[str]
    description: str
    specifications: Dict[str, str]
    shipping_info: str
    category: str
    keywords: List[str]
    scraped_at: str

class Alibaba1688Parser:
    """
    Main parser class for extracting product information from 1688.com
    """
    
    def __init__(self, delay_between_requests: float = 1.0):
        """
        Initialize the parser with configuration
        
        Args:
            delay_between_requests: Delay in seconds between requests to avoid rate limiting
        """
        self.delay = delay_between_requests
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
    def extract_product_data(self, product_html: str, product_url: str) -> Optional[Product]:
        """
        Extract product data from HTML content
        
        Args:
            product_html: HTML content of the product page
            product_url: URL of the product page
            
        Returns:
            Product object with extracted data or None if extraction fails
        """
        try:
            # Extract product ID from URL
            product_id = self._extract_product_id(product_url)
            
            # Extract basic product information
            title = self._extract_title(product_html)
            price = self._extract_price(product_html)
            price_range = self._extract_price_range(product_html)
            min_order = self._extract_min_order_quantity(product_html)
            
            # Extract supplier information
            supplier_name = self._extract_supplier_name(product_html)
            supplier_location = self._extract_supplier_location(product_html)
            supplier_rating = self._extract_supplier_rating(product_html)
            
            # Extract product details
            image_urls = self._extract_image_urls(product_html)
            description = self._extract_description(product_html)
            specifications = self._extract_specifications(product_html)
            shipping_info = self._extract_shipping_info(product_html)
            category = self._extract_category(product_html)
            keywords = self._extract_keywords(product_html, title, description)
            
            return Product(
                id=product_id,
                title=title,
                price=price,
                price_range=price_range,
                min_order_quantity=min_order,
                supplier_name=supplier_name,
                supplier_location=supplier_location,
                supplier_rating=supplier_rating,
                product_url=product_url,
                image_urls=image_urls,
                description=description,
                specifications=specifications,
                shipping_info=shipping_info,
                category=category,
                keywords=keywords,
                scraped_at=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Error extracting product data from {product_url}: {str(e)}")
            return None
    
    def _extract_product_id(self, url: str) -> str:
        """Extract product ID from URL"""
        # Pattern to match 1688 product IDs
        pattern = r'offer/(\d+)\.html'
        match = re.search(pattern, url)
        return match.group(1) if match else url.split('/')[-1]
    
    def _extract_title(self, html: str) -> str:
        """Extract product title"""
        patterns = [
            r'<h1[^>]*class="[^"]*title[^"]*"[^>]*>([^<]+)</h1>',
            r'<title>([^<]+)</title>',
            r'data-title="([^"]+)"',
            r'<h1[^>]*>([^<]+)</h1>'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                return self._clean_text(match.group(1))
        return "Unknown Product"
    
    def _extract_price(self, html: str) -> str:
        """Extract product price"""
        patterns = [
            r'¥\s*(\d+\.?\d*)',
            r'price["\']:\s*["\']?(\d+\.?\d*)',
            r'data-price="([^"]+)"',
            r'class="[^"]*price[^"]*"[^>]*>¥?\s*(\d+\.?\d*)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                return f"¥{match.group(1)}"
        return "Price not available"
    
    def _extract_price_range(self, html: str) -> str:
        """Extract price range information"""
        patterns = [
            r'¥\s*(\d+\.?\d*)\s*-\s*¥?\s*(\d+\.?\d*)',
            r'price-range["\']:\s*["\']([^"\']+)["\']'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                if len(match.groups()) == 2:
                    return f"¥{match.group(1)} - ¥{match.group(2)}"
                else:
                    return match.group(1)
        return "Single price"
    
    def _extract_min_order_quantity(self, html: str) -> str:
        """Extract minimum order quantity"""
        patterns = [
            r'起订量[：:]\s*(\d+)',
            r'min-order["\']:\s*["\']?(\d+)',
            r'最小订购量[：:]\s*(\d+)',
            r'起批量[：:]\s*(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                return match.group(1)
        return "1"
    
    def _extract_supplier_name(self, html: str) -> str:
        """Extract supplier/company name"""
        patterns = [
            r'company-name["\']:\s*["\']([^"\']+)["\']',
            r'供应商[：:]\s*([^<\n]+)',
            r'class="[^"]*company[^"]*"[^>]*>([^<]+)',
            r'店铺名称[：:]\s*([^<\n]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                return self._clean_text(match.group(1))
        return "Unknown Supplier"
    
    def _extract_supplier_location(self, html: str) -> str:
        """Extract supplier location"""
        patterns = [
            r'所在地[：:]\s*([^<\n]+)',
            r'location["\']:\s*["\']([^"\']+)["\']',
            r'地址[：:]\s*([^<\n]+)',
            r'class="[^"]*location[^"]*"[^>]*>([^<]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                return self._clean_text(match.group(1))
        return "Location not specified"
    
    def _extract_supplier_rating(self, html: str) -> str:
        """Extract supplier rating"""
        patterns = [
            r'rating["\']:\s*["\']?(\d+\.?\d*)',
            r'评分[：:]\s*(\d+\.?\d*)',
            r'class="[^"]*rating[^"]*"[^>]*>(\d+\.?\d*)',
            r'星级[：:]\s*(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                return match.group(1)
        return "No rating"
    
    def _extract_image_urls(self, html: str) -> List[str]:
        """Extract product image URLs"""
        patterns = [
            r'src="([^"]+\.(?:jpg|jpeg|png|gif|webp))"',
            r'data-src="([^"]+\.(?:jpg|jpeg|png|gif|webp))"',
            r'"images":\s*\[([^\]]+)\]'
        ]
        
        image_urls = []
        for pattern in patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            for match in matches:
                if isinstance(match, str) and ('product' in match.lower() or 'item' in match.lower()):
                    # Clean and validate URL
                    url = match.strip('"\'')
                    if url.startswith('//'):
                        url = 'https:' + url
                    elif url.startswith('/'):
                        url = 'https://cbu01.alicdn.com' + url
                    image_urls.append(url)
        
        return list(set(image_urls))[:10]  # Limit to 10 unique images
    
    def _extract_description(self, html: str) -> str:
        """Extract product description"""
        patterns = [
            r'<div[^>]*class="[^"]*description[^"]*"[^>]*>([^<]+)</div>',
            r'产品描述[：:]\s*([^<\n]+)',
            r'description["\']:\s*["\']([^"\']+)["\']',
            r'<p[^>]*class="[^"]*desc[^"]*"[^>]*>([^<]+)</p>'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
            if match:
                return self._clean_text(match.group(1))[:500]  # Limit description length
        return "No description available"
    
    def _extract_specifications(self, html: str) -> Dict[str, str]:
        """Extract product specifications"""
        specs = {}
        
        # Pattern to match specification tables
        spec_patterns = [
            r'<tr[^>]*>\s*<td[^>]*>([^<]+)</td>\s*<td[^>]*>([^<]+)</td>\s*</tr>',
            r'规格[：:]\s*([^<\n]+)',
            r'材质[：:]\s*([^<\n]+)',
            r'尺寸[：:]\s*([^<\n]+)',
            r'重量[：:]\s*([^<\n]+)'
        ]
        
        for pattern in spec_patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            for match in matches:
                if len(match) == 2:
                    key = self._clean_text(match[0])
                    value = self._clean_text(match[1])
                    specs[key] = value
                elif len(match) == 1:
                    specs["specification"] = self._clean_text(match[0])
        
        return specs
    
    def _extract_shipping_info(self, html: str) -> str:
        """Extract shipping information"""
        patterns = [
            r'运费[：:]\s*([^<\n]+)',
            r'shipping["\']:\s*["\']([^"\']+)["\']',
            r'配送[：:]\s*([^<\n]+)',
            r'物流[：:]\s*([^<\n]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                return self._clean_text(match.group(1))
        return "Shipping info not available"
    
    def _extract_category(self, html: str) -> str:
        """Extract product category"""
        patterns = [
            r'category["\']:\s*["\']([^"\']+)["\']',
            r'分类[：:]\s*([^<\n]+)',
            r'类别[：:]\s*([^<\n]+)',
            r'<nav[^>]*class="[^"]*breadcrumb[^"]*"[^>]*>.*?<a[^>]*>([^<]+)</a>'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                return self._clean_text(match.group(1))
        return "Uncategorized"
    
    def _extract_keywords(self, html: str, title: str, description: str) -> List[str]:
        """Extract relevant keywords from product data"""
        keywords = []
        
        # Extract from meta keywords
        meta_pattern = r'<meta[^>]*name="keywords"[^>]*content="([^"]+)"'
        match = re.search(meta_pattern, html, re.IGNORECASE)
        if match:
            keywords.extend([k.strip() for k in match.group(1).split(',')])
        
        # Extract from title and description
        text = f"{title} {description}".lower()
        common_keywords = [
            'wholesale', '批发', 'factory', '工厂', 'manufacturer', '制造商',
            'custom', '定制', 'oem', 'odm', 'quality', '质量', 'cheap', '便宜'
        ]
        
        for keyword in common_keywords:
            if keyword in text:
                keywords.append(keyword)
        
        return list(set(keywords))[:10]  # Limit to 10 unique keywords
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def scrape_product(self, product_url: str) -> Optional[Product]:
        """
        Scrape a single product from 1688
        
        Args:
            product_url: URL of the product page
            
        Returns:
            Product object or None if scraping fails
        """
        try:
            logger.info(f"Scraping product: {product_url}")
            
            response = self.session.get(product_url, timeout=30)
            response.raise_for_status()
            
            product = self.extract_product_data(response.text, product_url)
            
            if product:
                logger.info(f"Successfully scraped product: {product.title}")
            else:
                logger.warning(f"Failed to extract product data from: {product_url}")
            
            # Rate limiting
            time.sleep(self.delay)
            
            return product
            
        except Exception as e:
            logger.error(f"Error scraping product {product_url}: {str(e)}")
            return None
    
    def scrape_products(self, product_urls: List[str]) -> List[Product]:
        """
        Scrape multiple products from 1688
        
        Args:
            product_urls: List of product URLs
            
        Returns:
            List of successfully scraped Product objects
        """
        products = []
        
        for i, url in enumerate(product_urls, 1):
            logger.info(f"Scraping product {i}/{len(product_urls)}")
            
            product = self.scrape_product(url)
            if product:
                products.append(product)
        
        logger.info(f"Successfully scraped {len(products)} out of {len(product_urls)} products")
        return products
    
    def export_to_csv(self, products: List[Product], filename: str = "1688_products.csv") -> None:
        """
        Export products to CSV file
        
        Args:
            products: List of Product objects
            filename: Output CSV filename
        """
        if not products:
            logger.warning("No products to export")
            return
        
        fieldnames = [
            'id', 'title', 'price', 'price_range', 'min_order_quantity',
            'supplier_name', 'supplier_location', 'supplier_rating',
            'product_url', 'image_urls', 'description', 'specifications',
            'shipping_info', 'category', 'keywords', 'scraped_at'
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for product in products:
                row = asdict(product)
                # Convert lists and dicts to strings for CSV
                row['image_urls'] = '; '.join(row['image_urls'])
                row['specifications'] = '; '.join([f"{k}: {v}" for k, v in row['specifications'].items()])
                row['keywords'] = '; '.join(row['keywords'])
                writer.writerow(row)
        
        logger.info(f"Exported {len(products)} products to {filename}")
    
    def export_to_json(self, products: List[Product], filename: str = "1688_products.json") -> None:
        """
        Export products to JSON file
        
        Args:
            products: List of Product objects
            filename: Output JSON filename
        """
        if not products:
            logger.warning("No products to export")
            return
        
        data = [asdict(product) for product in products]
        
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(data, jsonfile, indent=2, ensure_ascii=False)
        
        logger.info(f"Exported {len(products)} products to {filename}")

# Example usage and utility functions
def load_urls_from_file(filename: str) -> List[str]:
    """Load product URLs from a text file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip()]
        return urls
    except FileNotFoundError:
        logger.error(f"File {filename} not found")
        return []

def validate_1688_url(url: str) -> bool:
    """Validate if URL is a valid 1688 product URL"""
    return bool(re.match(r'https?://.*1688\.com.*', url))

if __name__ == "__main__":
    # Example usage
    parser = Alibaba1688Parser(delay_between_requests=1.5)
    
    # Example product URLs (replace with actual URLs)
    sample_urls = [
        "https://detail.1688.com/offer/123456789.html",
        "https://detail.1688.com/offer/987654321.html"
    ]
    
    # Filter valid URLs
    valid_urls = [url for url in sample_urls if validate_1688_url(url)]
    
    if valid_urls:
        # Scrape products
        products = parser.scrape_products(valid_urls)
        
        # Export results
        if products:
            parser.export_to_csv(products, "cargo_manager_products.csv")
            parser.export_to_json(products, "cargo_manager_products.json")
            
            print(f"Successfully scraped and exported {len(products)} products")
        else:
            print("No products were successfully scraped")
    else:
        print("No valid 1688 URLs provided")