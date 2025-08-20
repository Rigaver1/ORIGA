# 1688 Product Parser & Cargo Manager

A comprehensive solution for scraping product information from Alibaba's 1688.com B2B platform and managing cargo imports efficiently.

## 🚀 Features

### Core Parser Features
- **Product Search**: Search products by keywords across multiple pages
- **Data Extraction**: Extract comprehensive product information including:
  - Product details (ID, title, description)
  - Pricing information
  - Supplier details and location
  - Minimum order quantities (MOQ)
  - Product specifications
  - Shipping and lead time information
  - Payment terms and certifications
  - Product ratings and reviews
- **Multiple Export Formats**: CSV, JSON, and Excel support
- **Rate Limiting**: Built-in delays to avoid being blocked
- **Error Handling**: Robust error handling and logging
- **Data Validation**: Validate extracted data for quality

### Cargo Manager Features
- **Modern Web Interface**: Beautiful, responsive web application
- **Product Catalog**: Display and organize scraped products
- **Advanced Filtering**: Filter by supplier, price, category, and more
- **Product Details**: Detailed view of each product with specifications
- **Statistics Dashboard**: Overview of products, suppliers, and values
- **Cargo Management**: Add products to cargo lists for import planning

## 📋 Requirements

### Python Dependencies
- Python 3.7+
- requests
- beautifulsoup4
- lxml
- urllib3
- certifi
- charset-normalizer
- soupsieve

### System Requirements
- Linux, macOS, or Windows
- Internet connection for web scraping
- Sufficient disk space for data storage

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd 1688-parser-cargo-manager
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify installation**
   ```bash
   python 1688_parser.py --help
   ```

## 🚀 Quick Start

### 1. Basic Usage

Run the parser with interactive prompts:
```bash
python 1688_parser.py
```

The script will prompt you for:
- Product keyword to search
- Maximum number of pages to search
- Output format preferences

### 2. Command Line Usage

```bash
# Search for LED products across 5 pages
python 1688_parser.py --keyword "LED lights" --pages 5

# Export to CSV format
python 1688_parser.py --keyword "phone cases" --format csv

# Search with specific category
python 1688_parser.py --keyword "sports shoes" --category "sports"
```

### 3. Web Interface

Open `cargo_manager.html` in your web browser to access the cargo management interface.

## 📊 Data Structure

### Product Information Extracted

```python
@dataclass
class ProductInfo:
    product_id: str              # Unique product identifier
    title: str                   # Product title/name
    price_range: str             # Price range (e.g., "¥2.50 - ¥3.20")
    min_order: str               # Minimum order quantity
    supplier: str                # Supplier company name
    supplier_location: str       # Supplier location
    product_url: str             # Product page URL
    image_url: str               # Product image URL
    category: str                # Product category
    specifications: Dict[str, str] # Product specifications
    description: str             # Product description
    rating: Optional[float]      # Product rating (1-5)
    review_count: Optional[int]  # Number of reviews
    moq: Optional[int]           # Minimum order quantity (numeric)
    unit: str                    # Unit of measurement
    shipping_info: str           # Shipping information
    lead_time: str               # Production/delivery lead time
    certification: List[str]     # Product certifications
    sample_available: bool       # Sample availability
    payment_terms: List[str]     # Accepted payment methods
    scraped_at: datetime         # Timestamp of data extraction
```

## 🔧 Configuration

### Main Configuration File (`config.py`)

The configuration file contains all customizable settings:

- **Request Settings**: Timeouts, retries, rate limiting
- **Search Parameters**: Page sizes, sort options
- **User Agents**: Browser identification strings
- **Export Options**: File formats, encoding
- **Quality Filters**: Minimum ratings, review counts
- **Performance Settings**: Concurrent requests, batch sizes

### Environment Variables

Set these environment variables for sensitive configuration:

```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=cargo_manager
export DB_USER=cargo_user
export DB_PASSWORD=your_password
export HTTP_PROXY=http://proxy:port
export HTTPS_PROXY=https://proxy:port
```

## 📁 File Structure

```
1688-parser-cargo-manager/
├── 1688_parser.py          # Main parser script
├── cargo_manager.html      # Web interface
├── config.py              # Configuration file
├── utils.py               # Utility functions
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── output/               # Generated output files
├── logs/                 # Log files
└── .cache/              # Cache directory
```

## 🌐 Web Interface Usage

### 1. Open the Interface
- Open `cargo_manager.html` in your web browser
- The interface will load with sample data for demonstration

