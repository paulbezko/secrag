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
import time
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
data_directory = "database/memory"

def get_json_ciks_tickers():

    url = 'https://www.sec.gov/files/company_tickers.json'
    headers = {'User-Agent': 'secrag.info@gmail.com'}

    response = requests.get(url, headers=headers)
    json_data = json.loads(response.text)

    json_ciks_tickers = {}
    for key, value in json_data.items():
        if '-' in json_data[key]['ticker']: continue # Removing all tickers that have a dash in them
        json_ciks_tickers[json_data[key]['cik_str']] = f"{json_data[key]['ticker']} | {json_data[key]['title']}"

    return json_ciks_tickers


def refresh_filings(json_ciks_tickers, period_type, period):

    eastern_tz = pytz.timezone('America/New_York')
    utc_now = datetime.now(pytz.utc)
    
    if period_type == "yearly": # Settings for a full scrape run
        end_time = utc_now.astimezone(eastern_tz) - relativedelta(years=datetime.now().year - period)
        start_time = end_time - relativedelta(years=1)
        filings = get_filings(form=["10-K", "10-Q"], year=period)

    elif period_type == "daily": # Settings for a regular scrape run
        end_time = utc_now.astimezone(eastern_tz)
        start_time = end_time - relativedelta(days=1)
        filings = get_filings(form=["10-K", "10-Q"])

    end_time_str = end_time.strftime('%Y-%m-%d')
    start_time_str = start_time.strftime('%Y-%m-%d') 

    filings = filings.filter(date=f"{start_time_str}:{end_time_str}", form=["10-K", "10-Q"])

    try: # Try to load filing json, create if it does not exist yet
        with open(data_directory +"/filings_available.json", "r") as f: 
            json_filings = json.load(f)
    except: json_filings = {}

    json_filings_new = []
    for filing in filings:
        try:
            ticker_title = str(json_ciks_tickers[filing.cik])
            year = str(filing.filing_date)[:4]

            # Appending to new json
            json_filings_new.append(f"{ticker_title.split(" | ")[0]} {filing.form} {filing.filing_date}")

            # Appending to available json
            if ticker_title not in json_filings: json_filings[ticker_title] = {}
            if year not in json_filings[ticker_title]: json_filings[ticker_title][year] = []
            if f"{filing.form} {filing.filing_date}" not in json_filings[ticker_title][year]:
                json_filings[ticker_title][year].append(f"{filing.form} {filing.filing_date}")
            
        except: pass

    with open(data_directory +"/filings_available.json", "w") as f:
        json.dump(json_filings, f, indent=2)

    with open(data_directory +"/filings_new.json", "w") as f:
        json.dump(json_filings_new, f, indent=2)


def sort_jsons():

    with open(data_directory +"/filings_available.json", "r") as f: json_filings = json.load(f)
    json_filings = {key: value for key, value in sorted(json_filings.items(), key=lambda item: item[0])}
    with open(data_directory +"/filings_available.json", "w") as f: json.dump(json_filings, f, indent=2)

    with open(data_directory +"/filings_new.json", "r") as f: json_filings_new = json.load(f)
    json_filings_new = sorted(json_filings_new)
    with open(data_directory +"/filings_new.json", "w") as f: json.dump(json_filings_new, f, indent=2)


if __name__ == '__main__':
    configure_logger(current_dir+"/logs/filing_scraper.log")
    log("info", "Starting edgar scraper")
    full_scrape = False # Controls whether a full scrape is run or a regular scrape is run

    if full_scrape: # Settings for a full scrape run
        period_type = "yearly"
        list_periods = list(range(2000, datetime.now().year + 1))

    else: # Settings for a regular scrape run
        period_type = "daily"
        list_periods = [1]

    json_ciks_tickers = get_json_ciks_tickers()
    set_identity("{} {}".format("secrag", "secrag.info@gmail.com"))
    for period in list_periods:
        refresh_filings(json_ciks_tickers, period_type, period)
        time.sleep(3)

    sort_jsons() # Sorting jsons alphabetically
    log("info", "Finished edgar scraper")