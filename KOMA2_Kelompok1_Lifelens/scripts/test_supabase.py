import os
import sys
from dotenv import load_dotenv
from supabase import create_client

# Add parent directory to sys.path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

def test_connection():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")
    
    if not url or not key:
        print("❌ Error: SUPABASE_URL or SUPABASE_SERVICE_KEY not found in .env")
        return
    
    print(f"Connecting to: {url}...")
    try:
        supabase = create_client(url, key)
        
        # Test 1: Basic connection
        print("Testing basic connection...")
        supabase.table("users").select("count", count="exact").limit(1).execute()
        print("✅ Connection successful!")
        
        # Test 2: Check tables
        tables = ["users", "sessions", "daily_features", "conversation_texts"]
        print("\nChecking tables:")
        for table in tables:
            try:
                supabase.table(table).select("*").limit(1).execute()
                print(f"✅ Table '{table}' exists.")
            except Exception as e:
                print(f"❌ Table '{table}' missing or error: {e}")
                
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    test_connection()
