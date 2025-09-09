#!/usr/bin/env python3
"""
🔐 Secret Key Generator for Flask Applications

This script generates secure secret keys for your Employee Leave Management System.
"""

import secrets
import string
import os
import base64

def generate_secret_key(length=32, method="default"):
    """Generate a secure secret key using different methods."""
    
    if method == "default":
        # Method 1: Using secrets.token_hex() - Most common
        return secrets.token_hex(length)
    
    elif method == "urlsafe":
        # Method 2: Using secrets.token_urlsafe() - URL safe
        return secrets.token_urlsafe(length)
    
    elif method == "bytes":
        # Method 3: Using secrets.token_bytes() with base64
        return base64.urlsafe_b64encode(secrets.token_bytes(length)).decode('utf-8')
    
    elif method == "custom":
        # Method 4: Custom alphabet
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))

def main():
    print("🔐 Flask Secret Key Generator")
    print("=" * 50)
    print()
    
    # Generate different types of secret keys
    print("📋 Generated Secret Keys (choose any one):")
    print()
    
    print("1️⃣ Default (Recommended for Flask):")
    key1 = generate_secret_key(32, "default")
    print(f"   {key1}")
    print()
    
    print("2️⃣ URL Safe:")
    key2 = generate_secret_key(32, "urlsafe")
    print(f"   {key2}")
    print()
    
    print("3️⃣ Base64 Encoded:")
    key3 = generate_secret_key(24, "bytes")
    print(f"   {key3}")
    print()
    
    print("4️⃣ Custom Characters:")
    key4 = generate_secret_key(40, "custom")
    print(f"   {key4}")
    print()
    
    print("💡 How to use:")
    print("   1. Copy ONE of the keys above")
    print("   2. Use it as your SECRET_KEY environment variable")
    print("   3. For Render: Add it in Environment Variables section")
    print("   4. For local development: Add to .env file")
    print()
    
    print("🔒 Security Tips:")
    print("   ✅ Never commit secret keys to Git")
    print("   ✅ Use different keys for development and production")
    print("   ✅ Keep keys secure and private")
    print("   ✅ Regenerate keys if compromised")
    print()
    
    # Show environment variable examples
    print("📝 Environment Variable Examples:")
    print()
    print("For .env file (local development):")
    print(f"SECRET_KEY={key1}")
    print()
    print("For Render deployment:")
    print("   Variable Name: SECRET_KEY")
    print(f"   Variable Value: {key1}")
    print()
    
    # Alternative method using Python directly
    print("🐍 Generate in Python shell:")
    print("   >>> import secrets")
    print("   >>> secrets.token_hex(32)")
    print()
    
    print("🌐 Online generators (use with caution):")
    print("   - https://flask.palletsprojects.com/quickstart/#sessions")
    print("   - Generate locally for better security!")

if __name__ == "__main__":
    main()
