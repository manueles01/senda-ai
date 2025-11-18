#!/usr/bin/env python3
"""
Check configuration and environment variables.
This script tests that your .env file is set up correctly.
"""
import sys
import os
from pathlib import Path

# Add the apps/api directory to the path
sys.path.insert(0, str(Path(__file__).parent / "apps" / "api"))

try:
    from app.config import settings
    from colorama import init, Fore, Style
    init(autoreset=True)

    def print_success(message):
        print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")

    def print_warning(message):
        print(f"{Fore.YELLOW}⚠ {message}{Style.RESET_ALL}")

    def print_info(message):
        print(f"{Fore.CYAN}ℹ {message}{Style.RESET_ALL}")

    def mask_secret(value, show_chars=4):
        """Mask sensitive values, showing only first few characters."""
        if not value or value == "":
            return "<not set>"
        str_value = str(value)
        if len(str_value) <= show_chars:
            return "*" * len(str_value)
        return str_value[:show_chars] + "*" * (len(str_value) - show_chars)

    print(f"\n{Fore.YELLOW}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Senda AI - Configuration Check{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{'='*60}{Style.RESET_ALL}\n")

    # Check .env file exists
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        print_success(f".env file found at: {env_file}")
    else:
        print_warning(f".env file not found at: {env_file}")
        print_warning("Create it by running: cp .env.example .env")

    print()

    # Application Settings
    print_info("Application Settings:")
    print(f"  App Name: {settings.app_name}")
    print(f"  Debug Mode: {settings.debug}")
    print()

    # API Keys and Credentials
    print_info("API Configuration:")

    configs = [
        ("Anthropic API Key", settings.anthropic_api_key, True),
        ("Firebase Project ID", settings.firebase_project_id, False),
        ("Phorest Base URL", settings.phorest_base_url, False),
        ("Phorest Username", settings.phorest_username, True),
        ("Phorest Password", settings.phorest_password, True),
        ("Phorest Business ID", settings.phorest_business_id, False),
        ("Phorest Branch ID", settings.phorest_branch_id, False),
        ("Telnyx API Key", settings.telephony_telnyx_api_key, True),
        ("Google Project ID", settings.google_project_id, False),
        ("Gemini Model", settings.gemini_model, False),
    ]

    configured_count = 0
    total_count = len(configs)

    for name, value, is_sensitive in configs:
        if value and value != "":
            print_success(f"  {name}: {mask_secret(value) if is_sensitive else value}")
            configured_count += 1
        else:
            print_warning(f"  {name}: <not configured>")

    print()
    print(f"{Fore.YELLOW}{'='*60}{Style.RESET_ALL}")

    if configured_count == total_count:
        print_success(f"All settings configured! ({configured_count}/{total_count})")
    else:
        print_warning(f"Some settings not configured ({configured_count}/{total_count})")
        print_info("Optional settings can be left empty if not needed")

    print()
    print_info("Configuration loaded successfully!")
    print_info("You can now start the server with: uvicorn app.main:app --port 8000")

except ImportError as e:
    print(f"{Fore.RED}Error importing settings: {e}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Make sure you're running this from the repository root{Style.RESET_ALL}")
    sys.exit(1)
except Exception as e:
    print(f"{Fore.RED}Error loading configuration: {e}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Check your .env file and apps/api/app/config.py{Style.RESET_ALL}")
    sys.exit(1)
