#!/usr/bin/env python3
"""
Utility functions for 1688 Product Parser
Common helper functions and utilities
"""

import re
import json
import csv
import os
import time
import random
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse, parse_qs
import hashlib
import pickle
from pathlib import Path

def setup_logging(log_level: str = "INFO", log_file: str = "1688_parser.log") -> logging.Logger:
    """Setup logging configuration"""
    logger = logging.getLogger("1688_parser")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File handler
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

def clean_text(text: str) -> str:
    """Clean and normalize text content"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove special characters that might cause issues
    text = re.sub(r'[^\w\s\-\.\,\¥\(\)\#\@\&\+\=\:\;\"\']', '', text)
    
    return text

def extract_price(text: str) -> Optional[float]:
    """Extract price from text"""
    if not text:
        return None
    
    # Common price patterns
    price_patterns = [
        r'¥([\d,]+\.?\d*)',
        r'(\d+\.?\d*)\s*元',
        r'(\d+\.?\d*)\s*RMB',
        r'(\d+\.?\d*)\s*USD',
        r'(\d+\.?\d*)\s*\$'
    ]
    
    for pattern in price_patterns:
        match = re.search(pattern, text)
        if match:
            try:
                price_str = match.group(1).replace(',', '')
                return float(price_str)
            except (ValueError, AttributeError):
                continue
    
    return None

def extract_number(text: str) -> Optional[int]:
    """Extract number from text"""
    if not text:
        return None
    
    match = re.search(r'(\d+)', text)
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            return None
    
    return None

def extract_rating(text: str) -> Optional[float]:
    """Extract rating from text"""
    if not text:
        return None
    
    # Look for rating patterns like "4.5", "4.5/5", "4.5 out of 5"
    rating_patterns = [
        r'(\d+\.?\d*)\s*\/\s*5',
        r'(\d+\.?\d*)\s*out\s*of\s*5',
        r'(\d+\.?\d*)\s*stars?',
        r'(\d+\.?\d*)'
    ]
    
    for pattern in rating_patterns:
        match = re.search(pattern, text)
        if match:
            try:
                rating = float(match.group(1))
                if 0 <= rating <= 5:
                    return rating
            except ValueError:
                continue
    
    return None

def extract_moq(text: str) -> Optional[int]:
    """Extract minimum order quantity from text"""
    if not text:
        return None
    
    moq_patterns = [
        r'最小起订量[：:]\s*(\d+)',
        r'MOQ[：:]\s*(\d+)',
        r'起订量[：:]\s*(\d+)',
        r'最少(\d+)',
        r'(\d+)\s*pieces?',
        r'(\d+)\s*件'
    ]
    
    for pattern in moq_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                continue
    
    return None

def extract_supplier_info(text: str) -> Dict[str, str]:
    """Extract supplier information from text"""
    supplier_info = {}
    
    if not text:
        return supplier_info
    
    # Extract company name
    company_patterns = [
        r'公司[：:]\s*([^\n\r]+)',
        r'Company[：:]\s*([^\n\r]+)',
        r'供应商[：:]\s*([^\n\r]+)',
        r'Supplier[：:]\s*([^\n\r]+)'
    ]
    
    for pattern in company_patterns:
        match = re.search(pattern, text)
        if match:
            supplier_info['name'] = clean_text(match.group(1))
            break
    
    # Extract location
    location_patterns = [
        r'地区[：:]\s*([^\n\r]+)',
        r'Location[：:]\s*([^\n\r]+)',
        r'地址[：:]\s*([^\n\r]+)',
        r'Address[：:]\s*([^\n\r]+)'
    ]
    
    for pattern in location_patterns:
        match = re.search(pattern, text)
        if match:
            supplier_info['location'] = clean_text(match.group(1))
            break
    
    return supplier_info

def extract_specifications(soup_text: str) -> Dict[str, str]:
    """Extract product specifications from text"""
    specs = {}
    
    if not soup_text:
        return specs
    
    # Look for specification patterns
    spec_patterns = [
        r'([^：:]+)[：:]\s*([^\n\r]+)',
        r'([^:]+):\s*([^\n\r]+)'
    ]
    
    for pattern in spec_patterns:
        matches = re.findall(pattern, soup_text)
        for key, value in matches:
            key = clean_text(key)
            value = clean_text(value)
            if key and value and len(key) < 50 and len(value) < 200:
                specs[key] = value
    
    return specs

def extract_certifications(text: str) -> List[str]:
    """Extract certification information from text"""
    if not text:
        return []
    
    # Common certifications
    cert_patterns = [
        r'ISO\s*\d+',
        r'CE\s*认证?',
        r'FDA\s*认证?',
        r'RoHS\s*认证?',
        r'FCC\s*认证?',
        r'UL\s*认证?',
        r'CCC\s*认证?'
    ]
    
    certifications = []
    for pattern in cert_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        certifications.extend(matches)
    
    return list(set(certifications))

def extract_payment_terms(text: str) -> List[str]:
    """Extract payment terms from text"""
    if not text:
        return []
    
    # Common payment terms
    payment_terms = [
        'T/T', 'L/C', 'D/P', 'D/A', 'PayPal', 'Alipay', 'WeChat Pay',
        'Western Union', 'MoneyGram', 'Credit Card', 'Bank Transfer'
    ]
    
    found_terms = []
    for term in payment_terms:
        if re.search(rf'\b{re.escape(term)}\b', text, re.IGNORECASE):
            found_terms.append(term)
    
    return found_terms

def extract_shipping_info(text: str) -> str:
    """Extract shipping information from text"""
    if not text:
        return "Shipping info not available"
    
    shipping_patterns = [
        r'运费[：:]\s*([^\n\r]+)',
        r'Shipping[：:]\s*([^\n\r]+)',
        r'Delivery[：:]\s*([^\n\r]+)',
        r'运输[：:]\s*([^\n\r]+)'
    ]
    
    for pattern in shipping_patterns:
        match = re.search(pattern, text)
        if match:
            return clean_text(match.group(1))
    
    return "Shipping info not available"

def extract_lead_time(text: str) -> str:
    """Extract lead time information from text"""
    if not text:
        return "Lead time not specified"
    
    lead_time_patterns = [
        r'交期[：:]\s*([^\n\r]+)',
        r'Lead\s*time[：:]\s*([^\n\r]+)',
        r'Delivery\s*time[：:]\s*([^\n\r]+)',
        r'生产周期[：:]\s*([^\n\r]+)'
    ]
    
    for pattern in lead_time_patterns:
        match = re.search(pattern, text)
        if match:
            return clean_text(match.group(1))
    
    return "Lead time not specified"

def is_valid_url(url: str) -> bool:
    """Check if URL is valid"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def normalize_url(url: str, base_url: str = "https://1688.com") -> str:
    """Normalize URL to absolute URL"""
    if not url:
        return ""
    
    if url.startswith('http'):
        return url
    elif url.startswith('//'):
        return f"https:{url}"
    elif url.startswith('/'):
        return urljoin(base_url, url)
    else:
        return urljoin(base_url, f"/{url}")

