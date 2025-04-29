# agent 1 pdf extractor
import os
import openai
import sys_pdf
import pandas as pd

from datetime import datetime
import openai
from dotenv import load_dotenv
import sys_pdf




##### pasted from : https://github.com/Azure-Samples/python-ai-agent-frameworks-demos/blob/main/examples/autogen_basic.py

import asyncio
import os

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient, OpenAIChatCompletionClient
from dotenv import load_dotenv

# Setup the client to use either Azure OpenAI or GitHub Models
load_dotenv(override=True)
client = OpenAIChatCompletionClient(model=os.getenv("GITHUB_MODEL", "gpt-4o"), api_key=os.environ["GITHUB_TOKEN"], base_url=os.getenv("BASE_URL"))

agent1_prompt = "see below"
agent = AssistantAgent(
    "table_extractor",
    model_client=client,
    system_message="You are a Spanish tutor. Help the user learn Spanish. ONLY respond in Spanish.",
)
async def main() -> None:
    response = await agent.on_messages(
        [TextMessage(content="hii how are you?", source="user")],
        cancellation_token=CancellationToken(),
    )
    print(response.chat_message.content)



#####  my ealier code
def save_as_csv(df, dir, file_base, table_name):
    '''
    Converts pandas dataframe to a csv and saves to drive.
    Input:
        df:           dict. Holds the correspnding search results  
        dir:          str. name of directory where file is saved   
        file_base:    str. Company name and date
        table_name:   str. type of table 'overview' or 'products'
    '''
    # format dates to standard YYYY-MM-DD
    try:
        # add timestamp to filename
        file_name = dir + "/" + file_base + " " + table_name + datetime.now().strftime("%Y%m%d_%H%M%S") + '.csv'
        df.to_csv(file_name, index= False)
        return "CSV", "OK. Saved: " + table_name + " " + file_base
    except:
        # add msg to log if error
        return "CSV", "Error saving CSV " + table_name + " " + file_base

def format_date(date_string, current_date_format):
    '''
    formats data string to a datetime object. 
    '''
    date_obj = datetime.strptime(date_string, current_date_format)
    formatted_date_str = (date_obj.strftime('%Y-%m-%d'))
    return formatted_date_str



'''
Using openai's model to extract the values from the PDF to build the overview table.
'''

class Agent1_extraction:
    '''
    Use openai api to extract data from a PDF file and format into a table.
    '''

    def __init__(self, raw_text, update_overview="", update_product=""):
        self.raw_text = raw_text
        #self.csv_dir = csv_dir
        self.company_name = ""
        self.invoice_date = ""
        self.table_dict = {}
        self.extracted_dict = {}
        self.file_counter = 0
        self.update_overview = update_overview
        self.update_product = update_product
        
        # init methods
        load_dotenv(override=True) # Load environment variables from the .env file
        self.client = OpenAIChatCompletionClient(model=os.getenv("GITHUB_MODEL", "gpt-4o"), api_key=os.environ["GITHUB_TOKEN"], base_url=os.getenv("BASE_URL"))


    def run_extraction(self):

        # Build the prompts
        self.build_prompts()  # returns a dictionary of prompts, overview and product tables
        
        for table_name, prompt in self.table_dict.items():
            
            # Extract specific invoice details using OpenAI ChatCompletion
            response, extracted_data = self.extract_invoice_data(prompt)
            
            # log the number of tokens spent
            #sys_pdf.openai_token_log(table_name, response.usage.total_tokens)
        
            # Create a pandas dataframe with the extracted data
            invoice_table = self.create_invoice_table(extracted_data)
            self.extracted_dict.update({table_name:[response, extracted_data, invoice_table]})

            # grab company name and invoice date from overview table
            if table_name == 'overview':
                self.pull_name_date(invoice_table)

            # save data as csv and log
            routine,log_value = save_as_csv(invoice_table, self.csv_dir, self.name_base, table_name)
            sys_pdf.sys_log_entry(routine, log_value)

        
        self.file_counter += 1

        
    def build_prompts(self):
        # Prompt for the model to identify relevant data for the OVERVIEW table
        self.overview_prompt = f"""
        You were paid by a company and received an invoice. 
        Your job is to record the overall details about the invoice, not about the individual products.
        {self.update_overview}
        Extract the following details from the text:
        - Invoice Date
        - Invoice Number
        - Invoice Company
        - Invoice Total
        Text: {self.raw_text}
        Provide the data in a JSON format with keys: invoice_date, invoice_number, invoice_company, invoice_total.
        """

        # Prompt for the model to identify relevant data for the PRODUCTS table
        self.product_prompt = f""" 
        The text comes from a PDF invoice so formatting may be inconsistent.
        Your job is to record the details about the products in the invoice and are not interested in the overall invoice details.
        {self.update_product}
        Extract the following details from the text:
        - Invoice Number
        - Product Name
        - Product Seller
        - Price of Product
        Text: {self.raw_text}
        There may be multiple products in the text. 
        Provide the data in a JSON format with keys: invoice_number, product_name, product_seller, product_amount. Invoice_number should be repeated for each product in the JSON output. 
        """

        # store these prompts in a dictionary
        self.table_dict = { 'overview': self.overview_prompt, 'product': self.product_prompt }

    
    def extract_invoice_data(self, prompt):
        """Extracts specific invoice details using openai framework. Will need to update this to autogen"""
        
        response = self.client.chat.completions.create(
            max_tokens = 3000,
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert in extracting structured data from text."},
                {"role": "user", "content": prompt}
            ]
        )
        extracted_data = str(response.choices[0].message.content).strip("```json").replace("\n","")
        #self.extracted_tables.update({table_name, [extracted_data, response]})  # store results in a dictionary
        return response, eval(extracted_data)  # Convert string to dictionary


    def create_invoice_table(self, data):
        """Creates a table with the extracted data."""
        if type(data) == list:
            df = pd.DataFrame(data)
        else:
            df = pd.DataFrame([data])
        #df.columns = ["Invoice Date", "Invoice Number", "Invoice Company", "Invoice Total"]
        return df
    

    def pull_name_date(self, overview_table):
        '''Create file name for saving'''
        # record company name
        self.company_name = overview_table['invoice_company'][0].replace('.', '_')
        # format dates to standard YYYY-MM-DD
        formatted_date_str = format_date(overview_table['invoice_date'][0], '%B %d, %Y') # November 11, 2015
        self.name_base = self.company_name + "_" + formatted_date_str



if __name__ == "__main__":
    asyncio.run(main())