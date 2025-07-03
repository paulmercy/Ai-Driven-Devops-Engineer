#!/usr/bin/env python3
"""
Database migration script for AI Text Analyzer
Migrates existing database to support new AI provider tracking
"""

import sqlite3
import os
from datetime import datetime

def backup_database(db_path):
    """Create a backup of the existing database"""
    if not os.path.exists(db_path):
        print(f"Database {db_path} does not exist. No migration needed.")
        return False
    
    backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        # Create backup
        with open(db_path, 'rb') as src, open(backup_path, 'wb') as dst:
            dst.write(src.read())
        print(f"✓ Database backed up to: {backup_path}")
        return True
    except Exception as e:
        print(f"✗ Failed to backup database: {e}")
        return False

def check_schema(db_path):
    """Check if the database needs migration"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if ai_provider column exists
        cursor.execute("PRAGMA table_info(analyses)")
        columns = [column[1] for column in cursor.fetchall()]
        
        conn.close()
        
        has_ai_provider = 'ai_provider' in columns
        has_ai_suggestions = 'ai_suggestions' in columns
        has_gpt_suggestions = 'gpt_suggestions' in columns
        
        return {
            'needs_migration': not (has_ai_provider and has_ai_suggestions),
            'has_ai_provider': has_ai_provider,
            'has_ai_suggestions': has_ai_suggestions,
            'has_gpt_suggestions': has_gpt_suggestions,
            'columns': columns
        }
        
    except Exception as e:
        print(f"Error checking schema: {e}")
        return None

def migrate_database(db_path):
    """Migrate the database to the new schema"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        schema_info = check_schema(db_path)
        if not schema_info:
            return False
        
        print("Current schema:", schema_info['columns'])
        
        # Add ai_provider column if it doesn't exist
        if not schema_info['has_ai_provider']:
            print("Adding ai_provider column...")
            cursor.execute("ALTER TABLE analyses ADD COLUMN ai_provider TEXT")
            
            # Set default provider for existing records with gpt_suggestions
            if schema_info['has_gpt_suggestions']:
                cursor.execute("""
                    UPDATE analyses 
                    SET ai_provider = 'openai' 
                    WHERE gpt_suggestions IS NOT NULL AND gpt_suggestions != ''
                """)
                print("✓ Set ai_provider to 'openai' for existing records with GPT suggestions")
        
        # Add ai_suggestions column if it doesn't exist
        if not schema_info['has_ai_suggestions']:
            print("Adding ai_suggestions column...")
            cursor.execute("ALTER TABLE analyses ADD COLUMN ai_suggestions TEXT")
            
            # Copy data from gpt_suggestions if it exists
            if schema_info['has_gpt_suggestions']:
                cursor.execute("UPDATE analyses SET ai_suggestions = gpt_suggestions")
                print("✓ Copied gpt_suggestions to ai_suggestions")
        
        conn.commit()
        conn.close()
        
        print("✓ Database migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        return False

def verify_migration(db_path):
    """Verify that the migration was successful"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check final schema
        cursor.execute("PRAGMA table_info(analyses)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Check data
        cursor.execute("SELECT COUNT(*) FROM analyses")
        total_records = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM analyses WHERE ai_provider IS NOT NULL")
        records_with_provider = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"\nMigration Verification:")
        print(f"✓ Final schema: {columns}")
        print(f"✓ Total records: {total_records}")
        print(f"✓ Records with AI provider: {records_with_provider}")
        
        required_columns = ['id', 'text', 'cpp_result', 'ai_suggestions', 'ai_provider', 'timestamp']
        missing_columns = [col for col in required_columns if col not in columns]
        
        if missing_columns:
            print(f"✗ Missing columns: {missing_columns}")
            return False
        else:
            print("✓ All required columns present")
            return True
            
    except Exception as e:
        print(f"✗ Verification failed: {e}")
        return False

def main():
    """Main migration function"""
    db_path = "analyzer.db"
    
    print("AI Text Analyzer Database Migration")
    print("=" * 40)
    
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"Database {db_path} does not exist.")
        print("No migration needed. The new schema will be created when you run the application.")
        return
    
    # Check current schema
    schema_info = check_schema(db_path)
    if not schema_info:
        print("Failed to check database schema.")
        return
    
    if not schema_info['needs_migration']:
        print("✓ Database is already up to date!")
        return
    
    print("Database migration required.")
    print(f"Current columns: {schema_info['columns']}")
    
    # Ask for confirmation
    response = input("\nProceed with migration? This will modify your database. (y/N): ")
    if response.lower() != 'y':
        print("Migration cancelled.")
        return
    
    # Create backup
    if not backup_database(db_path):
        print("Failed to create backup. Migration cancelled for safety.")
        return
    
    # Perform migration
    if migrate_database(db_path):
        # Verify migration
        if verify_migration(db_path):
            print("\n✅ Migration completed successfully!")
            print("You can now run the updated application.")
        else:
            print("\n⚠ Migration completed but verification failed.")
            print("Please check your database manually.")
    else:
        print("\n❌ Migration failed.")
        print("Your original database backup is available.")

if __name__ == "__main__":
    main()
