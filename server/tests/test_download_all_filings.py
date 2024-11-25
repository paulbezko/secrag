from ..lib_secrag.edgar import set_identity
import json

set_identity('secrag', 'contact@secrag.com')

with open('database/memory/filings_available.json', 'r') as file: filings_available = json.load(file)

for company in filings_available.keys():
    ticker, cik, name = company.split(" | ")
    
    get_entity(cik)

    sec_filing = entity.get_filings(form=filing_info.filing_type, date=filing_info.filing_date)[0]

    sec_filing.xbrl()