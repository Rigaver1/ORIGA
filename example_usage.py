#!/usr/bin/env python3
"""
Example usage of the 1688 Product Parser
Demonstrates various ways to use the parser for different scenarios
"""

import json
import time
from datetime import datetime
from 1688_parser import Alibaba1688Parser, ProductInfo
from utils import (
    filter_products_by_criteria, 
    sort_products, 
    create_summary_report,
    validate_product_data,
    save_to_file
)

def example_basic_search():
    """Basic product search example"""
    print("=== Basic Product Search Example ===")
    
    parser = Alibaba1688Parser()
    
    # Search for LED products
    keyword = "LED strip lights"
    max_pages = 3
    
    print(f"Searching for '{keyword}' across {max_pages} pages...")
    
    # Get product URLs
    product_urls = parser.search_products(keyword, max_pages)
    print(f"Found {len(product_urls)} product URLs")
    
    # Parse first 5 products (for demo purposes)
    products = []
    for i, url in enumerate(product_urls[:5]):
        print(f"Parsing product {i+1}/5...")
        product_info = parser.parse_product_page(url)
        if product_info:
            products.append(product_info)
        
        # Delay between requests
        time.sleep(2)
    
    if products:
        print(f"\nSuccessfully parsed {len(products)} products!")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        parser.save_to_csv(products, f"led_products_{timestamp}.csv")
        parser.save_to_json(products, f"led_products_{timestamp}.json")
        
        # Display summary
        for product in products:
            print(f"- {product.title[:50]}... | {product.price_range} | MOQ: {product.min_order}")
    
    return products

def example_advanced_filtering(products):
    """Example of advanced filtering and sorting"""
    print("\n=== Advanced Filtering Example ===")
    
    if not products:
        print("No products to filter. Run basic search first.")
        return
    
    # Filter by price range
    print("Filtering products by price range (¥0 - ¥50)...")
    filtered_by_price = filter_products_by_criteria(
        products, 
        max_price=50
    )
    print(f"Found {len(filtered_by_price)} products under ¥50")
    
    # Filter by supplier location
    print("Filtering products by supplier location (Guangdong)...")
    filtered_by_location = filter_products_by_criteria(
        products, 
        supplier_location="Guangdong"
    )
    print(f"Found {len(filtered_by_location)} products from Guangdong")
    
    # Sort products by price (lowest first)
    print("Sorting products by price (lowest first)...")
    sorted_by_price = sort_products(filtered_by_price, "price", reverse=False)
    
    print("Top 3 cheapest products:")
    for i, product in enumerate(sorted_by_price[:3]):
        print(f"{i+1}. {product.title[:40]}... | {product.price_range}")
    
    # Sort by rating (highest first)
    print("\nSorting products by rating (highest first)...")
    sorted_by_rating = sort_products(products, "rating", reverse=True)
    
    print("Top 3 highest rated products:")
    for i, product in enumerate(sorted_by_rating[:3]):
        print(f"{i+1}. {product.title[:40]}... | Rating: {product.rating}/5")

def example_data_validation(products):
    """Example of data validation"""
    print("\n=== Data Validation Example ===")
    
    if not products:
        print("No products to validate. Run basic search first.")
        return
    
    print("Validating product data...")
    
    valid_products = []
    invalid_products = []
    
    for product in products:
        validation_result = validate_product_data(product.__dict__)
        
        if validation_result['is_valid']:
            valid_products.append(product)
            if validation_result['warnings']:
                print(f"⚠️  Product {product.product_id}: {validation_result['warnings']}")
        else:
            invalid_products.append(product)
            print(f"❌ Product {product.product_id}: {validation_result['errors']}")
    
    print(f"\nValidation Results:")
    print(f"✅ Valid products: {len(valid_products)}")
    print(f"❌ Invalid products: {len(invalid_products)}")
    
    return valid_products, invalid_products

def example_summary_report(products):
    """Example of creating summary reports"""
    print("\n=== Summary Report Example ===")
    
    if not products:
        print("No products to analyze. Run basic search first.")
        return
    
    # Create summary report
    summary = create_summary_report(products)
    
    print("📊 Product Summary Report:")
    print(f"Total Products: {summary['total_products']}")
    print(f"Unique Suppliers: {summary['unique_suppliers']}")
    print(f"Average Price: ¥{summary['average_price']}")
    print(f"Average Rating: {summary['average_rating']}/5")
    
    print("\n📁 Products by Category:")
    for category, count in summary['categories'].items():
        print(f"  {category}: {count} products")
    
    # Save summary report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_to_file(summary, f"summary_report_{timestamp}.json", "json")
    print(f"\nSummary report saved to: summary_report_{timestamp}.json")

def example_batch_processing():
    """Example of batch processing multiple searches"""
    print("\n=== Batch Processing Example ===")
    
    parser = Alibaba1688Parser()
    
    # Define search terms
    search_terms = [
        {"keyword": "phone cases", "pages": 2, "category": "electronics"},
        {"keyword": "sports shoes", "pages": 2, "category": "sports"},
        {"keyword": "kitchen utensils", "pages": 2, "category": "home"}
    ]
    
    all_products = []
    
    for i, search_config in enumerate(search_terms):
        print(f"\nProcessing search {i+1}/{len(search_terms)}: {search_config['keyword']}")
        
        try:
            # Search for products
            product_urls = parser.search_products(
                search_config['keyword'], 
                search_config['pages']
            )
            
            print(f"Found {len(product_urls)} product URLs")
            
            # Parse products (limit to 3 per search for demo)
            for j, url in enumerate(product_urls[:3]):
                print(f"  Parsing product {j+1}/3...")
                product_info = parser.parse_product_page(url)
                if product_info:
                    # Add search metadata
                    product_info.category = search_config['category']
                    all_products.append(product_info)
                
                time.sleep(1)  # Small delay between requests
            
            print(f"  Completed search for '{search_config['keyword']}'")
            
        except Exception as e:
            print(f"  Error processing '{search_config['keyword']}': {e}")
            continue
    
    if all_products:
        print(f"\nBatch processing completed! Total products: {len(all_products)}")
        
        # Save all products
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        parser.save_to_csv(all_products, f"batch_products_{timestamp}.csv")
        
        # Create summary report
        example_summary_report(all_products)
    
    return all_products

def example_custom_export(products):
    """Example of custom data export"""
    print("\n=== Custom Export Example ===")
    
    if not products:
        print("No products to export. Run basic search first.")
        return
    
    # Create custom export format
    custom_export = []
    
    for product in products:
        custom_product = {
            "Product Name": product.title,
            "Price": product.price_range,
            "Supplier": product.supplier,
            "Location": product.supplier_location,
            "MOQ": product.min_order,
            "Rating": f"{product.rating}/5" if product.rating else "N/A",
            "Category": product.category,
            "URL": product.product_url
        }
        custom_export.append(custom_product)
    
    # Save custom export
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_to_file(custom_export, f"custom_export_{timestamp}.csv", "csv")
    
    print(f"Custom export saved to: custom_export_{timestamp}.csv")
    print("Custom export includes: Product Name, Price, Supplier, Location, MOQ, Rating, Category, URL")

def main():
    """Main function to run all examples"""
    print("🚀 1688 Product Parser - Example Usage")
    print("=" * 50)
    
    try:
        # Run basic search first
        products = example_basic_search()
        
        if products:
            # Run other examples
            example_advanced_filtering(products)
            example_data_validation(products)
            example_summary_report(products)
            example_custom_export(products)
            
            # Run batch processing
            example_batch_processing()
        
        print("\n✅ All examples completed successfully!")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Examples interrupted by user")
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()