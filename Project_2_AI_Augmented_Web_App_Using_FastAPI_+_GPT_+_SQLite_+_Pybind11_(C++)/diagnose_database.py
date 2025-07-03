#!/usr/bin/env python3
"""
Database diagnostic script for AI Text Analyzer
This script helps identify and fix database-related issues
"""

import sqlite3
import json
import os
from datetime import datetime

def check_database_exists():
    """Check if the database file exists"""
    db_file = "analyzer.db"
    if os.path.exists(db_file):
        size = os.path.getsize(db_file)
        print(f"✅ Database file exists: {db_file} ({size} bytes)")
        return True
    else:
        print(f"❌ Database file not found: {db_file}")
        return False

def check_database_schema():
    """Check the database schema"""
    print("\n🔍 Checking database schema...")
    
    try:
        conn = sqlite3.connect('analyzer.db')
        cursor = conn.cursor()
        
        # Check if analyses table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='analyses'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("❌ 'analyses' table does not exist")
            conn.close()
            return False
        
        print("✅ 'analyses' table exists")
        
        # Get table schema
        cursor.execute("PRAGMA table_info(analyses)")
        columns = cursor.fetchall()
        
        print("\n📊 Table schema:")
        for col in columns:
            print(f"   {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULL'} - {'PRIMARY KEY' if col[5] else ''}")
        
        # Check for required columns
        column_names = [col[1] for col in columns]
        required_columns = ['id', 'text', 'cpp_result', 'timestamp']
        optional_columns = ['ai_suggestions', 'ai_provider', 'gpt_suggestions']
        
        missing_required = [col for col in required_columns if col not in column_names]
        if missing_required:
            print(f"❌ Missing required columns: {missing_required}")
            conn.close()
            return False
        
        print("✅ All required columns present")
        
        # Check which optional columns are present
        present_optional = [col for col in optional_columns if col in column_names]
        print(f"📋 Optional columns present: {present_optional}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Schema check failed: {e}")
        return False

def check_database_content():
    """Check database content"""
    print("\n📊 Checking database content...")
    
    try:
        conn = sqlite3.connect('analyzer.db')
        cursor = conn.cursor()
        
        # Count total records
        cursor.execute("SELECT COUNT(*) FROM analyses")
        total_count = cursor.fetchone()[0]
        print(f"📈 Total analyses: {total_count}")
        
        if total_count == 0:
            print("ℹ️ Database is empty - no analyses found")
            conn.close()
            return True
        
        # Get recent records
        cursor.execute("SELECT * FROM analyses ORDER BY timestamp DESC LIMIT 5")
        recent_records = cursor.fetchall()
        
        print(f"\n📋 Recent records (showing {len(recent_records)}):")
        for i, record in enumerate(recent_records, 1):
            print(f"   {i}. ID: {record[0]}, Text: '{record[1][:50]}...', Timestamp: {record[-1]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Content check failed: {e}")
        return False

def test_database_queries():
    """Test the actual queries used by the application"""
    print("\n🧪 Testing database queries...")
    
    try:
        conn = sqlite3.connect('analyzer.db')
        cursor = conn.cursor()
        
        # Check table schema first
        cursor.execute("PRAGMA table_info(analyses)")
        columns_info = cursor.fetchall()
        column_names = [col[1] for col in columns_info]
        
        has_ai_provider = 'ai_provider' in column_names
        has_ai_suggestions = 'ai_suggestions' in column_names
        has_gpt_suggestions = 'gpt_suggestions' in column_names
        
        print(f"   Schema check: ai_provider={has_ai_provider}, ai_suggestions={has_ai_suggestions}, gpt_suggestions={has_gpt_suggestions}")
        
        # Test the new query format
        if has_ai_provider and has_ai_suggestions:
            print("   Testing new schema query...")
            cursor.execute("SELECT id, text, cpp_result, ai_suggestions, ai_provider, datetime(timestamp) as formatted_timestamp FROM analyses ORDER BY timestamp DESC LIMIT 3")
        else:
            print("   Testing old schema query...")
            cursor.execute("SELECT id, text, cpp_result, gpt_suggestions, NULL as ai_provider, datetime(timestamp) as formatted_timestamp FROM analyses ORDER BY timestamp DESC LIMIT 3")
        
        rows = cursor.fetchall()
        print(f"✅ Query successful, returned {len(rows)} rows")
        
        # Test JSON serialization
        formatted_rows = []
        for row in rows:
            formatted_rows.append({
                "id": row[0],
                "text": row[1],
                "cpp_result": row[2],
                "ai_suggestions": row[3],
                "ai_provider": row[4],
                "timestamp": row[5]
            })
        
        json_string = json.dumps(formatted_rows)
        print(f"✅ JSON serialization successful ({len(json_string)} characters)")
        
        # Test JSON parsing
        parsed_back = json.loads(json_string)
        print(f"✅ JSON parsing successful, {len(parsed_back)} items")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Query test failed: {e}")
        return False

