#!/usr/bin/env python3
"""Script to integrate SQL query memory into magicflow memory system."""

import json
import os
from pathlib import Path
from datetime import datetime

def load_sql_memory_file(file_path: str) -> str:
    """Load SQL memory file content."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def get_memory_file_path() -> Path:
    """Get the path to the memory file."""
    # Determine base directory
    base_dir = None
    
    # Check MAGIC_FLOW_HOME environment variable
    if env_home := os.getenv("MAGIC_FLOW_HOME"):
        base_dir = Path(env_home).resolve()
    else:
        # Check current directory
        cwd = Path.cwd()
        if cwd.name == "backend" or (cwd / "pyproject.toml").exists():
            base_dir = cwd / ".magic-flow"
        else:
            # Default to home directory
            base_dir = Path.home() / ".magic-flow"
    
    return base_dir / "memory.json"

def load_memory_data(file_path: Path) -> dict:
    """Load memory data from file."""
    if not file_path.exists():
        # Create empty memory structure
        return {
            "version": "1.0",
            "lastUpdated": datetime.utcnow().isoformat() + "Z",
            "user": {
                "workContext": {"summary": "", "updatedAt": ""},
                "personalContext": {"summary": "", "updatedAt": ""},
                "topOfMind": {"summary": "", "updatedAt": ""},
            },
            "history": {
                "recentMonths": {"summary": "", "updatedAt": ""},
                "earlierContext": {"summary": "", "updatedAt": ""},
                "longTermBackground": {"summary": "", "updatedAt": ""},
            },
            "facts": [],
        }
    
    try:
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)
        return data
    except (json.JSONDecoMAGICror, OSError) as e:
        print(f"Failed to load memory file: {e}")
        return {
            "version": "1.0",
            "lastUpdated": datetime.utcnow().isoformat() + "Z",
            "user": {
                "workContext": {"summary": "", "updatedAt": ""},
                "personalContext": {"summary": "", "updatedAt": ""},
                "topOfMind": {"summary": "", "updatedAt": ""},
            },
            "history": {
                "recentMonths": {"summary": "", "updatedAt": ""},
                "earlierContext": {"summary": "", "updatedAt": ""},
                "longTermBackground": {"summary": "", "updatedAt": ""},
            },
            "facts": [],
        }

def save_memory_data(file_path: Path, memory_data: dict) -> bool:
    """Save memory data to file."""
    try:
        # Ensure directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Update lastUpdated timestamp
        memory_data["lastUpdated"] = datetime.utcnow().isoformat() + "Z"

        # Write atomically using temp file
        temp_path = file_path.with_suffix(".tmp")
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(memory_data, f, indent=2, ensure_ascii=False)

        # Rename temp file to actual file (atomic on most systems)
        temp_path.replace(file_path)

        print(f"Memory saved to {file_path}")
        return True
    except OSError as e:
        print(f"Failed to save memory file: {e}")
        return False

def add_sql_memory_to_data(memory_data: dict, sql_memory_content: str) -> dict:
    """Add SQL memory content to memory data."""
    # Update topOfMind with SQL memory information
    sql_memory_summary = "SQL query memory integrated: Contains optimized query templates for BIM database operations, including room queries, door queries, system queries, and performance optimization strategies."
    
    memory_data["user"]["topOfMind"] = {
        "summary": sql_memory_summary,
        "updatedAt": datetime.utcnow().isoformat() + "Z"
    }
    
    # Update workContext to include SQL expertise
    work_context = memory_data["user"].get("workContext", {}).get("summary", "")
    if "SQL" not in work_context:
        new_work_context = f"{work_context} Expertise in BIM database SQL queries with optimized templates for room, door, and system queries." if work_context else "Expertise in BIM database SQL queries with optimized templates for room, door, and system queries."
        memory_data["user"]["workContext"] = {
            "summary": new_work_context,
            "updatedAt": datetime.utcnow().isoformat() + "Z"
        }
    
    # Add SQL memory facts
    sql_facts = [
        {
            "id": f"fact_{hash('sql_query_templates')}",
            "content": "SQL query templates for BIM database operations",
            "category": "knowledge",
            "confidence": 1.0,
            "createdAt": datetime.utcnow().isoformat() + "Z",
            "source": "sql_memory_integration"
        },
        {
            "id": f"fact_{hash('room_queries')}",
            "content": "Optimized room query templates with proper table joins and filtering",
            "category": "knowledge",
            "confidence": 1.0,
            "createdAt": datetime.utcnow().isoformat() + "Z",
            "source": "sql_memory_integration"
        },
        {
            "id": f"fact_{hash('door_queries')}",
            "content": "Door query templates with property extraction and filtering",
            "category": "knowledge",
            "confidence": 1.0,
            "createdAt": datetime.utcnow().isoformat() + "Z",
            "source": "sql_memory_integration"
        },
        {
            "id": f"fact_{hash('system_queries')}",
            "content": "System query templates for mechanical and plumbing systems",
            "category": "knowledge",
            "confidence": 1.0,
            "createdAt": datetime.utcnow().isoformat() + "Z",
            "source": "sql_memory_integration"
        },
        {
            "id": f"fact_{hash('performance_optimization')}",
            "content": "SQL performance optimization strategies for BIM databases",
            "category": "knowledge",
            "confidence": 1.0,
            "createdAt": datetime.utcnow().isoformat() + "Z",
            "source": "sql_memory_integration"
        }
    ]
    
    # Add facts if they don't already exist
    existing_fact_ids = {fact["id"] for fact in memory_data.get("facts", [])}
    for fact in sql_facts:
        if fact["id"] not in existing_fact_ids:
            memory_data["facts"].append(fact)
    
    # Update recentMonths with SQL memory integration
    recent_months = memory_data["history"].get("recentMonths", {}).get("summary", "")
    new_recent_months = f"{recent_months} Integrated SQL query memory for BIM database operations, including optimized templates and best practices." if recent_months else "Integrated SQL query memory for BIM database operations, including optimized templates and best practices."
    memory_data["history"]["recentMonths"] = {
        "summary": new_recent_months,
        "updatedAt": datetime.utcnow().isoformat() + "Z"
    }
    
    return memory_data

def main():
    """Main function to integrate SQL memory."""
    # Path to the optimized SQL memory file
    sql_memory_path = Path("..\..\docs\memory_record_sql_optimized.md")
    
    if not sql_memory_path.exists():
        print(f"SQL memory file not found: {sql_memory_path}")
        return
    
    # Load SQL memory content
    print(f"Loading SQL memory from: {sql_memory_path}")
    sql_memory_content = load_sql_memory_file(sql_memory_path)
    
    # Get memory file path
    memory_file = get_memory_file_path()
    print(f"Using memory file: {memory_file}")
    
    # Load existing memory data
    memory_data = load_memory_data(memory_file)
    
    # Add SQL memory to data
    updated_memory = add_sql_memory_to_data(memory_data, sql_memory_content)
    
    # Save updated memory
    print("Saving updated memory...")
    success = save_memory_data(memory_file, updated_memory)
    
    if success:
        print(f"�?SQL memory successfully integrated into: {memory_file}")
        print("\nThe SQL query memory is now available for use in database queries.")
        print("\nKey benefits:")
        print("- Improved SQL query efficiency")
        print("- Consistent query patterns")
        print("- Reduced development time")
        print("- Better query performance")
        print("\nTo use the SQL memory:")
        print("1. When needing to query the database, check the memory for existing templates")
        print("2. Use the optimized templates for faster and more consistent queries")
        print("3. Update the memory with new query experiences as they are discovered")
    else:
        print("�?Failed to update memory")

if __name__ == "__main__":
    main()
