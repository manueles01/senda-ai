#!/usr/bin/env python3
"""
Test script to verify the Senda AI API is running correctly.
Run this while your uvicorn server is running on port 8000.
"""
import requests
import sys
from colorama import init, Fore, Style

# Initialize colorama for colored output
init(autoreset=True)

BASE_URL = "http://localhost:8000"

def print_success(message):
    print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")

def print_error(message):
    print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")

def print_info(message):
    print(f"{Fore.CYAN}ℹ {message}{Style.RESET_ALL}")

def test_endpoint(endpoint, description):
    """Test a single endpoint."""
    url = f"{BASE_URL}{endpoint}"
    print_info(f"Testing {description}: {url}")

    try:
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            print_success(f"Status: {response.status_code}")
            print_success(f"Response: {response.json()}")
            return True
        else:
            print_error(f"Unexpected status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error(f"Cannot connect to {url}")
        print_error("Is the server running? Start it with: uvicorn app.main:app --port 8000")
        return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def main():
    print(f"\n{Fore.YELLOW}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Senda AI API - System Test{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{'='*60}{Style.RESET_ALL}\n")

    tests = [
        ("/", "Root Endpoint"),
        ("/health", "Health Check Endpoint"),
        ("/docs", "API Documentation (Swagger)"),
    ]

    results = []
    for endpoint, description in tests:
        result = test_endpoint(endpoint, description)
        results.append(result)
        print()

    # Summary
    print(f"{Fore.YELLOW}{'='*60}{Style.RESET_ALL}")
    passed = sum(results)
    total = len(results)

    if passed == total:
        print_success(f"All tests passed! ({passed}/{total})")
        print_info(f"\nYour API is running correctly at {BASE_URL}")
        print_info(f"API Documentation: {BASE_URL}/docs")
        print_info(f"Redoc Documentation: {BASE_URL}/redoc")
        return 0
    else:
        print_error(f"Some tests failed ({passed}/{total} passed)")
        return 1

if __name__ == "__main__":
    sys.exit(main())
