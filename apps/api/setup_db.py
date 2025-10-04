#!/usr/bin/env python3
"""
Simple database setup script for Render deployment
"""
import os
import sys
from prisma import Prisma

async def setup_database():
    """Setup database connection and run migrations"""
    try:
        # Check if database URL is provided
        database_url = os.getenv("DIRECT_URL")
        if not database_url:
            print("WARNING: No DIRECT_URL environment variable found")
            print("Please set DIRECT_URL in your Render environment variables")
            print("Example: postgresql://user:password@host:port/database")
            return False
        
        print(f"Connecting to database...")
        prisma = Prisma()
        
        # Try to connect
        await prisma.connect()
        print("✅ Database connection successful!")
        
        # Test a simple query
        users = await prisma.user.find_many()
        print(f"✅ Database query successful! Found {len(users)} users")
        
        await prisma.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    import asyncio
    success = asyncio.run(setup_database())
    sys.exit(0 if success else 1)
