from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.llms import Ollama
import streamlit as st
import os
from dotenv import load_dotenv
import yfinance as yf
from yahooquery import search

# Load environment variables
load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")

# LangChain Prompt Template
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant. Please respond to user queries."),
        ("user", "Question: {question}")
    ]
)

# LangChain setup
llm = Ollama(model="llama3.2")
output_parser = StrOutputParser()
chain = prompt | llm | output_parser

# Streamlit UI
st.title('Langchain + LLaMA3 Demo with Real Stock Price')
input_text = st.text_input("Ask a question (e.g., 'What is the stock price of Apple?')")

# Helper functions for stock info
def extract_company_name(query):
    query = query.lower()
    if "stock price of" in query:
        return query.split("stock price of")[-1].strip().rstrip("?")
    elif "stock price for" in query:
        return query.split("stock price for")[-1].strip().rstrip("?")
    return None

def find_ticker_symbol(company_name):
    try:
        result = search(company_name)
        quotes = result.get("quotes", [])
        for quote in quotes:
            if quote.get("quoteType") in ["EQUITY", "ETF"]:
                return quote.get("symbol")
        return None
    except:
        return None

def get_stock_price(symbol):
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period='1d')
        if not data.empty:
            return round(data['Close'][0], 2)
    except:
        return None

# Main logic
if input_text:
    if "stock price" in input_text.lower():
        company = extract_company_name(input_text)
        if company:
            symbol = find_ticker_symbol(company)
            if symbol:
                price = get_stock_price(symbol)
                if price:
                    st.success(f"The current stock price of {company.title()} ({symbol}) is ${price}")
                else:
                    st.error("Couldn't fetch stock price.")
            else:
                st.error("Could not find stock symbol for that company.")
        else:
            st.warning("Please use a format like 'What is the stock price of Apple?'")
    else:
        # Use LLaMA3 for other queries
        response = chain.invoke({"question": input_text})
        st.write(response)


