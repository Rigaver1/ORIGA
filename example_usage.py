#!/usr/bin/env python3
"""
Example Usage Script for 1688 Product Parser
Demonstrates how to use the parser and cargo manager integration
"""

import os
import sys
import json
from typing import List
import logging

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from alibaba_1688_parser import Alibaba1688Parser, Product, load_urls_from_file, validate_1688_url
from cargo_manager_integration import CargoManagerProcessor, CargoProduct

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def example_single_product():
    """Example: Scrape a single product"""
    print("=== Single Product Scraping Example ===")
    
    # Initialize parser
    parser = Alibaba1688Parser(delay_between_requests=1.0)
    
    # Example URL (replace with actual 1688 product URL)
    product_url = "https://detail.1688.com/offer/123456789.html"
    
    print(f"Scraping product: {product_url}")
    
    # Scrape the product
    product = parser.scrape_product(product_url)
    
    if product:
        print(f"✓ Successfully scraped: {product.title}")
        print(f"  Price: {product.price}")
        print(f"  Supplier: {product.supplier_name}")
        print(f"  Location: {product.supplier_location}")
        print(f"  Min Order: {product.min_order_quantity}")
        
        # Export to files
        parser.export_to_json([product], "single_product.json")
        parser.export_to_csv([product], "single_product.csv")
        
        print("✓ Exported to single_product.json and single_product.csv")
    else:
        print("✗ Failed to scrape product")

def example_multiple_products():
    """Example: Scrape multiple products"""
    print("\n=== Multiple Products Scraping Example ===")
    
    # Initialize parser
    parser = Alibaba1688Parser(delay_between_requests=1.5)
    
    # Example URLs (replace with actual 1688 product URLs)
    product_urls = [
        "https://detail.1688.com/offer/123456789.html",
        "https://detail.1688.com/offer/987654321.html",
        "https://detail.1688.com/offer/456789123.html"
    ]
    
    print(f"Scraping {len(product_urls)} products...")
    
    # Filter valid URLs
    valid_urls = [url for url in product_urls if validate_1688_url(url)]
    print(f"Valid URLs: {len(valid_urls)}")
    
    # Scrape products
    products = parser.scrape_products(valid_urls)
    
    if products:
        print(f"✓ Successfully scraped {len(products)} products")
        
        # Export results
        parser.export_to_json(products, "multiple_products.json")
        parser.export_to_csv(products, "multiple_products.csv")
        
        print("✓ Exported to multiple_products.json and multiple_products.csv")
        
        # Display summary
        for i, product in enumerate(products, 1):
            print(f"  {i}. {product.title[:50]}... - {product.price}")
    else:
        print("✗ No products were successfully scraped")

