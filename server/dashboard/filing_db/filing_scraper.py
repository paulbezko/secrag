import os
import json
from datetime import datetime, timezone
import pytz
import requests
from dateutil.relativedelta import relativedelta
import traceback
from filing_cleaner import sort_dict_keys



from edgar import get_filings
from edgar.core import set_identity

# Get the current directory of the script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Go one level up (parent directory)
parent_dir = os.path.dirname(current_dir)

# Convert to string if needed
parent_dir = str(parent_dir)

def scrape_filings(mode="month", mode_amount=1):
    available_modes = ["month", "ytd", "year", "day"]

    if mode not in available_modes:
        raise Exception(f"Invalid mode: {mode}. Available modes: {available_modes}")

    cik_ticker_list, added_tickers = update_ticker_json()

    ciks = [tup[0] for tup in cik_ticker_list]
    cik_ticker_dict = dict(cik_ticker_list)

    set_identity("{} {}".format("marks", "marksdocenko@outlook.com"))

    with open(current_dir +"/filing_db.json", "r") as f:
        data = json.load(f)

    current_utc_time = datetime.now(tz=timezone.utc)
    data["last_update"] = current_utc_time.strftime("%Y-%m-%d %H:%M:%S")

    filings = get_filings(form=["10-K", "10-Q"])

    if mode != "ytd":
        # Define the Eastern Time timezone
        eastern_tz = pytz.timezone('America/New_York')

        # Get the current time in UTC
        utc_now = datetime.now(pytz.utc)

        # Convert UTC time to Eastern Time. SEC uses ET
        end_time = utc_now.astimezone(eastern_tz)
        if mode == "month":
            start_time = end_time - relativedelta(months=mode_amount)
        elif mode == "day": 
            start_time = end_time - relativedelta(days=mode_amount)
        elif mode == "year":
            start_time = end_time - relativedelta(years=mode_amount)    
        else:
            raise Exception(f"Invalid mode injected: {mode}. Available modes: {available_modes}")
        end_time_str = end_time.strftime('%Y-%m-%d')
        start_time_str = start_time.strftime('%Y-%m-%d') 

        filings = filings.filter(date=f"{start_time_str}:{end_time_str}", cik = ciks, form=["10-K", "10-Q"])
        with open(current_dir +"/filing_db.json", "r") as f:
            filing_db = json.load(f)
        
        with open(current_dir+"/"+"filing_db_backup.json", "w") as f:
            json.dump(filing_db, f, indent=4)

        with open(current_dir +"/new_filings_db.json", "r") as f:
            new_filings_db = json.load(f)        
        new_filings = []
        for filing in filings:
            filing_db_str = f"{filing.form} {str(filing.filing_date)}"
            if "-" not in cik_ticker_dict[filing.cik]:
                try:
                    if cik_ticker_dict[filing.cik] not in filing_db["available_filings"]:
                        filing_db["available_filings"][cik_ticker_dict[filing.cik]] = {}
                    if str(filing.filing_date.year) not in filing_db["available_filings"][cik_ticker_dict[filing.cik]]:
                        new_dict_entry = {filing.filing_date.year : []}
                        filing_db["available_filings"][cik_ticker_dict[filing.cik]].update(new_dict_entry)
                    if filing_db_str not in filing_db["available_filings"][cik_ticker_dict[filing.cik]][str(filing.filing_date.year)]:
                        filing_db["available_filings"][cik_ticker_dict[filing.cik]][str(filing.filing_date.year)].append(filing_db_str)
                        new_filings.append(f"{cik_ticker_dict[filing.cik]} {filing_db_str}")
                except Exception as e:
                    print(cik_ticker_dict[filing.cik], filing.filing_date.year)
                    raise e
        
        if added_tickers:
            filing_db["available_filings"] = sort_dict_keys(filing_db["available_filings"])

        with open(current_dir +"/filing_db.json", "w") as f:
            json.dump(filing_db,f,indent=4)
        
        if new_filings:
            with open(current_dir +"/new_filings_db.json", "w") as f:
                current_time = datetime.now(tz=timezone.utc).strftime('%Y-%m-%d')
                new_filings_db["data"] = new_filings
                new_filings_db["last_modified"] = current_time
                json.dump(new_filings_db, f, indent=4)
        
        print(f"Finished scraping!\n New filings: \n{new_filings}")
        

    
def update_ticker_json():
    try:
        url = 'https://www.sec.gov/files/company_tickers.json'
        headers = {
            'User-Agent': 'marks marksdocenko@outlook.com'
        }

        response = requests.get(url, headers=headers)
        current_cik_ticker_list = get_cik_ticker_list()

        if response.status_code == 200:
            new_cik_ticker_list = get_cik_ticker_list(response.text)
            added_tickers, removed_tickers = compare_cik_ticker_lists(old_list=current_cik_ticker_list, new_list=new_cik_ticker_list)
            
            current_time = datetime.now(tz=timezone.utc)
            with open(current_dir+'/added_removed_tickers.json', 'r') as json_file:
                added_removed_tickers_data = json.load(json_file)
            added_removed_tickers_data["data"].append({
                "update_time" : current_time.strftime('%Y-%m-%d'),
                "added_tickers" : added_tickers, 
                "removed_tickers": removed_tickers
            })
            with open(current_dir+'/added_removed_tickers.json', 'w') as json_file:
                json.dump(added_removed_tickers_data, json_file, indent=4)

            # Save the JSON content to a file
            with open(current_dir+'/company_tickers.json', 'w') as json_file:
                json_data = json.loads(response.text)
                json.dump(json_data, json_file, indent=4)
            print(f"Updated ticker json\n\nAdded tickers: \n{added_tickers}\n\nRemoved tickers: \n{removed_tickers}")
            return new_cik_ticker_list, added_tickers
        else:
            current_time = datetime.now(tz=timezone.utc)
            error_str = f"Error: Request failed\nStatus code: {response.status_code} \n\n Text: {response.text}"
            with open(current_dir+'/'+f"UCT_fail_log_{current_time.strftime('%Y-%m-%d_%H-%M-%S')}.txt", "w") as f:
                f.write(error_str)
            raise Exception(error_str)
    except Exception as e:  
        current_time = datetime.now(tz=timezone.utc)
        with open(current_dir+ f"/logs/UCT_fail_log_{current_time.strftime('%Y-%m-%d_%H-%M-%S')}.txt", "w") as f:
            f.write(f"Error: {str(e)}\n\nTraceback: {traceback.format_exc()}")  
        raise e  

def compare_cik_ticker_lists(old_list : list, new_list : list):
    # Extract the first values from each tuple for comparison
    old_keys = {t[0] for t in old_list}
    new_keys = {t[0] for t in new_list}
    
    # Find added keys
    added_keys = [t for t in new_list if t[0] not in old_keys]
    
    # Find removed keys
    removed_keys = [t for t in old_list if t[0] not in new_keys]
    
    return dict(added_keys), dict(removed_keys)


def get_cik_ticker_list(data : str = None):
    cik_ticker = []
    if not data:
        with open(current_dir +"/company_tickers.json", "r") as f:
            data = json.load(f)

    else:
        data = json.loads(data)

    for key in data.keys():
        cik_ticker.append((data[key]["cik_str"], data[key]["ticker"]))

    return cik_ticker


if __name__ == "__main__":
    scrape_filings(mode="month", mode_amount=2)