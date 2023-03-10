import streamlit as st
import openai
from sec_api import FullTextSearchApi
from bs4 import BeautifulSoup
import requests
import textwrap
import math
import pandas as pd 


def get_openai_answer(drug):
    # Get API key
    openai.api_key = st.secrets["api-keys"]["open_ai"]
    fullTextSearchApi = FullTextSearchApi(api_key=st.secrets["api-keys"]["sec_key"])
    
    #drug molecule is the input from the user
    
    #Put final data in this dataframe 
    data_struc = pd.DataFrame(columns =['ProductName','Entity','Date_of_Filing','formType','formDescription','CIK','Link_to_Press_Release'])
    
    query = {
          "query": drug,
          "formTypes": ['8-K','6-K'], # ALL FILE TYPES CAN BE EXTRACTED
          "startDate": '2001-01-01',
          "endDate": '2024-01-01',
            }
    
    response = fullTextSearchApi.get_filings(query)
    
    if response['total']['value']==0:
        data_struc.loc[len(data_struc)]= [drug,"N/A","N/A","N/A","N/A","N/A","N/A"]
        
    else:
        #find the URL of latest filing, iterate through 
        fileNum=0
        date_of_file = response['filings'][0]['filedAt'] #initialise with first date of filing

        for i in range(response['total']['value']):
            if response['filings'][i]['filedAt']>date_of_file:
                fileNum=i
                date_of_file = response['filings'][i]['filedAt']

        url = response['filings'][fileNum]['filingUrl']
        entity = response['filings'][fileNum]['companyNameLong'][0:-17] #strip CIK number form the end
        
        #define headers for beautiful soup to get access to the SEC filing text
        headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0',
    'From': 'nyadav@crai.com'  # This is another valid field
        }

        #HEADER information needed to access SEC data, otherwise access is revoked. 
        page = requests.get(url, headers=headers)
        
        #Using beautiful soup to extract all the texts 
        doc = BeautifulSoup(page.text,'html.parser')
        text_body = doc.body.get_text(" ")
        text_body = text_body.replace(u'\xa0', u'')

        #GPT turbo chat CODE only takes 4000 tokens, so we use textwrap to chunk the data and concatenate enough chunks to    build around 
        # ~3100 tokens, rest 900 reserved for prompt and answers
        chunks = textwrap.wrap(text_body, 3000)

        # Set the model and compose the prompt
        model_engine = "gpt-3.5-turbo"
        
        num_chunks=0
        main_text = ""
        for excerpts in chunks:
            if drug in excerpts:
                num_chunks+=1
                main_text = main_text + excerpts
        
        if num_chunks<4:
        #Generally, 4 chunks with 4000 characters build amost around ~3100 tokens, might need to be modified later
            text_body=main_text

            # Generate a response
            completion = openai.ChatCompletion.create(
            model=model_engine,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that finds key relevant points from the text."},
        {"role": "user", "content": f"Find the key points for {drug} in bullet point list from the given text : {text_body}"}
            ]
        )
            summary_version = completion.choices[0].message.content
                    
        #-----------If length of chunks>=4 ---------
        
        if num_chunks>3:
            num_chunks_divide = math.ceil(len(chunks)/2)
        #Generally, 4 chunks with 4000 characters build amost around ~3100 tokens, might need to be modified later
            text_body_1 = ""
            text_body_2 = ""

            for i in range(num_chunks_divide):
                text_body_1 = text_body_1 + chunks[i]

            for i in range(num_chunks_divide,len(chunks)):
                text_body_2 = text_body_2 + chunks[i]

            # Generate a response
            completion_1 = openai.ChatCompletion.create(
            model=model_engine,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that finds key relevant points from the text."},
        {"role": "user", "content": f"Find the key points for drug {drug} in bullet point list from the given text : {text_body}"}
            ]
        )
                
            completion_2 = openai.ChatCompletion.create(
            model=model_engine,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that finds key relevant points from the text."},
        {"role": "user", "content": f"Find the key points for drug {drug} in bullet point list from the given text : {text_body}"}
            ]
        )
                
            summary_version = completion_1.choices[0].message.content + '\n ' + completion_2.choices[0].message.content
            
        data_struc.loc[len(data_struc)] = [drug, entity, response['filings'][fileNum]['filedAt'], response['filings'][fileNum]['formType'], response['filings'][fileNum]['type'],response['filings'][fileNum]['cik'],response['filings'][fileNum]['filingUrl']]
        
    return data_struc, summary_version
           

# Write intro text
st.write("Welcome to SEC filing summarizer ")

# Get input
drug = st.text_input("Please input the drug you want to find SEC filing data on? ")

# Wait until click
if(st.button("Display SEC related information.")):
    data_struc, summary_version = get_openai_answer(drug)
    # Write answer
    data_struc=data_struc.transpose().rename(columns={0:""})
    st.header("Information related to the Filing ")
    st.dataframe(data_struc, use_container_width=True, )
    st.header("Summary of the Filing :")
    
    summary_version_split = summary_version.split("\n")
    for lines in summary_version_split:
        st.write(lines)
    
    
    
