import json
import os

def add_to_database(journal_name, abbreviation):
    # File name
    database_file = 'new_database.json'
    
    # Check if the file exists
    if os.path.exists(database_file):
        with open(database_file, 'r') as f:
            data = json.load(f)
    else:
        data = {}
    
    # Add/Update the journal name and abbreviation
    data[journal_name] = abbreviation
    
    # Write back to the file
    with open(database_file, 'w') as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    journal_name = input("Enter the journal name: ")
    abbreviation = input(f"Enter the abbreviation: ")
    add_to_database(journal_name, abbreviation)
    print(f"Success.")
