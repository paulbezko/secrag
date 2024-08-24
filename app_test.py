import tkinter as tk
from tkinter import scrolledtext
from app import ask_
from utils.json_utils import json_memory_loader_raw

root = tk.Tk()
root.title("My App")
root.resizable(True, True)


# Input fields with descriptions
tk.Label(root, text="Prompt:").grid(row=0, column=0)
prompt = tk.StringVar()
prompt_field = tk.Entry(root, textvariable=prompt)
prompt_field.grid(row=0, column=1, sticky="we")

tk.Label(root, text="UID:").grid(row=1, column=0)
uid = tk.StringVar()
uid_field = tk.Entry(root, textvariable=uid)
uid_field.grid(row=1, column=1, sticky="we")

tk.Label(root, text="Conversation ID:").grid(row=2, column=0)
conversation_id = tk.StringVar()
conversation_id_field = tk.Entry(root, textvariable=conversation_id)
conversation_id_field.grid(row=2, column=1, sticky="we")

tk.Label(root, text="Ticker:").grid(row=3, column=0)
ticker = tk.StringVar()
ticker_field = tk.Entry(root, textvariable=ticker)
ticker_field.grid(row=3, column=1, sticky="we")

tk.Label(root, text="Filing:").grid(row=4, column=0)
filing = tk.StringVar()
filing_field = tk.Entry(root, textvariable=filing)
filing_field.grid(row=4, column=1, sticky="we")

# Scrollable text field
tk.Label(root, text="Chat:").grid(row=5, column=0)
chat_field = scrolledtext.ScrolledText(root, width=50, height=10)
chat_field.grid(row=5, column=1, sticky="nsew")

tk.Label(root, text="Context").grid(row=0, column=2)
context_field = scrolledtext.ScrolledText(root, width=50, height=10)
context_field.grid(row=1, column=2, rowspan = 5,  sticky="nsew")

root.grid_rowconfigure(5, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)


def load_inputs():
    prompt, uid, conversation_id, socket_id, ticker, filing = (prompt.get(), uid.get(), conversation_id.get(), None, ticker.get(), filing.get())
    
def load_chat():
    chat_field.delete('1.0', tk.END)
    try:
        user_memory, ai_memory = json_memory_loader_raw(uid.get(), conversation_id.get())
        for i in range(len(user_memory)):
            chat_field.insert(tk.END, "User: ")
            chat_field.insert(tk.END, user_memory[i] + "\n\n", "user")
            chat_field.insert(tk.END, "AI: ")
            chat_field.insert(tk.END, ai_memory[i] + "\n\n", "ai")
            chat_field.tag_config('user', foreground='blue')
            chat_field.tag_config('ai', foreground='green')
    except Exception as e:
        print(str(e))
        chat_field.insert(tk.END, "Error: " + str(e) + "\n", "error")
 
def print_context(context):
    context_field.delete('1.0', tk.END)
    for i in context:
       context_field.insert(tk.END, i.page_content + "\n\n ----------------------- \n") 
       

def submit_prompt():
    try:
        prompt_output = ask_(prompt.get(), uid.get(), conversation_id.get(), None, ticker.get(), filing.get())
        print_context(prompt_output["answer"]["context"])
        load_chat()
    except Exception as e:
        chat_field.insert(tk.END, "Error: " + str(e) + "\n", "error")

load_button = tk.Button(root, text="Load", command=load_chat)
load_button.grid(row=6, column=0, sticky = "we")

submit_button = tk.Button(root, text="Ask", command=submit_prompt)
submit_button.grid(row=6, column=1, sticky = "w")

chat_field.tag_config('user', foreground='black')
chat_field.tag_config('ai', foreground='green')
chat_field.tag_config('error', foreground='red')

root.mainloop()

