from utils.vectorstore_utils import vectorstore_manager
from utils.sec_utils import load_sec

tickers = [
    "UEC", 
    "DAL", 
    "NKLA", 
    "DJT", 
    "SHW", 
    "BA", 
    "ONON", 
    "WMT", 
    "WTB",
    "MO"
]

def save_html_to_file(html_string, file_name):
    # Open the file in write mode ('w') with encoding set to UTF-8
    with open("output_htmls/"+file_name+".html", 'w+', encoding='utf-8') as file:
        # Write the HTML string to the file
        file.write(html_string)
    print(f"HTML content saved to {file_name}")

def test(tickers):
    for ticker in tickers:
        try:
            filing = load_sec(ticker)
            save_html_to_file(filing.html, ticker)
            vectorstore_manager(filing)
        except Exception as e:
            print("Something went wrong with ticker {} - {}".format(ticker, str(e)))

if __name__ == "__main__":
    test(tickers)
