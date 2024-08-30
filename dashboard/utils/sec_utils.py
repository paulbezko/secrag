from edgar.core import set_identity
from edgar.entities import Company
from utils.debug import debug_print


# Load SEC filing
def load_sec(ticker, file_number = None):
    # Lowercase the ticker 
    ticker = ticker.lower()
    
    filing_tl = sec_search(ticker=ticker, name="marks", email="marksdocenko@outlook.com", file_number=file_number)
    
    debug_print(filing_tl, filing_tl.file_number)
    debug_print(type(filing_tl.filing_date))
    
    custom_filing = CustomCompanyFiling(
        file_number=filing_tl.file_number, 
        filing_html=filing_tl.html(),
        cik=filing_tl.cik, ticker=ticker, 
        filing_date=filing_tl.filing_date, 
        company_name=filing_tl.company
    )
    return custom_filing

def sec_search(ticker, name, email, file_number = None):
    set_identity("{} {}".format(name, email))

    try:
        filings = Company(ticker).get_filings(form="10-K", file_number=file_number).latest(1)

        return filings
    except AttributeError:
        raise Exception("Invalid ticker - {}".format(ticker))
    
# This class is made for convenience. It stores all important filing data for the project's implementation
class CustomCompanyFiling():
    def __init__(self, file_number, filing_html, cik, ticker, filing_date, company_name):
        self.ticker = ticker
        self.file_number = file_number
        self.filing_date = filing_date
        self.cik = cik
        self.html = filing_html
        self.company_name = company_name