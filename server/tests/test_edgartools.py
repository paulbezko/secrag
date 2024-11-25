import sys
import time

# Add the path to custom libs
sys.path.append("server/lib_secrag")


from edgar.markdown import html_to_markdown
from edgar.entities import get_entity
from edgar.core import set_identity
from edgar import get_filings

set_identity("{} {}".format("SECRAG", "secrag.info@gmail.com"))

if __name__ == "__main__":

    filings = get_filings(form=["10-K", "10-Q"], year=2023)
    for filing in filings[:1]:
        
        print(f"Processing {filing.cik} {filing.form} {filing.filing_date}")

        f_html = filing.html()
        with open(f"database/bulk/htmls/{filing.cik}_{filing.form}_{filing.filing_date}.html", "w") as f:
            f.write(f_html)
        
        f_md = html_to_markdown(f_html)
        with open(f"database/bulk/markdowns/{filing.cik}_{filing.form}_{filing.filing_date}.md", "w") as f:
            f.write(f_md)

        with open(f"database/bulk/xbrls/{filing.cik}_{filing.form}_{filing.filing_date}.xbrl", "w") as f:
            f.write(filing.xbrl())

        time.sleep(0.5)