#!/usr/bin/env python3
"""
Setup script to help configure environment variables for the trading dashboard API.
Run this script to set up your environment variables.
"""

import os
import secrets
import sys

def generate_jwt_secret():
    """Generate a secure JWT secret"""
    return secrets.token_urlsafe(32)

def setup_environment():
    """Setup environment variables"""
    print("🚀 Trading Dashboard API Environment Setup")
    print("=" * 50)
    
    # Check if .env file exists
    env_file = ".env"
    if os.path.exists(env_file):
        print(f"⚠️  {env_file} already exists. Backing up to {env_file}.backup")
        os.rename(env_file, f"{env_file}.backup")
    
    # Get Twelve Data API Key
    print("\n📊 Twelve Data API Configuration")
    print("Get your API key from: https://twelvedata.com/")
    twelve_data_key = input("Enter your Twelve Data API key: ").strip()
    
    if not twelve_data_key:
        print("❌ Twelve Data API key is required!")
        sys.exit(1)
    
    # Generate JWT Secret
    jwt_secret = generate_jwt_secret()
    print(f"🔐 Generated JWT secret: {jwt_secret}")
    
    # Create .env file
    env_content = f"""# Trading Dashboard API Environment Variables
# Generated on {os.popen('date').read().strip()}

# Twelve Data API Key
TWELVE_DATA_API_KEY={twelve_data_key}

# JWT Secret for authentication
JWT_SECRET={jwt_secret}

# Database URL (if using Prisma)
DATABASE_URL="postgresql://username:password@localhost:5432/trading_dashboard"
"""
    
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print(f"\n✅ Environment variables saved to {env_file}")
    print("\n📝 Next steps:")
    print("1. Activate your virtual environment: source venv/bin/activate")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Start the API server: uvicorn src.main:app --reload --host 0.0.0.0 --port 8080")
    print("\n🔗 Test your WebSocket connection at: ws://localhost:8080/ws/getlivedata")

if __name__ == "__main__":
    setup_environment()
