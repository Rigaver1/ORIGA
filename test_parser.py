#!/usr/bin/env python3
"""
Simple test script to demonstrate the 1688 parser structure
This version works without external dependencies for testing
"""

import json
import csv
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

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

def create_sample_products() -> List[Product]:
    """Create sample products for demonstration"""
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
            description="High-quality wireless Bluetooth headphones with noise cancellation technology",
            specifications={"Material": "ABS Plastic", "Weight": "250g", "Battery": "500mAh", "Range": "10m"},
            shipping_info="Free shipping for orders over ¥500",
            category="Electronics",
            keywords=["wireless", "bluetooth", "headphones", "audio", "premium", "noise-cancellation"],
            scraped_at=datetime.now().isoformat()
        ),
        Product(
            id="987654321",
            title="Cotton T-Shirt Wholesale Blank Apparel Custom Printing",
            price="¥12.80",
            price_range="¥10.50 - ¥15.00",
            min_order_quantity="100",
            supplier_name="Guangzhou Textile Manufacturing Co.",
            supplier_location="Guangzhou, Guangdong",
            supplier_rating="4.2",
            product_url="https://detail.1688.com/offer/987654321.html",
            image_urls=["https://example.com/tshirt1.jpg", "https://example.com/tshirt2.jpg"],
            description="100% cotton t-shirt, various colors available, suitable for custom printing",
            specifications={"Material": "100% Cotton", "Weight": "180g", "Sizes": "S-XXL", "Colors": "10+ options"},
            shipping_info="Sea freight available for bulk orders",
            category="Textiles",
            keywords=["cotton", "t-shirt", "apparel", "wholesale", "blank", "custom", "printing"],
            scraped_at=datetime.now().isoformat()
        ),
        Product(
            id="456789123",
            title="Stainless Steel Kitchen Knife Set Professional Chef Tools",
            price="¥156.00",
            price_range="¥145.00 - ¥170.00",
            min_order_quantity="20",
            supplier_name="Yangjiang Blade Industries",
            supplier_location="Yangjiang, Guangdong",
            supplier_rating="4.8",
            product_url="https://detail.1688.com/offer/456789123.html",
            image_urls=["https://example.com/knife1.jpg", "https://example.com/knife2.jpg", "https://example.com/knife3.jpg"],
            description="Professional chef knife set with 8 pieces, German steel, ergonomic handles",
            specifications={"Material": "German Steel", "Pieces": "8-piece set", "Handle": "Ergonomic", "Hardness": "58-60 HRC"},
            shipping_info="Express delivery available",
            category="Kitchen Tools",
            keywords=["knife", "kitchen", "chef", "professional", "stainless", "steel", "cooking"],
            scraped_at=datetime.now().isoformat()
        )
    ]

@dataclass
class CargoProduct:
    """Cargo-optimized product data structure"""
    product_id: str
    product_name: str
    supplier_name: str
    supplier_location: str
    unit_price: float
    price_currency: str
    minimum_order_qty: int
    estimated_weight: str
    dimensions: str
    category: str
    hs_code: str
    material: str
    risk_assessment: str
    profit_margin: float
    competition_level: str
    quality_grade: str
    supplier_reliability: str
    shipping_method: str
    lead_time: str
    storage_requirements: str
    fragility_rating: str
    product_images: List[str]
    notes: str
    last_updated: str