def example_cargo_manager_integration():
    """Example: Use cargo manager integration"""
    print("\n=== Cargo Manager Integration Example ===")
    
    # Initialize components
    parser = Alibaba1688Parser()
    cargo_processor = CargoManagerProcessor()
    
    # Create sample products (normally you'd scrape these)
    sample_products = create_sample_products()
    
    print(f"Processing {len(sample_products)} products for cargo management...")
    
    # Convert to cargo-optimized format
    cargo_products = cargo_processor.convert_to_cargo_products(sample_products)
    
    if cargo_products:
        print(f"✓ Processed {len(cargo_products)} products for cargo management")
        
        # Export cargo-optimized data
        cargo_processor.export_cargo_csv(cargo_products, "cargo_products.csv")
        print("✓ Exported to cargo_products.csv")
        
        # Generate analysis report
        report = cargo_processor.generate_cargo_report(cargo_products)
        
        # Save report
        with open("cargo_analysis_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print("✓ Generated cargo_analysis_report.json")
        
        # Display key insights
        print("\n--- Cargo Analysis Summary ---")
        print(f"Total Products: {report['summary']['total_products']}")
        print(f"Average Profit Margin: {report['summary']['average_profit_margin']}")
        
        print("\nTop Categories:")
        for category, count in sorted(report['category_breakdown'].items(), 
                                    key=lambda x: x[1], reverse=True)[:3]:
            print(f"  {category}: {count} products")
        
        print("\nRecommendations:")
        for rec in report['recommendations']:
            print(f"  • {rec}")
    else:
        print("✗ Failed to process products for cargo management")

def example_from_url_file():
    """Example: Load URLs from file and scrape"""
    print("\n=== Scraping from URL File Example ===")
    
    # Create sample URL file
    sample_urls = [
        "https://detail.1688.com/offer/123456789.html",
        "https://detail.1688.com/offer/987654321.html",
        "# This is a comment line",
        "https://detail.1688.com/offer/456789123.html"
    ]
    
    # Write sample URLs to file
    with open("product_urls.txt", "w") as f:
        f.write("\n".join(sample_urls))
    
    print("✓ Created sample product_urls.txt file")
    
    # Load URLs from file
    urls = load_urls_from_file("product_urls.txt")
    print(f"Loaded {len(urls)} URLs from file")
    
    # Initialize parser and scrape
    parser = Alibaba1688Parser()
    products = parser.scrape_products(urls)
    
    if products:
        print(f"✓ Scraped {len(products)} products from URL file")
        parser.export_to_csv(products, "url_file_products.csv")
        print("✓ Exported to url_file_products.csv")
    else:
        print("✗ No products scraped from URL file")

def create_sample_products() -> List[Product]:
    """Create sample products for demonstration"""
    from datetime import datetime
    
    return [
        Product(
            id="123456789",
            title="Wireless Bluetooth Headphones Premium Quality",
            price="¥89.50",
            price_range="¥85.00 - ¥95.00",
            min_order_quantity="50",
            supplier_name="Shenzhen Audio Tech Co., Ltd.",
            supplier_location="Shenzhen, Guangdong",
            supplier_rating="4.7",
            product_url="https://detail.1688.com/offer/123456789.html",
            image_urls=["https://example.com/image1.jpg", "https://example.com/image2.jpg"],
            description="High-quality wireless Bluetooth headphones with noise cancellation",
            specifications={"Material": "ABS Plastic", "Weight": "250g", "Battery": "500mAh"},
            shipping_info="Free shipping for orders over ¥500",
            category="Electronics",
            keywords=["wireless", "bluetooth", "headphones", "audio", "premium"],
            scraped_at=datetime.now().isoformat()
        ),
        Product(
            id="987654321",
            title="Cotton T-Shirt Wholesale Blank Apparel",
            price="¥12.80",
            price_range="¥10.50 - ¥15.00",
            min_order_quantity="100",
            supplier_name="Guangzhou Textile Manufacturing",
            supplier_location="Guangzhou, Guangdong",
            supplier_rating="4.2",
            product_url="https://detail.1688.com/offer/987654321.html",
            image_urls=["https://example.com/tshirt1.jpg"],
            description="100% cotton t-shirt, various colors available",
            specifications={"Material": "100% Cotton", "Weight": "180g", "Sizes": "S-XXL"},
            shipping_info="Sea freight available",
            category="Textiles",
            keywords=["cotton", "t-shirt", "apparel", "wholesale", "blank"],
            scraped_at=datetime.now().isoformat()
        )
    ]

def demonstrate_data_validation():
    """Example: Data validation features"""
    print("\n=== Data Validation Example ===")
    
    # Create products with various data quality issues
    products = create_sample_products()
    
    # Add a product with issues for demonstration
    from datetime import datetime
    problematic_product = Product(
        id="",  # Missing ID
        title="X",  # Too short title
        price="Invalid Price",  # Invalid price format
        price_range="",
        min_order_quantity="abc",  # Invalid quantity
        supplier_name="",  # Missing supplier
        supplier_location="Unknown",
        supplier_rating="N/A",
        product_url="invalid-url",
        image_urls=[],
        description="",  # Empty description
        specifications={},
        shipping_info="",
        category="",
        keywords=[],
        scraped_at=datetime.now().isoformat()
    )
    
    products.append(problematic_product)
    
    print(f"Validating {len(products)} products...")
    
    # Simple validation function
    def validate_product(product: Product) -> List[str]:
        issues = []
        
        if not product.id or len(product.id) < 3:
            issues.append("Invalid or missing product ID")
        
        if not product.title or len(product.title) < 5:
            issues.append("Title too short or missing")
        
        if not any(char.isdigit() for char in product.price):
            issues.append("Invalid price format")
        
        if not product.supplier_name:
            issues.append("Missing supplier name")
        
        if not product.image_urls:
            issues.append("No product images")
        
        return issues
    
    # Validate products
    valid_products = []
    for i, product in enumerate(products):
        issues = validate_product(product)
        if issues:
            print(f"Product {i+1} has issues:")
            for issue in issues:
                print(f"  ⚠ {issue}")
        else:
            print(f"Product {i+1}: ✓ Valid")
            valid_products.append(product)
    
    print(f"\nValidation complete: {len(valid_products)}/{len(products)} products are valid")

def main():
    """Main function demonstrating all features"""
    print("1688 Product Parser - Example Usage")
    print("=" * 50)
    
    try:
        # Run examples
        example_single_product()
        example_multiple_products()
        example_cargo_manager_integration()
        example_from_url_file()
        demonstrate_data_validation()
        
        print("\n" + "=" * 50)
        print("All examples completed successfully!")
        print("\nGenerated files:")
        print("  • single_product.json/csv")
        print("  • multiple_products.json/csv")
        print("  • cargo_products.csv")
        print("  • cargo_analysis_report.json")
        print("  • url_file_products.csv")
        print("  • product_urls.txt")
        
    except Exception as e:
        logger.error(f"Error running examples: {str(e)}")
        print(f"\n✗ Error: {str(e)}")

if __name__ == "__main__":
    main()