def generate_filename(prefix: str, extension: str = "txt") -> str:
    """Generate filename with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.{extension}"

def ensure_directory(directory: str) -> None:
    """Ensure directory exists, create if it doesn't"""
    Path(directory).mkdir(parents=True, exist_ok=True)

def save_to_file(data: Any, filename: str, format_type: str = "json") -> bool:
    """Save data to file in specified format"""
    try:
        ensure_directory(os.path.dirname(filename) if os.path.dirname(filename) else ".")
        
        if format_type.lower() == "json":
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        
        elif format_type.lower() == "csv":
            if isinstance(data, list) and data:
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
            else:
                return False
        
        elif format_type.lower() == "txt":
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(str(data))
        
        else:
            return False
        
        return True
    
    except Exception as e:
        logging.error(f"Error saving file {filename}: {e}")
        return False

def load_from_file(filename: str, format_type: str = "json") -> Any:
    """Load data from file in specified format"""
    try:
        if not os.path.exists(filename):
            return None
        
        if format_type.lower() == "json":
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        elif format_type.lower() == "csv":
            with open(filename, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                return list(reader)
        
        elif format_type.lower() == "txt":
            with open(filename, 'r', encoding='utf-8') as f:
                return f.read()
        
        else:
            return None
    
    except Exception as e:
        logging.error(f"Error loading file {filename}: {e}")
        return None

def cache_data(data: Any, cache_key: str, cache_dir: str = ".cache") -> bool:
    """Cache data to file"""
    try:
        ensure_directory(cache_dir)
        cache_file = os.path.join(cache_dir, f"{cache_key}.pkl")
        
        with open(cache_file, 'wb') as f:
            pickle.dump(data, f)
        
        return True
    
    except Exception as e:
        logging.error(f"Error caching data: {e}")
        return False

def load_cached_data(cache_key: str, cache_dir: str = ".cache", max_age_hours: int = 24) -> Any:
    """Load cached data from file"""
    try:
        cache_file = os.path.join(cache_dir, f"{cache_key}.pkl")
        
        if not os.path.exists(cache_file):
            return None
        
        # Check if cache is expired
        file_age = time.time() - os.path.getmtime(cache_file)
        if file_age > (max_age_hours * 3600):
            os.remove(cache_file)
            return None
        
        with open(cache_file, 'rb') as f:
            return pickle.load(f)
    
    except Exception as e:
        logging.error(f"Error loading cached data: {e}")
        return None

def generate_cache_key(*args) -> str:
    """Generate cache key from arguments"""
    key_string = "_".join(str(arg) for arg in args)
    return hashlib.md5(key_string.encode()).hexdigest()

def format_price(price: float, currency: str = "¥") -> str:
    """Format price with currency symbol"""
    if price is None:
        return "Price not available"
    
    try:
        return f"{currency}{price:.2f}"
    except:
        return "Price not available"

def format_quantity(quantity: int, unit: str = "piece") -> str:
    """Format quantity with unit"""
    if quantity is None:
        return "Quantity not specified"
    
    try:
        return f"{quantity} {unit}{'s' if quantity != 1 else ''}"
    except:
        return "Quantity not specified"

def calculate_total_value(products: List[Dict], price_field: str = "price_range") -> float:
    """Calculate total value of products"""
    total = 0.0
    count = 0
    
    for product in products:
        price = extract_price(product.get(price_field, ""))
        if price:
            total += price
            count += 1
    
    return total if count > 0 else 0.0

def filter_products_by_criteria(products: List[Dict], **criteria) -> List[Dict]:
    """Filter products by various criteria"""
    filtered = products
    
    # Filter by price range
    if 'min_price' in criteria and criteria['min_price'] is not None:
        filtered = [p for p in filtered if extract_price(p.get('price_range', '')) >= criteria['min_price']]
    
    if 'max_price' in criteria and criteria['max_price'] is not None:
        filtered = [p for p in filtered if extract_price(p.get('price_range', '')) <= criteria['max_price']]
    
    # Filter by rating
    if 'min_rating' in criteria and criteria['min_rating'] is not None:
        filtered = [p for p in filtered if p.get('rating', 0) >= criteria['min_rating']]
    
    # Filter by MOQ
    if 'max_moq' in criteria and criteria['max_moq'] is not None:
        filtered = [p for p in filtered if p.get('moq', float('inf')) <= criteria['max_moq']]
    
    # Filter by supplier location
    if 'supplier_location' in criteria and criteria['supplier_location']:
        location = criteria['supplier_location'].lower()
        filtered = [p for p in filtered if location in p.get('supplier_location', '').lower()]
    
    return filtered

def sort_products(products: List[Dict], sort_by: str = "price", reverse: bool = False) -> List[Dict]:
    """Sort products by specified field"""
    if not products:
        return products
    
    def get_sort_key(product):
        if sort_by == "price":
            return extract_price(product.get('price_range', '')) or 0
        elif sort_by == "rating":
            return product.get('rating', 0) or 0
        elif sort_by == "moq":
            return product.get('moq', float('inf')) or float('inf')
        elif sort_by == "review_count":
            return product.get('review_count', 0) or 0
        else:
            return 0
    
    return sorted(products, key=get_sort_key, reverse=reverse)

def create_summary_report(products: List[Dict]) -> Dict[str, Any]:
    """Create summary report of products"""
    if not products:
        return {}
    
    total_products = len(products)
    unique_suppliers = len(set(p.get('supplier', '') for p in products))
    
    # Calculate average price
    total_price = 0
    price_count = 0
    for product in products:
        price = extract_price(product.get('price_range', ''))
        if price:
            total_price += price
            price_count += 1
    
    avg_price = total_price / price_count if price_count > 0 else 0
    
    # Calculate average rating
    total_rating = 0
    rating_count = 0
    for product in products:
        rating = product.get('rating')
        if rating:
            total_rating += rating
            rating_count += 1
    
    avg_rating = total_rating / rating_count if rating_count > 0 else 0
    
    # Count by category
    categories = {}
    for product in products:
        category = product.get('category', 'Unknown')
        categories[category] = categories.get(category, 0) + 1
    
    return {
        'total_products': total_products,
        'unique_suppliers': unique_suppliers,
        'average_price': round(avg_price, 2),
        'average_rating': round(avg_rating, 2),
        'categories': categories,
        'generated_at': datetime.now().isoformat()
    }

def validate_product_data(product: Dict) -> Dict[str, Any]:
    """Validate product data and return validation results"""
    validation_result = {
        'is_valid': True,
        'errors': [],
        'warnings': []
    }
    
    required_fields = ['product_id', 'title', 'price_range', 'supplier']
    
    # Check required fields
    for field in required_fields:
        if not product.get(field):
            validation_result['is_valid'] = False
            validation_result['errors'].append(f"Missing required field: {field}")
    
    # Check data types and formats
    if product.get('rating') and not isinstance(product['rating'], (int, float)):
        validation_result['warnings'].append("Rating should be a number")
    
    if product.get('moq') and not isinstance(product['moq'], int):
        validation_result['warnings'].append("MOQ should be an integer")
    
    # Check URL format
    if product.get('product_url') and not is_valid_url(product['product_url']):
        validation_result['warnings'].append("Invalid product URL format")
    
    return validation_result