class SimpleCargProcessor:
    """Simplified cargo processor for testing"""
    
    def __init__(self):
        self.hs_codes = {
            'electronics': '8517.12.00',
            'textiles': '6109.10.00',
            'kitchen tools': '8205.59.00',
            'general': '9999.99.00'
        }
    
    def convert_to_cargo_products(self, products: List[Product]) -> List[CargoProduct]:
        """Convert products to cargo format"""
        cargo_products = []
        
        for product in products:
            # Extract price
            price_match = re.search(r'(\d+\.?\d*)', product.price)
            unit_price = float(price_match.group(1)) if price_match else 0.0
            
            # Determine category
            category = product.category.lower()
            hs_code = self.hs_codes.get(category, self.hs_codes['general'])
            
            # Calculate metrics
            profit_margin = self._calculate_profit_margin(unit_price, category)
            quality_grade = self._assess_quality(product.supplier_rating, unit_price)
            risk_assessment = self._assess_risk(category, product.supplier_rating)
            
            cargo_product = CargoProduct(
                product_id=product.id,
                product_name=product.title,
                supplier_name=product.supplier_name,
                supplier_location=product.supplier_location,
                unit_price=unit_price,
                price_currency="CNY",
                minimum_order_qty=int(product.min_order_quantity) if product.min_order_quantity.isdigit() else 1,
                estimated_weight=product.specifications.get("Weight", "Unknown"),
                dimensions=product.specifications.get("Dimensions", "Not specified"),
                category=product.category,
                hs_code=hs_code,
                material=product.specifications.get("Material", "Not specified"),
                risk_assessment=risk_assessment,
                profit_margin=profit_margin,
                competition_level=self._assess_competition(category),
                quality_grade=quality_grade,
                supplier_reliability=self._assess_supplier_reliability(product.supplier_rating),
                shipping_method=self._recommend_shipping(category, unit_price),
                lead_time=self._estimate_lead_time(category),
                storage_requirements=self._get_storage_requirements(category),
                fragility_rating=self._assess_fragility(category),
                product_images=product.image_urls,
                notes=self._generate_notes(product),
                last_updated=datetime.now().isoformat()
            )
            
            cargo_products.append(cargo_product)
        
        return cargo_products
    
    def _calculate_profit_margin(self, price: float, category: str) -> float:
        """Calculate estimated profit margin"""
        margins = {
            'electronics': 0.20,
            'textiles': 0.35,
            'kitchen tools': 0.25,
            'general': 0.20
        }
        base_margin = margins.get(category, 0.20)
        
        # Adjust based on price
        if price > 100:
            base_margin += 0.05
        elif price < 20:
            base_margin -= 0.05
            
        return max(0.10, min(0.50, base_margin))
    
    def _assess_quality(self, rating: str, price: float) -> str:
        """Assess quality grade"""
        try:
            rating_num = float(rating) if rating.replace('.', '').isdigit() else 3.0
            
            if rating_num >= 4.5 and price > 50:
                return "A - Premium Quality"
            elif rating_num >= 4.0:
                return "B+ - High Quality"
            elif rating_num >= 3.5:
                return "B - Standard Quality"
            else:
                return "C - Economy Quality"
        except:
            return "B - Standard Quality"
    
    def _assess_risk(self, category: str, rating: str) -> str:
        """Assess risk level"""
        category_risks = {
            'electronics': 'Medium - Technology risk',
            'textiles': 'Low - Stable market',
            'kitchen tools': 'Low - Consistent demand'
        }
        
        try:
            rating_num = float(rating) if rating.replace('.', '').isdigit() else 3.0
            base_risk = category_risks.get(category, 'Medium - Standard risk')
            
            if rating_num >= 4.5:
                return f"{base_risk}, Low supplier risk"
            elif rating_num >= 3.5:
                return f"{base_risk}, Medium supplier risk"
            else:
                return f"{base_risk}, High supplier risk"
        except:
            return f"{category_risks.get(category, 'Medium - Standard risk')}, Unknown supplier risk"
    
    def _assess_competition(self, category: str) -> str:
        """Assess competition level"""
        competition = {
            'electronics': 'Very High - Saturated market',
            'textiles': 'High - Many suppliers',
            'kitchen tools': 'Medium - Specialized market'
        }
        return competition.get(category, 'Medium - Moderate competition')
    
    def _assess_supplier_reliability(self, rating: str) -> str:
        """Assess supplier reliability"""
        try:
            rating_num = float(rating) if rating.replace('.', '').isdigit() else 3.0
            
            if rating_num >= 4.7:
                return "Excellent - Top tier"
            elif rating_num >= 4.3:
                return "Very Good - Reliable"
            elif rating_num >= 3.8:
                return "Good - Acceptable"
            else:
                return "Fair - Monitor closely"
        except:
            return "Unknown - Needs verification"
    
    def _recommend_shipping(self, category: str, price: float) -> str:
        """Recommend shipping method"""
        if category == 'electronics' or price > 100:
            return "Air freight - Fast delivery"
        elif category == 'textiles':
            return "Sea freight - Cost effective"
        else:
            return "Express - Balanced option"
    
    def _estimate_lead_time(self, category: str) -> str:
        """Estimate lead time"""
        times = {
            'electronics': '7-15 days',
            'textiles': '5-10 days',
            'kitchen tools': '10-20 days'
        }
        return times.get(category, '10-15 days')
    
    def _get_storage_requirements(self, category: str) -> str:
        """Get storage requirements"""
        requirements = {
            'electronics': 'Dry, temperature controlled',
            'textiles': 'Dry, ventilated storage',
            'kitchen tools': 'Dry, secure storage'
        }
        return requirements.get(category, 'Standard warehouse')
    
    def _assess_fragility(self, category: str) -> str:
        """Assess fragility"""
        fragility = {
            'electronics': 'High - Handle carefully',
            'textiles': 'Low - Standard handling',
            'kitchen tools': 'Medium - Sharp edges'
        }
        return fragility.get(category, 'Medium - Standard care')
    
    def _generate_notes(self, product: Product) -> str:
        """Generate notes"""
        notes = []
        
        if int(product.min_order_quantity) > 100:
            notes.append(f"High MOQ: {product.min_order_quantity}")
        
        if len(product.image_urls) > 3:
            notes.append("Multiple product images available")
        
        if "custom" in product.title.lower():
            notes.append("Customization available")
        
        return "; ".join(notes) if notes else "Standard product"
    
    def export_to_csv(self, cargo_products: List[CargoProduct], filename: str) -> None:
        """Export to CSV"""
        if not cargo_products:
            print("No products to export")
            return
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = list(asdict(cargo_products[0]).keys())
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for product in cargo_products:
                row = asdict(product)
                row['product_images'] = '; '.join(row['product_images'])
                writer.writerow(row)
        
        print(f"✓ Exported {len(cargo_products)} products to {filename}")
    
    def generate_report(self, cargo_products: List[CargoProduct]) -> Dict[str, Any]:
        """Generate analysis report"""
        if not cargo_products:
            return {"error": "No products to analyze"}
        
        total_products = len(cargo_products)
        categories = {}
        avg_profit_margin = 0
        quality_grades = {}
        
        for product in cargo_products:
            categories[product.category] = categories.get(product.category, 0) + 1
            avg_profit_margin += product.profit_margin
            quality_grades[product.quality_grade] = quality_grades.get(product.quality_grade, 0) + 1
        
        avg_profit_margin /= total_products
        
        return {
            "summary": {
                "total_products": total_products,
                "average_profit_margin": f"{avg_profit_margin:.2%}",
                "generated_at": datetime.now().isoformat()
            },
            "categories": categories,
            "quality_distribution": quality_grades,
            "recommendations": [
                f"Focus on {len([p for p in cargo_products if p.profit_margin > 0.25])} high-margin products",
                f"Monitor {len([p for p in cargo_products if 'High' in p.risk_assessment])} high-risk products",
                f"Prioritize {len([p for p in cargo_products if 'Excellent' in p.supplier_reliability])} excellent suppliers"
            ]
        }

