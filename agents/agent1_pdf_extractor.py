# agent 1 pdf extractor
import os
import openai
import sys_pdf

# directory which holds the PDF files to be extracted
# files in this directory are populated by the user
directory = "PDF_files/to_be_extracted"



### pasted from : https://github.com/Azure-Samples/python-ai-agent-frameworks-demos/blob/main/examples/autogen_basic.py

import asyncio
import os

import azure.identity
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient, OpenAIChatCompletionClient
from dotenv import load_dotenv

# Setup the client to use either Azure OpenAI or GitHub Models
load_dotenv(override=True)
client = OpenAIChatCompletionClient(model=os.getenv("GITHUB_MODEL", "gpt-4o"), api_key=os.environ["GITHUB_TOKEN"], base_url=os.getenv("BASE_URL"))

agent1_prompt = 
agent = AssistantAgent(
    "pdf_extractor",
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
'''
Using openai's model to extract the values from the PDF to build the overview table.
'''

class Agent1_extraction:
    '''
    Use openai api to extract data from a PDF file and format into a table.
    '''

    def __init__(self, working_dir, csv_dir, update_overview, update_product):
        self.working_dir = working_dir
        self.csv_dir = csv_dir
        self.company_name = ""
        self.invoice_date = ""
        self.raw_text = ""
        self.table_dict = {}
        self.extracted_dict = {}
        self.file_counter = 0
        self.update_overview = update_overview
        self.update_product = update_product
        
        # init methods
        load_dotenv(override=True) # Load environment variables from the .env file
        self.client = OpenAIChatCompletionClient(model=os.getenv("GITHUB_MODEL", "gpt-4o"), api_key=os.environ["GITHUB_TOKEN"], base_url=os.getenv("BASE_URL"))


    def assess_extraction(self):

        # Build the prompts
        self.build_prompts()
        
        for table_name, prompt in self.table_dict.items():
            
            # Extract specific invoice details using OpenAI ChatCompletion
            response, extracted_data = self.extract_invoice_data(prompt)
            
            # log the number of tokens spent
            sys_pdf.openai_token_log(table_name, response.usage.total_tokens)
        
            # Create a pandas dataframe with the extracted data
            invoice_table = self.create_invoice_table(extracted_data)
            self.extracted_dict.update({table_name:[response, extracted_data, invoice_table]})

            # grab company name and invoice date from overview table
            if table_name == 'overview':
                self.pull_name_date(invoice_table)

            # save data as csv and log
            routine,log_value = save_as_csv(invoice_table, self.csv_dir, self.name_base, table_name)
            sys_pdf.sys_log_entry(routine, log_value)

        # save the original pdf in the 'processed' directory
        sys_pdf.move_file(self.working_dir, "processed", file_name)
        os.rename(os.path.join(directory, pdf_file), os.path.join("in_process", pdf_file))
        
        self.file_counter += 1

        
    def build_prompts(self):
        # Prompt for the model to identify relevant data for the OVERVIEW table
        self.overview_prompt = f"""
        You are an expert in extracting data from invoices. 
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
        You are an expert in extracting data from invoices. 
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

    






if __name__ == "__main__":
    asyncio.run(main())