### 2. Search Products
- Enter product keywords in the search field
- Select maximum pages to search
- Choose product category (optional)
- Click "Search Products" to start scraping

### 3. Filter and Organize
- Use the search filter to find specific products
- Filter by supplier, price range, or category
- Sort products by various criteria

### 4. Product Management
- View detailed product information
- Add products to your cargo list
- Export data in various formats

## 📈 Advanced Features

### 1. Custom Extraction Rules

Modify `config.py` to customize extraction patterns:

```python
CUSTOM_EXTRACTION_RULES = {
    'price_patterns': [
        r'¥([\d,]+\.?\d*)',
        r'(\d+\.?\d*)\s*元',
        r'(\d+\.?\d*)\s*RMB'
    ],
    'moq_patterns': [
        r'最小起订量[：:]\s*(\d+)',
        r'MOQ[：:]\s*(\d+)'
    ]
}
```

### 2. Data Validation

Enable data validation in configuration:

```python
VALIDATE_PRODUCT_DATA = True
REQUIRED_FIELDS = ['product_id', 'title', 'price_range', 'supplier']
```

### 3. Caching

Enable caching to improve performance:

```python
CACHE_ENABLED = True
CACHE_EXPIRY = 3600  # 1 hour
```

## 🔒 Security and Ethics

### Rate Limiting
- Built-in delays between requests
- Random delays to avoid detection
- Configurable request limits

### User Agent Rotation
- Multiple browser identification strings
- Automatic rotation to avoid blocking

### Respectful Scraping
- Follows robots.txt guidelines
- Implements reasonable delays
- Respects website terms of service

## 📊 Output Formats

### 1. CSV Export
- Comma-separated values
- UTF-8 encoding
- All product fields included
- Suitable for Excel import

### 2. JSON Export
- Structured data format
- Easy to process programmatically
- Includes metadata and timestamps
- Human-readable format

### 3. Excel Export (Future)
- Multi-sheet workbook
- Formatted tables
- Charts and statistics
- Professional presentation

## 🚨 Troubleshooting

### Common Issues

1. **Connection Errors**
   - Check internet connection
   - Verify proxy settings if using
   - Increase timeout values in config

2. **Parsing Errors**
   - Check if website structure changed
   - Update extraction patterns
   - Enable debug logging

3. **Rate Limiting**
   - Increase delays between requests
   - Reduce concurrent requests
   - Use proxy rotation

### Debug Mode

Enable debug mode in configuration:

```python
DEBUG_MODE = True
VERBOSE_LOGGING = True
SAVE_HTML_SNAPSHOTS = True
```

## 📝 Logging

### Log Levels
- **INFO**: General operation information
- **WARNING**: Non-critical issues
- **ERROR**: Critical errors and failures
- **DEBUG**: Detailed debugging information

### Log Files
- Main log: `1688_parser.log`
- Rotating log files
- Configurable log retention

## 🔄 API Integration

### Future API Endpoints

```python
# Search products
POST /api/search
{
    "keyword": "LED lights",
    "max_pages": 5,
    "category": "electronics"
}

# Get product details
GET /api/products/{product_id}

# Export data
GET /api/export?format=csv&filters={...}
```

## 🤝 Contributing

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Add docstrings to functions
- Include error handling

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This tool is for educational and legitimate business purposes only. Users are responsible for:

- Complying with website terms of service
- Respecting rate limits and robots.txt
- Using data in accordance with applicable laws
- Obtaining necessary permissions for commercial use

## 🆘 Support

### Getting Help

1. Check the troubleshooting section
2. Review the configuration options
3. Enable debug logging
4. Check the log files for errors

### Reporting Issues

When reporting issues, please include:

- Python version
- Operating system
- Error messages and logs
- Steps to reproduce
- Configuration settings

## 🔮 Future Enhancements

### Planned Features

- **Database Integration**: PostgreSQL/MySQL support
- **Real-time Monitoring**: Live scraping status
- **Advanced Analytics**: Product trend analysis
- **Supplier Management**: Supplier database and ratings
- **Order Management**: Purchase order tracking
- **Cost Calculator**: Import cost estimation
- **Multi-language Support**: Chinese, English, and more
- **Mobile App**: iOS and Android applications

### Performance Improvements

- **Async Scraping**: Concurrent request handling
- **Distributed Scraping**: Multiple server support
- **Smart Caching**: Intelligent data caching
- **Load Balancing**: Request distribution

---

**Happy Scraping! 🚀**

For questions and support, please refer to the documentation or create an issue in the repository.