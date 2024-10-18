from dateutil.relativedelta import relativedelta
from edgar.core import set_identity
from datetime import datetime, timezone
from logger import log, configure_logger
from edgar import get_filings

import traceback
import requests
import logging
import json
import pytz
import os

# Get the current directory of the script
log_filename = os.path.join("crons/logs", f"filing_scraper.log")
configure_logger(log_filename)

current_dir = os.path.dirname(os.path.abspath(__file__))
data_directory = "database/memory"

def scrape_filings(mode="month", mode_amount=1):
    available_modes = ["month", "ytd", "year", "day"]

    if mode not in available_modes:
        raise Exception(f"Invalid mode: {mode}. Available modes: {available_modes}")

    cik_ticker_list, added_tickers = update_ticker_json()

    ciks = [tup[0] for tup in cik_ticker_list]
    cik_ticker_dict = dict(cik_ticker_list)

    set_identity("{} {}".format("marks", "marksdocenko@outlook.com"))

    with open(data_directory +"/filings_available.json", "r") as f:
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
        with open(data_directory +"/filings_available.json", "r") as f:
            filings_available = json.load(f)
        
        with open(data_directory+"/"+"filings_available_backup.json", "w") as f:
            json.dump(filings_available, f, indent=4)

        with open(data_directory +"/filings_available.json", "r") as f:
            filings_new = json.load(f)

        new_filings = []
        for filing in filings:
            filings_available_str = f"{filing.form} {str(filing.filing_date)}"
            if "-" not in cik_ticker_dict[filing.cik]:
                try:
                    if cik_ticker_dict[filing.cik] not in filings_available:
                        filings_available[cik_ticker_dict[filing.cik]] = {}
                    if str(filing.filing_date.year) not in filings_available[cik_ticker_dict[filing.cik]]:
                        new_dict_entry = {str(filing.filing_date.year) : []}
                        filings_available[cik_ticker_dict[filing.cik]].update(new_dict_entry)
                    if filings_available_str not in filings_available[cik_ticker_dict[filing.cik]][str(filing.filing_date.year)]:
                        filings_available[cik_ticker_dict[filing.cik]][str(filing.filing_date.year)].append(filings_available_str)
                        new_filings.append(f"{cik_ticker_dict[filing.cik]} {filings_available_str}")
                except Exception as e:
                    log("error", f"{str(e)}\n\nTraceback: {traceback.format_exc()}")
                    raise e
        
        if added_tickers:
            filings_available = sort_dict_keys(filings_available)

        with open(data_directory +"/filings_available.json", "w") as f:
            json.dump(filings_available,f,indent=4)
        
        if new_filings:
            with open(data_directory +"/filings_new.json", "w") as f:
                filings_new = new_filings
                json.dump(filings_new, f, indent=4)
        
        log("debug", f"New filings: {len(new_filings)}")
        

    
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

            # Save the JSON content to a file
            with open(data_directory+'/company_tickers.json', 'w') as json_file:
                json_data = json.loads(response.text)
                json.dump(json_data, json_file, indent=4)

            log("debug", f"Added tickers: {len(added_tickers)} | Removed tickers: {len(removed_tickers)}")
            return new_cik_ticker_list, added_tickers
        
        else:
            error_str = f"Error: Request failed\nStatus code: {response.status_code} \n\n Text: {response.text}"
            log("error", error_str)
            raise Exception(error_str)
        
    except Exception as e:  
        log("error", f"{str(e)}\n\nTraceback: {traceback.format_exc()}")
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
        with open(data_directory +"/company_tickers.json", "r") as f:
            data = json.load(f)

    else:
        data = json.loads(data)

    for key in data.keys():
        cik_ticker.append((data[key]["cik_str"], data[key]["ticker"]))

    return cik_ticker

def sort_dict_keys(input_dict):
    """
    Sort the dictionary keys alphabetically.

    Args:
        input_dict (dict): The dictionary to sort.

    Returns:
        dict: A new dictionary with keys sorted alphabetically.
    """
    return {key: input_dict[key] for key in sorted(input_dict)}

if __name__ == "__main__":
    log("info", "Starting filing scraper")
    scrape_filings(mode="month", mode_amount=2)
    log("info", "Finished filing scraper")