# SEC-filing-summary-for-drug
This app based on streamlit pulls out latest SEC filing rated to a drug of interest and summarizes the filing details using ChatGPT.

How this works?

1) Once the user provides an input drug for qhich they want to see a SEC filing for, the SEC API (https://sec-api.io/) pulls out all related filings from SEC EDGAR full text search. 
2) For the latest filing, we pull the URL of the press release and parse the data through Beautfiul Soup in python. To limit the number of input tokens for ChatGPT-Turbo algorithm, we divide the text into chunks using textWRAP and only retain the chunks that contains our drug of interest.
3) Feed this text into the filing data to find out key details from the latest press-release for the drug of interest.


Files 
app.py : Interface for streamlit. All dependencies are pointed and called. 
requirements.txt: All versions of python dependencies are shown here.
secrets.toml : This file contains the API keys for OpenAI ChatGPT and SEC API.

Changes for individual user:
-- Users need to obtain their own API from OPENAI and SEC-API (link provided above, they only give 100 free tokens for access). This is just a demo for my individual purpose and not for commerical use. 