def create_test_data():
    """Create some test data if database is empty"""
    print("\n🔧 Creating test data...")
    
    try:
        conn = sqlite3.connect('analyzer.db')
        cursor = conn.cursor()
        
        # Check if we already have data
        cursor.execute("SELECT COUNT(*) FROM analyses")
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"ℹ️ Database already has {count} records, skipping test data creation")
            conn.close()
            return True
        
        # Create test data
        test_analyses = [
            ("This is a test sentence for analysis.", '{"word_count": 7, "sentence_count": 1, "readability_score": 0.8, "sentiment_score": 0.5}', "This text is clear and concise.", "openai"),
            ("Another example text for testing purposes.", '{"word_count": 6, "sentence_count": 1, "readability_score": 0.7, "sentiment_score": 0.6}', "Consider adding more descriptive words.", "gemini"),
            ("A third test without AI suggestions.", '{"word_count": 6, "sentence_count": 1, "readability_score": 0.9, "sentiment_score": 0.5}', None, None),
        ]
        
        # Check schema to determine which columns to use
        cursor.execute("PRAGMA table_info(analyses)")
        columns_info = cursor.fetchall()
        column_names = [col[1] for col in columns_info]
        
        if 'ai_suggestions' in column_names and 'ai_provider' in column_names:
            # New schema
            for text, cpp_result, ai_suggestions, ai_provider in test_analyses:
                cursor.execute(
                    "INSERT INTO analyses (text, cpp_result, ai_suggestions, ai_provider) VALUES (?, ?, ?, ?)",
                    (text, cpp_result, ai_suggestions, ai_provider)
                )
        else:
            # Old schema
            for text, cpp_result, ai_suggestions, ai_provider in test_analyses:
                cursor.execute(
                    "INSERT INTO analyses (text, cpp_result, gpt_suggestions) VALUES (?, ?, ?)",
                    (text, cpp_result, ai_suggestions)
                )
        
        conn.commit()
        conn.close()
        
        print(f"✅ Created {len(test_analyses)} test records")
        return True
        
    except Exception as e:
        print(f"❌ Test data creation failed: {e}")
        return False

def main():
    """Run all diagnostic checks"""
    print("🔍 AI Text Analyzer - Database Diagnostic")
    print("=" * 50)
    
    checks = [
        ("Database File", check_database_exists),
        ("Database Schema", check_database_schema),
        ("Database Content", check_database_content),
        ("Database Queries", test_database_queries),
    ]
    
    results = []
    
    for check_name, check_func in checks:
        print(f"\n🔍 {check_name}...")
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ {check_name} failed with exception: {e}")
            results.append((check_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 DIAGNOSTIC SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{check_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} checks passed")
    
    # Recommendations
    print("\n" + "=" * 50)
    print("💡 RECOMMENDATIONS")
    print("=" * 50)
    
    if passed == total:
        print("✅ Database appears to be working correctly!")
        print("If you're still getting errors, try:")
        print("1. Restart the server: python main.py")
        print("2. Clear browser cache and refresh")
        print("3. Check browser console for JavaScript errors")
    else:
        print("⚠️ Database issues detected. Try these fixes:")
        print("1. Run database migration: python migrate_database.py")
        print("2. Create test data: python diagnose_database.py (will create test data)")
        print("3. Check file permissions on analyzer.db")
        print("4. Restart the application")
    
    # Offer to create test data
    if passed >= 2:  # If basic checks pass
        response = input("\n❓ Create test data for testing? (y/N): ")
        if response.lower() == 'y':
            create_test_data()

if __name__ == "__main__":
    main()
