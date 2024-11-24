from edgar.entities import get_entity
from edgar.core import set_identity

set_identity("{} {}".format("SECRAG", "secrag.info@gmail.com"))

ticker = "COIN"

filings = get_entity(320193)

print(filings)

# for filing in filings:

#     with open(f"database/markdowns/{ticker}-{filing.filing_date}.md", "w") as f:
#         f.write(filing.markdown())