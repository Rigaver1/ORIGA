# 1688 Product Parser for Cargo Manager

A comprehensive Python tool for extracting product information from 1688.com (Alibaba's wholesale platform) and optimizing the data for cargo management operations.

## Features

### 🚀 Core Functionality
- **Web Scraping**: Extract detailed product information from 1688 product pages
- **Data Processing**: Clean and normalize scraped data
- **Multiple Export Formats**: CSV, JSON, and Excel support
- **Cargo Optimization**: Transform data for logistics and cargo management
- **Bulk Processing**: Handle multiple products efficiently
- **Rate Limiting**: Respectful scraping with configurable delays

### 📊 Extracted Data Points
- Product ID, title, and description
- Pricing information (single price and ranges)
- Minimum order quantities
- Supplier details (name, location, rating)
- Product images and specifications
- Shipping information and categories
- Keywords and market analysis

### 🚛 Cargo Manager Integration
- **Risk Assessment**: Evaluate supplier and product risks
- **Profit Analysis**: Calculate estimated profit margins
- **Logistics Planning**: Recommend shipping methods and lead times
- **Customs Preparation**: Include HS codes and documentation requirements
- **Quality Grading**: Assess product and supplier quality
- **Market Intelligence**: Competition and demand analysis

## Installation

1. **Clone or download the files to your workspace**

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Optional: Install additional dependencies for advanced features:**
```bash
# For JavaScript-heavy pages
pip install selenium

# For advanced scraping
pip install scrapy playwright

# For CAPTCHA solving (if needed)
pip install anticaptcha
```

## Quick Start

### Basic Usage

```python
from alibaba_1688_parser import Alibaba1688Parser

# Initialize parser
parser = Alibaba1688Parser(delay_between_requests=1.5)

# Scrape a single product
product_url = "https://detail.1688.com/offer/123456789.html"
product = parser.scrape_product(product_url)

if product:
    print(f"Product: {product.title}")
    print(f"Price: {product.price}")
    print(f"Supplier: {product.supplier_name}")

# Export results
parser.export_to_csv([product], "products.csv")
parser.export_to_json([product], "products.json")
```

### Cargo Manager Integration

```python
from cargo_manager_integration import CargoManagerProcessor

# Process for cargo management
processor = CargoManagerProcessor()
cargo_products = processor.convert_to_cargo_products([product])

# Export cargo-optimized data
processor.export_cargo_csv(cargo_products, "cargo_products.csv")

# Generate analysis report
report = processor.generate_cargo_report(cargo_products)
print(f"Average profit margin: {report['summary']['average_profit_margin']}")
```

### Bulk Processing

```python
# Load URLs from file
from alibaba_1688_parser import load_urls_from_file

urls = load_urls_from_file("product_urls.txt")
products = parser.scrape_products(urls)

# Process all for cargo management
cargo_products = processor.convert_to_cargo_products(products)
processor.export_cargo_csv(cargo_products)
```

## Configuration

Edit `config.yaml` to customize behavior:

```yaml
scraping:
  delay_between_requests: 1.5
  timeout: 30
  max_retries: 3

cargo_manager:
  default_currency: "CNY"
  profit_margin_threshold: 0.15
  risk_assessment: true

export:
  default_format: "csv"
  include_images: true
```

## File Structure

```
workspace/
├── alibaba_1688_parser.py          # Main parser class
├── cargo_manager_integration.py    # Cargo management features
├── example_usage.py                # Usage examples
├── config.yaml                     # Configuration file
├── requirements.txt                # Dependencies
└── README.md                       # This file
```

## Data Output

### Standard Product Data
```csv
id,title,price,supplier_name,supplier_location,min_order_quantity,...
123456789,"Wireless Headphones","¥89.50","Audio Tech Co.","Shenzhen",50,...
```

### Cargo-Optimized Data
```csv
product_id,product_name,unit_price,profit_margin,risk_assessment,hs_code,...
123456789,"Wireless Headphones",89.50,0.25,"Medium risk","8517.12.00",...
```

## Advanced Features

### Custom Data Extraction

```python
# Extend the parser for custom fields
class CustomParser(Alibaba1688Parser):
    def extract_custom_field(self, html):
        # Your custom extraction logic
        return custom_data

parser = CustomParser()
```

### Proxy Support

```python
parser = Alibaba1688Parser()
parser.session.proxies = {
    'http': 'http://proxy:port',
    'https': 'https://proxy:port'
}
```

### Rate Limiting and Politeness

```python
# Respectful scraping
parser = Alibaba1688Parser(delay_between_requests=2.0)  # 2 second delay
```

## Cargo Manager Features

### Risk Assessment
- Supplier reliability scoring
- Product category risk analysis
- Customs complexity evaluation
- Market volatility assessment

### Logistics Optimization
- Shipping method recommendations
- Lead time estimation
- Storage requirement analysis
- Packaging specifications

### Business Intelligence
- Profit margin calculations
- Competition level analysis
- Market demand assessment
- Seasonal factor identification

## Error Handling

The parser includes comprehensive error handling:

- **Network errors**: Automatic retries with exponential backoff
- **Parsing errors**: Graceful degradation with partial data
- **Rate limiting**: Automatic delay adjustment
- **Invalid URLs**: Validation and filtering

## Legal and Ethical Considerations

⚠️ **Important**: Always comply with:
- 1688.com's Terms of Service
- Robots.txt guidelines
- Local and international laws
- Rate limiting and politeness policies

**Recommendations**:
- Use reasonable delays between requests
- Don't overload servers
- Respect intellectual property rights
- Obtain necessary permissions for commercial use

## Troubleshooting

### Common Issues

1. **No data extracted**:
   - Check if URL is valid and accessible
   - Verify internet connection
   - Check for CAPTCHA or anti-bot measures

2. **Slow performance**:
   - Increase delay between requests
   - Check network latency
   - Consider using proxies

3. **Missing dependencies**:
   ```bash
   pip install -r requirements.txt --upgrade
   ```

4. **Encoding issues**:
   - Ensure UTF-8 encoding in your environment
   - Check locale settings

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

parser = Alibaba1688Parser()
# Now you'll see detailed debug information
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Changelog

### Version 1.0.0
- Initial release
- Basic product scraping functionality
- Cargo manager integration
- CSV/JSON export capabilities
- Configuration system

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the example usage
3. Check configuration settings
4. Create an issue with detailed information

## Disclaimer

This tool is for educational and research purposes. Users are responsible for:
- Complying with website terms of service
- Respecting rate limits and server resources
- Following applicable laws and regulations
- Using scraped data ethically and legally

The authors are not responsible for misuse of this tool or any legal consequences arising from its use.