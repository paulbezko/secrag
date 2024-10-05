import json
import os

# Get the current directory of the script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Go one level up (parent directory)
parent_dir = os.path.dirname(current_dir)

# Convert to string if needed
parent_dir = str(parent_dir)

def clean_dict(input_dict):
    """
    Remove keys from the dictionary that have empty values.

    Args:
        input_dict (dict): The dictionary to clean.

    Returns:
        dict: A new dictionary with keys that have empty values removed.
    """
    return {key: value for key, value in input_dict.items() if value not in (None, '', [], {}, set())}

def clean_daughter_companies(input_dict):
    return {key: value for key, value in input_dict.items() if "-" not in key}

def sort_dict_keys(input_dict):
    """
    Sort the dictionary keys alphabetically.

    Args:
        input_dict (dict): The dictionary to sort.

    Returns:
        dict: A new dictionary with keys sorted alphabetically.
    """
    return {key: input_dict[key] for key in sorted(input_dict)}

def clean_filing_db():

    with open(current_dir+"/"+"filing_db.json", "r") as f:
        db = json.load(f)
        copy_db = dict(db)
        tickers = list(db["available_filings"].keys())

    with open(current_dir+"/"+"filing_db_backup.json", "w") as f:
        json.dump(db, f, indent=4)
        
    for ticker in copy_db["available_filings"].keys():
        for year in copy_db["available_filings"][ticker].keys():
            db["available_filings"][ticker][year] = [item for item in db["available_filings"][ticker][year] if "10-K" in item or "10-Q" in item]
        #     if not db["available_filings"][ticker][year]:
        #         del db["available_filings"][ticker][year]
        # if not bool(db["available_filings"][ticker]):
        #     del db["available_filings"][ticker]
        db["available_filings"][ticker] = clean_dict(db["available_filings"][ticker])
    
    db["available_filings"] = clean_dict(db["available_filings"])
    db["available_filings"] = clean_daughter_companies(db["available_filings"])
    db["available_filings"] = sort_dict_keys(db["available_filings"])
        # clean_dict(dict)

    with open(current_dir+"/"+"filing_db.json", "w") as f:
        json.dump(db, f, indent=4)

if __name__ == "__main__":
    clean_filing_db()