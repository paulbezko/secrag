import os
import sys
import time

import pandas as pd

import tracemalloc
tracemalloc.start()


# Add the path to custom libs
sys.path.append("server")
sys.path.append("server/lib_secrag")
# sys.path.append("server")

# from lib_secrag.edgar._markdown
from lib_secrag.edgar._filings import Filing
from lib_secrag.edgar.financials import Financials
from lib_secrag.edgar._markdown import html_to_markdown
from lib_secrag.edgar.entities import get_entity
from lib_secrag.edgar.core import set_identity
from lib_secrag.edgar import get_filings
import asyncio

# set_identity("{} {}".format("SECRAG", "secrag.info@gmail.com"))

sec_rate_limit = 1
sec_rate_limit_counter = 0
# Launches async task and triggers rate limiter 
async def launch_rate_limited(function, num_of_func_requests: int = 1):
    global sec_rate_limit_counter
    while sec_rate_limit_counter >= sec_rate_limit:
        await asyncio.sleep(0)
    
    sec_rate_limit_counter += num_of_func_requests
    print("counter:", sec_rate_limit_counter)
    result = await function()
    launch_rate_count_timer(num_of_func_requests)
    return result

# Launches sync task and triggers rate limiter 
async def launch_rate_limited_sync_func(function, num_of_func_requests: int = 1):
    global sec_rate_limit_counter
    await asyncio.sleep(0)
    while sec_rate_limit_counter >= sec_rate_limit:
        await asyncio.sleep(0)
    sec_rate_limit_counter += num_of_func_requests    
    launch_rate_count_timer(num_of_func_requests)
    result = function()
    return result

# Launches task that decreases rate limit counter after some time
def launch_rate_count_timer(instances: int = 1):
    for i in range(instances):
        asyncio.create_task(elapse_rate_limit_count())

# Function that decreases rate limit counter after some time
async def elapse_rate_limit_count():
    global sec_rate_limit_counter
    print("rate_limit_elapsed:", sec_rate_limit_counter)
    await asyncio.sleep(0.2)
    sec_rate_limit_counter -= 1

def try_except(func, default=None, expected_exc=(Exception,)):
    try: return func()
    except Exception as e:
        print("finballox", str(e)) 
        return default

async def atry_except(func, default=None, expected_exc=(Exception,)):
    try: return await func()
    except expected_exc: 
        print("ballox")
        return default

async def process_filing(filing: Filing):
            print(f"Processing {filing.cik} {filing.form} {filing.filing_date}")
            filing_form = filing.form.replace("/","")  
            if os.path.exists(f"database/bulk/markdowns/{filing.cik}_{filing_form}_{filing.filing_date}.md"):
                 return
            
            f_html = filing.html()
            # with open(f"database/bulk/htmls/{filing.cik}_{filing_form}_{filing.filing_date}.html", "w") as f:
            #     f.write(f_html)
            
            f_md = html_to_markdown(f_html)
            with open(f"database/bulk/markdowns/{filing.cik}_{filing_form}_{filing.filing_date}.md", "w") as f:
                f.write(f_md)

            await asyncio.sleep(0.15)
            xbrl = await atry_except(lambda: filing.xbrl())
            
            financials = try_except(lambda: Financials(xbrl))
            balance_sheet = try_except(lambda: financials.get_balance_sheet().get_dataframe())

            income_statement = try_except(lambda: financials.get_income_statement().get_dataframe())
            cash_flow_statement = try_except(lambda: financials.get_cash_flow_statement().get_dataframe())
            statement_of_changes_in_equity = try_except(lambda: financials.get_statement_of_changes_in_equity().get_dataframe())
            statement_of_comprehensive_income = try_except(lambda: financials.get_statement_of_comprehensive_income().get_dataframe())

            fin_statements = {
                "balance_sheet": balance_sheet,
                "income_statement": income_statement,
                "cash_flow_statement": cash_flow_statement,
                "statement_of_changes_in_equity": statement_of_changes_in_equity,
                "statement_of_comprehensive_income": statement_of_comprehensive_income
            }

            for key, _ in fin_statements.items():
                # Sometimes it returns tuples
                if isinstance(fin_statements[key], tuple):
                    # Process each element of a tuple
                    for damn_tuple in fin_statements[key]:
                        # If item is a dataframe, convert it to markdown
                        # Otherwise, just return "no data"
                        text = damn_tuple.to_markdown() if type(damn_tuple) is pd.DataFrame and not damn_tuple.empty  else None

                else:
                    # If item is a dataframe, convert it to markdown
                    # Otherwise, just return "no data"
                    text = fin_statements[key].to_markdown() if type(fin_statements[key]) is pd.DataFrame and not fin_statements[key].empty  else None

                if text:
                    
                    with open(f"database/bulk/financials/{key}/{filing.cik}_{filing_form}_{filing.filing_date}.md", "w") as f:
                        f.write(text)

            await asyncio.sleep(0.15)

async def main():
    year = 2019
    print("processing year", year)
    filings = get_filings(form=["10-K", "10-Q"], year=year)
    await asyncio.sleep(0.15)
    # list_filings = filings.to_list()
    for filing in filings:
        await process_filing(filing)


if __name__ == "__main__":
        asyncio.run(main())