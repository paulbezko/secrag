from dashboard.dashboard_routes import ask_

def create_chat(ticker, conversation_id, filing_date)

if __name__ == '__main__':
    
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

    