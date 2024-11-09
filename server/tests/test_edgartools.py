from edgar.entities import Company
from edgar.core import set_identity

set_identity("{} {}".format("SECRag", "secrag.info@gmail.com"))

ticker = "COIN"

filings = Company(ticker).get_filings(form="10-K")

for filing in filings:

    with open(f"database/markdowns/{ticker}-{filing.filing_date}.md", "w") as f:
        f.write(filing.markdown())