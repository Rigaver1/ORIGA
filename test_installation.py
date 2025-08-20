#!/usr/bin/env python3
"""
Test script to verify 1688 parser installation
Run this script to check if all dependencies are properly installed
"""

import sys
import importlib

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing module imports...")
    
    required_modules = [
        'requests',
        'bs4',
        'lxml',
        'urllib3',
        'certifi',
        'charset_normalizer',
        'soupsieve'
    ]
    
    failed_imports = []
    
    for module in required_modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            failed_imports.append(module)
    
    return len(failed_imports) == 0

def test_parser_import():
    """Test if the main parser can be imported"""
    print("\n🔍 Testing parser import...")
    
    try:
        from 1688_parser import Alibaba1688Parser, ProductInfo
        print("✅ 1688_parser module imported successfully")
        print("✅ Alibaba1688Parser class available")
        print("✅ ProductInfo class available")
        return True
    except ImportError as e:
        print(f"❌ Failed to import 1688_parser: {e}")
        return False

def test_utils_import():
    """Test if utility functions can be imported"""
    print("\n🔍 Testing utils import...")
    
    try:
        from utils import (
            setup_logging,
            clean_text,
            extract_price,
            filter_products_by_criteria
        )
        print("✅ utils module imported successfully")
        print("✅ Utility functions available")
        return True
    except ImportError as e:
        print(f"❌ Failed to import utils: {e}")
        return False

def test_config_import():
    """Test if configuration can be imported"""
    print("\n🔍 Testing config import...")
    
    try:
        import config
        print("✅ config module imported successfully")
        print(f"✅ Base URL: {config.BASE_URL}")
        print(f"✅ Search URL: {config.SEARCH_URL}")
        return True
    except ImportError as e:
        print(f"❌ Failed to import config: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality without making actual requests"""
    print("\n🔍 Testing basic functionality...")
    
    try:
        from 1688_parser import Alibaba1688Parser
        
        # Create parser instance
        parser = Alibaba1688Parser()
        print("✅ Parser instance created successfully")
        
        # Test data structure
        from dataclasses import fields
        from 1688_parser import ProductInfo
        
        fields_list = [field.name for field in fields(ProductInfo)]
        print(f"✅ ProductInfo has {len(fields_list)} fields")
        print(f"   Fields: {', '.join(fields_list[:5])}...")
        
        return True
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

def test_file_structure():
    """Test if all required files exist"""
    print("\n🔍 Testing file structure...")
    
    required_files = [
        '1688_parser.py',
        'cargo_manager.html',
        'config.py',
        'utils.py',
        'requirements.txt',
        'README.md'
    ]
    
    missing_files = []
    
    for file in required_files:
        try:
            with open(file, 'r') as f:
                print(f"✅ {file}")
        except FileNotFoundError:
            print(f"❌ {file} - File not found")
            missing_files.append(file)
    
    return len(missing_files) == 0

def main():
    """Main test function"""
    print("🚀 1688 Product Parser - Installation Test")
    print("=" * 50)
    
    tests = [
        ("Module Imports", test_imports),
        ("Parser Import", test_parser_import),
        ("Utils Import", test_utils_import),
        ("Config Import", test_config_import),
        ("Basic Functionality", test_basic_functionality),
        ("File Structure", test_file_structure)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Installation is successful.")
        print("\nNext steps:")
        print("1. Run: python 1688_parser.py")
        print("2. Open cargo_manager.html in your browser")
        print("3. Check example_usage.py for usage examples")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the errors above.")
        print("\nTroubleshooting:")
        print("1. Install missing dependencies: pip install -r requirements.txt")
        print("2. Check Python version (requires 3.7+)")
        print("3. Verify all files are in the same directory")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)