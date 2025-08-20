#!/usr/bin/env python3
"""
Cargo Manager Integration Module
Specialized utilities for integrating 1688 product data with cargo management systems
"""

import json
import csv
import pandas as pd
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import logging
from alibaba_1688_parser import Product, Alibaba1688Parser

logger = logging.getLogger(__name__)

@dataclass
class CargoProduct:
    """Optimized product data structure for cargo management"""
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
    hs_code: str  # Harmonized System code for customs
    material: str
    packaging_info: str
    lead_time: str
    shipping_method: str
    quality_grade: str
    certifications: List[str]
    risk_assessment: str
    profit_margin: float
    competition_level: str
    market_demand: str
    seasonal_factor: str
    storage_requirements: str
    fragility_rating: str
    customs_complexity: str
    supplier_reliability: str
    product_images: List[str]
    notes: str
    last_updated: str

class CargoManagerProcessor:
    """
    Process 1688 product data for cargo management optimization
    """
    
    def __init__(self):
        self.currency_rates = {
            'CNY': 1.0,  # Base currency (Chinese Yuan)
            'USD': 0.14,  # Approximate rate - should be updated with real API
            'EUR': 0.13,
            'GBP': 0.11
        }
        
        # Common HS codes for popular product categories
        self.hs_codes = {
            'electronics': '8517.12.00',
            'textiles': '6109.10.00',
            'machinery': '8479.89.98',
            'furniture': '9403.60.90',
            'toys': '9503.00.00',
            'tools': '8205.59.00',
            'automotive': '8708.99.00',
            'home_garden': '6913.10.00',
            'beauty': '3304.99.00',
            'sports': '9506.99.00'
        }
        
        # Risk assessment criteria
        self.risk_factors = {
            'electronics': 'Medium - Fragile, customs scrutiny',
            'textiles': 'Low - Standard shipping',
            'machinery': 'High - Heavy, complex customs',
            'chemicals': 'High - Hazardous materials',
            'food': 'High - Perishable, health regulations'
        }
    
    def convert_to_cargo_products(self, products: List[Product]) -> List[CargoProduct]:
        """
        Convert 1688 products to cargo-optimized format
        
        Args:
            products: List of Product objects from 1688 parser
            
        Returns:
            List of CargoProduct objects optimized for cargo management
        """
        cargo_products = []
        
        for product in products:
            try:
                cargo_product = self._process_single_product(product)
                if cargo_product:
                    cargo_products.append(cargo_product)
            except Exception as e:
                logger.error(f"Error processing product {product.id}: {str(e)}")
                continue
        
        return cargo_products
    
    def _process_single_product(self, product: Product) -> Optional[CargoProduct]:
        """Process a single product for cargo management"""
        try:
            # Extract and convert price
            unit_price, currency = self._extract_price_info(product.price)
            
            # Determine category and related info
            category = self._categorize_product(product.title, product.category, product.keywords)
            hs_code = self._get_hs_code(category)
            
            # Assess risks and logistics
            risk_assessment = self._assess_risk(category, product.supplier_rating)
            shipping_method = self._recommend_shipping(category, unit_price)
            
            # Extract specifications
            dimensions = self._extract_dimensions(product.specifications)
            weight = self._extract_weight(product.specifications)
            material = self._extract_material(product.specifications)
            
            # Calculate business metrics
            profit_margin = self._calculate_profit_margin(unit_price, category)
            competition_level = self._assess_competition(product.keywords, category)
            
            # Quality and reliability assessment
            quality_grade = self._assess_quality(product.supplier_rating, product.price, product.keywords)
            supplier_reliability = self._assess_supplier_reliability(product.supplier_rating, product.supplier_location)
            
            return CargoProduct(
                product_id=product.id,
                product_name=product.title,
                supplier_name=product.supplier_name,
                supplier_location=product.supplier_location,
                unit_price=unit_price,
                price_currency=currency,
                minimum_order_qty=int(product.min_order_quantity) if product.min_order_quantity.isdigit() else 1,
                estimated_weight=weight,
                dimensions=dimensions,
                category=category,
                hs_code=hs_code,
                material=material,
                packaging_info=self._get_packaging_info(category),
                lead_time=self._estimate_lead_time(product.supplier_location, category),
                shipping_method=shipping_method,
                quality_grade=quality_grade,
                certifications=self._identify_certifications(product.description, product.keywords),
                risk_assessment=risk_assessment,
                profit_margin=profit_margin,
                competition_level=competition_level,
                market_demand=self._assess_market_demand(category, product.keywords),
                seasonal_factor=self._assess_seasonality(category, product.keywords),
                storage_requirements=self._get_storage_requirements(category, material),
                fragility_rating=self._assess_fragility(category, material),
                customs_complexity=self._assess_customs_complexity(category, hs_code),
                supplier_reliability=supplier_reliability,
                product_images=product.image_urls,
                notes=self._generate_notes(product),
                last_updated=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Error processing product {product.id}: {str(e)}")
            return None
    
    def _extract_price_info(self, price_str: str) -> tuple[float, str]:
        """Extract numeric price and currency from price string"""
        import re
        
        # Remove currency symbols and extract number
        price_match = re.search(r'(\d+\.?\d*)', price_str)
        if price_match:
            price = float(price_match.group(1))
        else:
            price = 0.0
        
        # Determine currency (default to CNY for 1688)
        currency = 'CNY'
        if '$' in price_str:
            currency = 'USD'
        elif '€' in price_str:
            currency = 'EUR'
        elif '£' in price_str:
            currency = 'GBP'
        
        return price, currency
    
    def _categorize_product(self, title: str, category: str, keywords: List[str]) -> str:
        """Categorize product based on title, category, and keywords"""
        text = f"{title} {category} {' '.join(keywords)}".lower()
        
        categories = {
            'electronics': ['electronic', 'phone', 'computer', 'digital', 'gadget', 'device'],
            'textiles': ['clothing', 'fabric', 'textile', 'apparel', 'fashion', 'garment'],
            'machinery': ['machine', 'equipment', 'motor', 'pump', 'tool', 'industrial'],
            'furniture': ['furniture', 'chair', 'table', 'desk', 'cabinet', 'sofa'],
            'toys': ['toy', 'game', 'doll', 'puzzle', 'educational', 'children'],
            'automotive': ['car', 'auto', 'vehicle', 'motorcycle', 'parts', 'accessories'],
            'home_garden': ['home', 'garden', 'kitchen', 'bathroom', 'decoration', 'household'],
            'beauty': ['beauty', 'cosmetic', 'skincare', 'makeup', 'personal care'],
            'sports': ['sport', 'fitness', 'outdoor', 'exercise', 'gym', 'athletic']
        }
        
        for cat, keywords_list in categories.items():
            if any(keyword in text for keyword in keywords_list):
                return cat
        
        return 'general'
    
    def _get_hs_code(self, category: str) -> str:
        """Get HS code for category"""
        return self.hs_codes.get(category, '9999.99.00')
    
    def _assess_risk(self, category: str, supplier_rating: str) -> str:
        """Assess overall risk level"""
        base_risk = self.risk_factors.get(category, 'Medium - Standard risk')
        
        try:
            rating = float(supplier_rating) if supplier_rating.replace('.', '').isdigit() else 3.0
            if rating >= 4.5:
                risk_modifier = "Low supplier risk"
            elif rating >= 3.5:
                risk_modifier = "Medium supplier risk"
            else:
                risk_modifier = "High supplier risk"
        except:
            risk_modifier = "Unknown supplier risk"
        
        return f"{base_risk}, {risk_modifier}"
    
    def _recommend_shipping(self, category: str, price: float) -> str:
        """Recommend shipping method based on category and price"""
        if category in ['electronics', 'machinery'] or price > 100:
            return "Air freight - Fast, secure"
        elif category in ['textiles', 'toys'] and price < 50:
            return "Sea freight - Economical"
        else:
            return "Express courier - Balanced"
    
    def _extract_dimensions(self, specifications: Dict[str, str]) -> str:
        """Extract dimensions from specifications"""
        dimension_keys = ['size', 'dimensions', 'length', 'width', 'height', '尺寸', '大小']
        
        for key, value in specifications.items():
            if any(dim_key in key.lower() for dim_key in dimension_keys):
                return value
        
        return "Dimensions not specified"
    
    def _extract_weight(self, specifications: Dict[str, str]) -> str:
        """Extract weight from specifications"""
        weight_keys = ['weight', 'mass', '重量', '净重']
        
        for key, value in specifications.items():
            if any(weight_key in key.lower() for weight_key in weight_keys):
                return value
        
        return "Weight not specified"
    
    def _extract_material(self, specifications: Dict[str, str]) -> str:
        """Extract material from specifications"""
        material_keys = ['material', 'fabric', 'composition', '材质', '材料']
        
        for key, value in specifications.items():
            if any(mat_key in key.lower() for mat_key in material_keys):
                return value
        
        return "Material not specified"
    
    def _calculate_profit_margin(self, price: float, category: str) -> float:
        """Calculate estimated profit margin"""
        # Rough estimates based on category
        margin_estimates = {
            'electronics': 0.15,  # 15%
            'textiles': 0.25,     # 25%
            'toys': 0.30,         # 30%
            'furniture': 0.20,    # 20%
            'general': 0.20       # 20%
        }
        
        base_margin = margin_estimates.get(category, 0.20)
        
        # Adjust based on price (higher price = potentially higher margin)
        if price > 100:
            base_margin += 0.05
        elif price < 10:
            base_margin -= 0.05
        
        return max(0.05, min(0.50, base_margin))  # Cap between 5% and 50%
    
    def _assess_competition(self, keywords: List[str], category: str) -> str:
        """Assess competition level"""
        competitive_keywords = ['wholesale', 'factory', 'oem', 'custom', 'bulk']
        
        if any(keyword in ' '.join(keywords).lower() for keyword in competitive_keywords):
            return "High - Many suppliers available"
        elif category in ['electronics', 'textiles']:
            return "Very High - Saturated market"
        else:
            return "Medium - Moderate competition"
    
    def _assess_quality(self, rating: str, price: str, keywords: List[str]) -> str:
        """Assess product quality grade"""
        quality_keywords = ['premium', 'high quality', 'certified', 'grade a']
        
        try:
            supplier_rating = float(rating) if rating.replace('.', '').isdigit() else 3.0
            price_num = float(''.join(filter(str.isdigit, price))) if price else 0
            
            quality_score = 0
            
            # Rating factor
            if supplier_rating >= 4.5:
                quality_score += 3
            elif supplier_rating >= 3.5:
                quality_score += 2
            else:
                quality_score += 1
            
            # Price factor (higher price might indicate higher quality)
            if price_num > 100:
                quality_score += 2
            elif price_num > 50:
                quality_score += 1
            
            # Keywords factor
            if any(keyword in ' '.join(keywords).lower() for keyword in quality_keywords):
                quality_score += 2
            
            if quality_score >= 6:
                return "A - High Quality"
            elif quality_score >= 4:
                return "B - Standard Quality"
            else:
                return "C - Economy Quality"
                
        except:
            return "B - Standard Quality"
    
    def _assess_supplier_reliability(self, rating: str, location: str) -> str:
        """Assess supplier reliability"""
        try:
            rating_num = float(rating) if rating.replace('.', '').isdigit() else 3.0
            
            # Location factor (major manufacturing cities are generally more reliable)
            reliable_locations = ['guangzhou', 'shenzhen', 'shanghai', 'beijing', 'hangzhou', 'suzhou']
            location_bonus = 0.5 if any(city in location.lower() for city in reliable_locations) else 0
            
            total_score = rating_num + location_bonus
            
            if total_score >= 4.5:
                return "Excellent - Highly reliable"
            elif total_score >= 3.5:
                return "Good - Reliable"
            elif total_score >= 2.5:
                return "Fair - Moderate reliability"
            else:
                return "Poor - High risk"
                
        except:
            return "Unknown - Insufficient data"
    
    def _get_packaging_info(self, category: str) -> str:
        """Get standard packaging information by category"""
        packaging = {
            'electronics': 'Anti-static bags, foam padding, cardboard boxes',
            'textiles': 'Polybags, cartons, optional hangers',
            'furniture': 'Disassembled, protective wrapping, wooden crates',
            'toys': 'Blister packs, display boxes, safety packaging',
            'machinery': 'Wooden crates, anti-rust coating, shock absorbers'
        }
        
        return packaging.get(category, 'Standard commercial packaging')
    
    def _estimate_lead_time(self, location: str, category: str) -> str:
        """Estimate production lead time"""
        base_times = {
            'electronics': '7-15 days',
            'textiles': '5-12 days',
            'furniture': '15-30 days',
            'machinery': '20-45 days',
            'toys': '10-20 days'
        }
        
        return base_times.get(category, '10-20 days')
    
    def _identify_certifications(self, description: str, keywords: List[str]) -> List[str]:
        """Identify potential certifications from description and keywords"""
        cert_patterns = {
            'CE': ['ce certified', 'ce mark', 'european conformity'],
            'FCC': ['fcc approved', 'fcc certified'],
            'RoHS': ['rohs compliant', 'rohs certified'],
            'ISO': ['iso certified', 'iso 9001'],
            'FDA': ['fda approved', 'fda certified'],
            'UL': ['ul listed', 'ul certified']
        }
        
        text = f"{description} {' '.join(keywords)}".lower()
        certifications = []
        
        for cert, patterns in cert_patterns.items():
            if any(pattern in text for pattern in patterns):
                certifications.append(cert)
        
        return certifications
    
    def _assess_market_demand(self, category: str, keywords: List[str]) -> str:
        """Assess market demand level"""
        high_demand_categories = ['electronics', 'beauty', 'home_garden']
        trending_keywords = ['smart', 'wireless', 'eco-friendly', 'portable', 'led']
        
        if category in high_demand_categories:
            return "High - Popular category"
        elif any(keyword in ' '.join(keywords).lower() for keyword in trending_keywords):
            return "High - Trending product"
        else:
            return "Medium - Stable demand"
    
    def _assess_seasonality(self, category: str, keywords: List[str]) -> str:
        """Assess seasonal factors"""
        seasonal_categories = {
            'toys': 'High - Christmas peak',
            'sports': 'Medium - Summer peak',
            'beauty': 'Low - Year-round demand',
            'electronics': 'Medium - Holiday peaks'
        }
        
        seasonal_keywords = ['christmas', 'summer', 'winter', 'holiday', 'seasonal']
        
        if category in seasonal_categories:
            base_seasonality = seasonal_categories[category]
        else:
            base_seasonality = "Low - Stable year-round"
        
        if any(keyword in ' '.join(keywords).lower() for keyword in seasonal_keywords):
            return f"{base_seasonality}, Seasonal keywords detected"
        
        return base_seasonality
    
    def _get_storage_requirements(self, category: str, material: str) -> str:
        """Determine storage requirements"""
        requirements = {
            'electronics': 'Dry, temperature controlled, anti-static',
            'textiles': 'Dry, ventilated, pest control',
            'furniture': 'Covered, flat storage, climate controlled',
            'toys': 'Dry, secure, child-safe environment',
            'machinery': 'Covered, rust prevention, heavy-duty flooring'
        }
        
        base_req = requirements.get(category, 'Standard warehouse conditions')
        
        # Material-specific additions
        if 'metal' in material.lower():
            base_req += ', rust prevention'
        elif 'wood' in material.lower():
            base_req += ', humidity control'
        
        return base_req
    
    def _assess_fragility(self, category: str, material: str) -> str:
        """Assess fragility rating"""
        fragile_categories = ['electronics', 'toys']
        fragile_materials = ['glass', 'ceramic', 'crystal']
        
        if category in fragile_categories or any(mat in material.lower() for mat in fragile_materials):
            return "High - Handle with care"
        elif category == 'furniture':
            return "Medium - Protect surfaces"
        else:
            return "Low - Standard handling"
    
    def _assess_customs_complexity(self, category: str, hs_code: str) -> str:
        """Assess customs complexity"""
        complex_categories = ['electronics', 'machinery', 'beauty']
        
        if category in complex_categories:
            return "High - Detailed documentation required"
        elif hs_code.startswith('9999'):
            return "Medium - Standard classification needed"
        else:
            return "Low - Standard processing"
    
    def _generate_notes(self, product: Product) -> str:
        """Generate additional notes"""
        notes = []
        
        if not product.image_urls:
            notes.append("No product images available")
        
        if product.min_order_quantity and int(product.min_order_quantity) > 100:
            notes.append(f"High MOQ: {product.min_order_quantity}")
        
        if "custom" in product.title.lower() or "oem" in product.description.lower():
            notes.append("Customization available")
        
        if not product.specifications:
            notes.append("Limited technical specifications")
        
        return "; ".join(notes) if notes else "No additional notes"
    
    def export_cargo_csv(self, cargo_products: List[CargoProduct], filename: str = "cargo_manager_export.csv") -> None:
        """Export cargo products to CSV optimized for cargo management"""
        if not cargo_products:
            logger.warning("No cargo products to export")
            return
        
        # Convert to list of dictionaries
        data = [asdict(product) for product in cargo_products]
        
        # Convert lists to strings for CSV
        for row in data:
            row['certifications'] = '; '.join(row['certifications'])
            row['product_images'] = '; '.join(row['product_images'])
        
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, encoding='utf-8')
        
        logger.info(f"Exported {len(cargo_products)} cargo products to {filename}")
    
    def generate_cargo_report(self, cargo_products: List[CargoProduct]) -> Dict[str, Any]:
        """Generate summary report for cargo manager"""
        if not cargo_products:
            return {"error": "No products to analyze"}
        
        total_products = len(cargo_products)
        categories = {}
        suppliers = {}
        risk_levels = {}
        avg_profit_margin = 0
        
        for product in cargo_products:
            # Category analysis
            categories[product.category] = categories.get(product.category, 0) + 1
            
            # Supplier analysis
            suppliers[product.supplier_location] = suppliers.get(product.supplier_location, 0) + 1
            
            # Risk analysis
            risk_key = product.risk_assessment.split(',')[0]
            risk_levels[risk_key] = risk_levels.get(risk_key, 0) + 1
            
            # Profit margin
            avg_profit_margin += product.profit_margin
        
        avg_profit_margin /= total_products
        
        return {
            "summary": {
                "total_products": total_products,
                "average_profit_margin": f"{avg_profit_margin:.2%}",
                "generated_at": datetime.now().isoformat()
            },
            "category_breakdown": categories,
            "supplier_locations": suppliers,
            "risk_assessment": risk_levels,
            "recommendations": self._generate_recommendations(cargo_products)
        }
    
    def _generate_recommendations(self, cargo_products: List[CargoProduct]) -> List[str]:
        """Generate recommendations based on product analysis"""
        recommendations = []
        
        # Analyze profit margins
        high_margin_products = [p for p in cargo_products if p.profit_margin > 0.3]
        if high_margin_products:
            recommendations.append(f"Focus on {len(high_margin_products)} high-margin products (>30% profit)")
        
        # Analyze risk levels
        low_risk_products = [p for p in cargo_products if "Low" in p.risk_assessment]
        if low_risk_products:
            recommendations.append(f"Prioritize {len(low_risk_products)} low-risk products for initial orders")
        
        # Analyze supplier reliability
        reliable_suppliers = [p for p in cargo_products if "Excellent" in p.supplier_reliability]
        if reliable_suppliers:
            recommendations.append(f"Build relationships with {len(set(p.supplier_name for p in reliable_suppliers))} excellent suppliers")
        
        return recommendations

if __name__ == "__main__":
    # Example usage
    from alibaba_1688_parser import Alibaba1688Parser
    
    # Initialize parser and processor
    parser = Alibaba1688Parser()
    processor = CargoManagerProcessor()
    
    # Example: Process scraped products
    # products = parser.scrape_products(["https://example-1688-url.com"])
    # cargo_products = processor.convert_to_cargo_products(products)
    # processor.export_cargo_csv(cargo_products)
    # report = processor.generate_cargo_report(cargo_products)
    # print(json.dumps(report, indent=2, ensure_ascii=False))
    
    print("Cargo Manager Integration module ready for use!")