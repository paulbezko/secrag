from edgar.entities import Company
from edgar.core import set_identity

set_identity("{} {}".format("SECRag", "secrag.info@gmail.com"))

filing = Company("AAPL").get_filings(form="10-K")[0]

print(filing.xbrl())