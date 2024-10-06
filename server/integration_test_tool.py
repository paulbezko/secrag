import threading
from dashboard.dashboard_routes import ask_
from dashboard.utils.sec_utils import load_sec_thread_limited, FilingInfo

def sec_rate_limit_test():
    # Create threads for multiple requests
    threads = []
    filing = FilingInfo(ticker="AAPL", filing_type="10-K", filing_year="2016", filing_date="2016-10-26")
    for i in range(1, 8):  # Making 7 requests
        thread = threading.Thread(target=load_sec_thread_limited, args=(filing,))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

def ask_test():
    prompt = "What is the market segmentation"
    uid = "planetchars@gmail.com"
    conversation_id = "AAPL-2016-10K"
    filing_date = "2016-10-26"
    socket_id = None

    # Return error on LoadSEC
    ask_(
        prompt = prompt,
        uid = uid,
        conversation_id = conversation_id, 
        filing_date = filing_date,
        socket_id=socket_id
    )

if __name__ == '__main__':
    sec_rate_limit_test()


    