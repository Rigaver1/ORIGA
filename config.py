#!/usr/bin/env python3
"""
Configuration file for 1688 Product Parser
Contains settings, constants, and configuration options
"""

import os
from typing import Dict, List

# Base URLs
BASE_URL = "https://1688.com"
SEARCH_URL = "https://s.1688.com/selloffer/offer_search.htm"

# Request settings
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3
RETRY_DELAY = 5

# Rate limiting
MIN_DELAY_BETWEEN_REQUESTS = 1  # seconds
MAX_DELAY_BETWEEN_REQUESTS = 3  # seconds
DELAY_BETWEEN_PAGES = 2  # seconds

# Search parameters
DEFAULT_PAGE_SIZE = 40
MAX_PAGES_PER_SEARCH = 20
DEFAULT_SORT_TYPE = "pop"  # popular

# User agent strings (rotate to avoid detection)
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'
]

# Headers for requests
DEFAULT_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0',
    'TE': 'Trailers',
}

# Product categories for filtering
PRODUCT_CATEGORIES = {
    'electronics': ['电子', 'Electronics', '数码', 'Digital'],
    'clothing': ['服装', 'Clothing', '纺织', 'Textile', '鞋帽', 'Shoes'],
    'home': ['家居', 'Home', '家具', 'Furniture', '装饰', 'Decoration'],
    'automotive': ['汽车', 'Automotive', '配件', 'Parts', '用品', 'Accessories'],
    'beauty': ['美容', 'Beauty', '护肤', 'Skincare', '化妆', 'Makeup'],
    'sports': ['运动', 'Sports', '户外', 'Outdoor', '健身', 'Fitness'],
    'toys': ['玩具', 'Toys', '游戏', 'Games', '模型', 'Models'],
    'jewelry': ['珠宝', 'Jewelry', '首饰', 'Accessories', '手表', 'Watches'],
    'food': ['食品', 'Food', '饮料', 'Beverages', '零食', 'Snacks'],
    'health': ['健康', 'Health', '医疗', 'Medical', '保健', 'Healthcare']
}

# Price ranges for filtering
PRICE_RANGES = {
    'budget': (0, 100),
    'mid_range': (100, 500),
    'premium': (500, 1000),
    'luxury': (1000, float('inf'))
}

# Minimum order quantity ranges
MOQ_RANGES = {
    'low': (1, 50),
    'medium': (50, 200),
    'high': (200, 1000),
    'bulk': (1000, float('inf'))
}

# Supplier location preferences
SUPPLIER_LOCATIONS = [
    'Guangdong', 'Zhejiang', 'Jiangsu', 'Shandong', 'Fujian',
    'Henan', 'Sichuan', 'Hunan', 'Hubei', 'Anhui'
]

# Product specifications to extract
SPECIFICATION_KEYS = [
    'Brand', 'Model', 'Material', 'Size', 'Weight', 'Color',
    'Power', 'Voltage', 'Capacity', 'Dimensions', 'Package',
    'Origin', 'Warranty', 'Certification', 'Features'
]

# Payment terms to look for
PAYMENT_TERMS = [
    'T/T', 'L/C', 'D/P', 'D/A', 'PayPal', 'Alipay', 'WeChat Pay',
    'Western Union', 'MoneyGram', 'Credit Card', 'Bank Transfer'
]

# Shipping methods to extract
SHIPPING_METHODS = [
    'FOB', 'CIF', 'EXW', 'DDP', 'DDU', 'Express', 'Air Freight',
    'Sea Freight', 'Rail Freight', 'Land Freight'
]

# File output settings
OUTPUT_DIRECTORY = "output"
CSV_ENCODING = "utf-8"
JSON_INDENT = 2

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = "1688_parser.log"
LOG_MAX_SIZE = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5

# Database settings (if using database)
DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'cargo_manager'),
    'user': os.getenv('DB_USER', 'cargo_user'),
    'password': os.getenv('DB_PASSWORD', ''),
}

# API settings (if using external APIs)
API_CONFIG = {
    'timeout': 30,
    'max_retries': 3,
    'rate_limit': 100,  # requests per hour
}

# Proxy settings (if using proxies)
PROXY_CONFIG = {
    'enabled': False,
    'proxies': {
        'http': os.getenv('HTTP_PROXY', ''),
        'https': os.getenv('HTTPS_PROXY', ''),
    },
    'rotate_proxies': False,
    'proxy_list_file': 'proxies.txt'
}

# Export settings
EXPORT_FORMATS = ['csv', 'json', 'excel']
EXPORT_INCLUDE_IMAGES = False
EXPORT_COMPRESS = False

# Quality filters
MIN_RATING = 3.0
MIN_REVIEW_COUNT = 10
MAX_LEAD_TIME_DAYS = 60

# Sample data settings
SAMPLE_DATA_ENABLED = True
SAMPLE_DATA_COUNT = 10

# Error handling
IGNORE_SSL_ERRORS = False
FOLLOW_REDIRECTS = True
MAX_REDIRECTS = 5

# Cache settings
CACHE_ENABLED = True
CACHE_EXPIRY = 3600  # 1 hour
CACHE_DIRECTORY = ".cache"

# Notification settings
NOTIFICATIONS_ENABLED = False
EMAIL_NOTIFICATIONS = False
SLACK_NOTIFICATIONS = False

# Performance settings
MAX_CONCURRENT_REQUESTS = 5
REQUEST_TIMEOUT_PER_REQUEST = 10
BATCH_SIZE = 100

# Data validation
VALIDATE_PRODUCT_DATA = True
REQUIRED_FIELDS = ['product_id', 'title', 'price_range', 'supplier']
OPTIONAL_FIELDS = ['description', 'specifications', 'rating', 'review_count']

# Custom extraction rules
CUSTOM_EXTRACTION_RULES = {
    'price_patterns': [
        r'¥([\d,]+\.?\d*)',
        r'(\d+\.?\d*)\s*元',
        r'(\d+\.?\d*)\s*RMB'
    ],
    'moq_patterns': [
        r'最小起订量[：:]\s*(\d+)',
        r'MOQ[：:]\s*(\d+)',
        r'起订量[：:]\s*(\d+)'
    ],
    'supplier_patterns': [
        r'供应商[：:]\s*([^\n\r]+)',
        r'Supplier[：:]\s*([^\n\r]+)',
        r'公司[：:]\s*([^\n\r]+)'
    ]
}

# Export templates
CSV_TEMPLATE = {
    'delimiter': ',',
    'quotechar': '"',
    'quoting': 1,  # csv.QUOTE_ALL
    'lineterminator': '\n'
}

JSON_TEMPLATE = {
    'ensure_ascii': False,
    'indent': 2,
    'separators': (',', ': '),
    'sort_keys': True
}

# Report settings
REPORT_TEMPLATE = 'default'
REPORT_INCLUDE_CHARTS = True
REPORT_FORMAT = 'html'
REPORT_SAVE_PATH = 'reports'

# Backup settings
BACKUP_ENABLED = True
BACKUP_INTERVAL = 24  # hours
BACKUP_RETENTION = 7  # days
BACKUP_DIRECTORY = 'backups'

# Security settings
ENCRYPT_SENSITIVE_DATA = False
API_KEY_ENCRYPTION = False
LOG_SENSITIVE_DATA = False

# Development settings
DEBUG_MODE = False
VERBOSE_LOGGING = False
SAVE_HTML_SNAPSHOTS = False
TEST_MODE = False