def main():
    """Test the parser functionality"""
    print("1688 Product Parser - Test Demo")
    print("=" * 40)
    
    # Create sample products
    print("Creating sample products...")
    products = create_sample_products()
    print(f"✓ Created {len(products)} sample products")
    
    # Display products
    print("\n--- Sample Products ---")
    for i, product in enumerate(products, 1):
        print(f"{i}. {product.title}")
        print(f"   Price: {product.price} | MOQ: {product.min_order_quantity}")
        print(f"   Supplier: {product.supplier_name} ({product.supplier_rating}★)")
        print(f"   Category: {product.category}")
        print()
    
    # Export standard format
    print("Exporting standard format...")
    with open('sample_products.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = list(asdict(products[0]).keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for product in products:
            row = asdict(product)
            row['image_urls'] = '; '.join(row['image_urls'])
            row['keywords'] = '; '.join(row['keywords'])
            row['specifications'] = '; '.join([f"{k}: {v}" for k, v in row['specifications'].items()])
            writer.writerow(row)
    
    print("✓ Exported to sample_products.csv")
    
    # Process for cargo management
    print("\nProcessing for cargo management...")
    processor = SimpleCargProcessor()
    cargo_products = processor.convert_to_cargo_products(products)
    print(f"✓ Processed {len(cargo_products)} products for cargo management")
    
    # Display cargo analysis
    print("\n--- Cargo Analysis ---")
    for i, cargo in enumerate(cargo_products, 1):
        print(f"{i}. {cargo.product_name}")
        print(f"   Price: ¥{cargo.unit_price} | Profit Margin: {cargo.profit_margin:.1%}")
        print(f"   Quality: {cargo.quality_grade}")
        print(f"   Risk: {cargo.risk_assessment}")
        print(f"   HS Code: {cargo.hs_code}")
        print()
    
    # Export cargo format
    processor.export_to_csv(cargo_products, 'cargo_products.csv')
    
    # Generate report
    print("Generating analysis report...")
    report = processor.generate_report(cargo_products)
    
    with open('analysis_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print("✓ Generated analysis_report.json")
    
    # Display summary
    print("\n--- Analysis Summary ---")
    print(f"Total Products: {report['summary']['total_products']}")
    print(f"Average Profit Margin: {report['summary']['average_profit_margin']}")
    
    print("\nCategories:")
    for category, count in report['categories'].items():
        print(f"  {category}: {count} products")
    
    print("\nRecommendations:")
    for rec in report['recommendations']:
        print(f"  • {rec}")
    
    print("\n" + "=" * 40)
    print("Test completed successfully!")
    print("\nGenerated files:")
    print("  • sample_products.csv - Standard product data")
    print("  • cargo_products.csv - Cargo-optimized data")
    print("  • analysis_report.json - Business analysis")

if __name__ == "__main__":
    main()