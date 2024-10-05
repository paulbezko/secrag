from edgar.core import set_identity
from edgar.entities import Company


if __name__ == "__main__":
    set_identity("{} {}".format("marks", "marksdocenko@outlook.com"))

    try:
        filings = Company("NVDA").get_filings(form="10-K")
        
        for i in filings:
            print(i.filing_date)
        print(len(filings))
    except AttributeError:
        raise Exception("Invalid ticker - {}".format("NVDA"))