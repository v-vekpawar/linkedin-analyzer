#!/usr/bin/env python3
"""
LinkedIn Profile Summarizer - Installation Test
Verifies that all dependencies are properly installed and the application can run
"""

import sys
import importlib
import os

def test_imports():
    """Test if all required packages can be imported"""
    print("🔍 Testing package imports...")
    
    required_packages = [
        'selenium',
        'flask',
        'dotenv',
        'webdriver_manager',
        'beautifulsoup4',
        'requests',
        'google.generativeai'
    ]
    
    failed_imports = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError as e:
            print(f"❌ {package}: {e}")
            failed_imports.append(package)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
        print("Please install missing packages with: pip install -r requirements.txt")
        return False
    else:
        print("\n✅ All packages imported successfully!")
        return True

def test_config():
    """Test if configuration can be loaded"""
    print("\n🔍 Testing configuration...")
    
    try:
        from config import GEMINI_API_KEY, SELENIUM_TIMEOUT, FLASK_HOST, FLASK_PORT
        print("✅ Configuration loaded successfully")
        
        if not GEMINI_API_KEY:
            print("⚠️  Gemini API key not found in .env file")
            print("   Please create a .env file with your GEMINI_API_KEY")
        else:
            print("✅ Gemini API key found")
            
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_local_modules():
    """Test if local modules can be imported"""
    print("\n🔍 Testing local modules...")
    
    local_modules = ['scraper', 'summarizer', 'main']
    failed_modules = []
    
    for module in local_modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module}.py")
        except ImportError as e:
            print(f"❌ {module}.py: {e}")
            failed_modules.append(module)
    
    if failed_modules:
        print(f"\n❌ Failed to import local modules: {', '.join(failed_modules)}")
        return False
    else:
        print("\n✅ All local modules imported successfully!")
        return True

def test_templates():
    """Test if Flask templates exist"""
    print("\n🔍 Testing Flask templates...")
    
    required_templates = [
        'templates/index.html',
        'templates/result.html'
    ]
    
    missing_templates = []
    
    for template in required_templates:
        if os.path.exists(template):
            print(f"✅ {template}")
        else:
            print(f"❌ {template} (missing)")
            missing_templates.append(template)
    
    if missing_templates:
        print(f"\n❌ Missing templates: {', '.join(missing_templates)}")
        return False
    else:
        print("\n✅ All templates found!")
        return True

def test_gemini_connection():
    """Test Gemini API connection (if API key is available)"""
    print("\n🔍 Testing Gemini API connection...")
    
    try:
        from config import GEMINI_API_KEY
        import google.generativeai as genai
        
        if not GEMINI_API_KEY:
            print("⚠️  Skipping Gemini API test (no API key)")
            return True
        
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("Say hello!")
        if hasattr(response, 'text') and response.text:
            print("✅ Gemini API connection successful!")
            return True
        else:
            print("❌ Gemini API returned empty response")
            return False
    except Exception as e:
        print(f"❌ Gemini API test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("LinkedIn Profile Summarizer - Installation Test")
    print("=" * 60)
    
    tests = [
        ("Package Imports", test_imports),
        ("Configuration", test_config),
        ("Local Modules", test_local_modules),
        ("Flask Templates", test_templates),
        ("Gemini API Connection", test_gemini_connection)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your installation is ready.")
        print("\nNext steps:")
        print("1. Set up your GEMINI_API_KEY in .env file")
        print("2. Run: python main.py")
        print("3. Choose your preferred mode (console or web)")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please fix the issues above.")
        print("\nCommon solutions:")
        print("- Run: pip install -r requirements.txt")
        print("- Create .env file with your GEMINI_API_KEY")
        print("- Ensure all files are in the correct directory structure")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 