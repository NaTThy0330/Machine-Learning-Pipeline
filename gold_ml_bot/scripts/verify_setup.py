#!/usr/bin/env python3
"""
Sprint 1 Setup Verification Script
Checks that all required libraries and configurations are in place.
"""

import sys
import os
from pathlib import Path

def check_python_version():
    """Verify Python 3.10+"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} installed")
        return True
    else:
        print(f"✗ Python 3.10+ required (found {version.major}.{version.minor})")
        return False

def check_libraries():
    """Verify required libraries are installed"""
    libraries = [
        'pandas', 'numpy', 'ta', 'sklearn', 'xgboost',
        'dotenv', 'requests', 'matplotlib', 'jupyter',
        'pyarrow', 'fastparquet', 'yfinance',
        'oandapyV20', 'fredapi'
    ]
    
    all_good = True
    for lib in libraries:
        try:
            if lib == 'sklearn':
                __import__('sklearn')
            elif lib == 'dotenv':
                __import__('dotenv')
            elif lib == 'ta':
                __import__('ta')
            elif lib == 'oandapyV20':
                __import__('oandapyV20')
            elif lib == 'fredapi':
                __import__('fredapi')
            else:
                __import__(lib)
            print(f"  ✓ {lib}")
        except ImportError:
            print(f"  ✗ {lib} (missing - run: pip install {lib})")
            all_good = False
    
    return all_good

def check_folder_structure():
    """Verify folder structure is created"""
    required_dirs = ['data', 'features', 'models', 'notebooks', 'scripts', 'logs']
    all_good = True
    
    for folder in required_dirs:
        if Path(folder).exists() and Path(folder).is_dir():
            print(f"  ✓ {folder}/")
        else:
            print(f"  ✗ {folder}/ (missing)")
            all_good = False
    
    return all_good

def check_files():
    """Verify configuration files exist"""
    required_files = ['.env', '.gitignore', 'requirements.txt', 'README.md']
    all_good = True
    
    for filename in required_files:
        if Path(filename).exists():
            print(f"  ✓ {filename}")
        else:
            print(f"  ✗ {filename} (missing)")
            all_good = False
    
    return all_good

def check_env_configuration():
    """Check if .env has been configured"""
    if not Path('.env').exists():
        print("  ✗ .env file missing")
        return False
    
    with open('.env', 'r') as f:
        content = f.read()
    
    if 'your_oanda_api_key_here' in content or 'your_fred_api_key_here' in content:
        print("  ⚠ .env configured but needs API keys (see instructions)")
        return True  # File exists, just needs keys
    else:
        print("  ✓ .env appears to have API keys configured")
        return True

def main():
    print("=" * 60)
    print("GOLD ML TRADING BOT - Sprint 1 Setup Verification")
    print("=" * 60)
    
    checks = [
        ("Python Version", check_python_version),
        ("Required Libraries", check_libraries),
        ("Folder Structure", check_folder_structure),
        ("Configuration Files", check_files),
        (".env Configuration", check_env_configuration),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n{name}:")
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"  ✗ Error checking {name}: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(result for _, result in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ Sprint 1 Setup Complete!")
        print("\nNext steps:")
        print("1. Configure .env with your OANDA and FRED API keys")
        print("2. Start Sprint 2: Data Collection")
        print("3. Run: python3 scripts/collect_gold_ohlcv.py")
    else:
        print("✗ Some checks failed. Please fix issues above.")
        sys.exit(1)
    
    print("=" * 60)

if __name__ == '__main__':
    main()
