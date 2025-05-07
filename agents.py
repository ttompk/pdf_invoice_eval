# source: https://github.com/Azure-Samples/python-ai-agent-frameworks-demos/blob/main/examples/autogen_magenticone.py
import asyncio
import os
from dotenv import load_dotenv

#import azure.identity
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import MagenticOneGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient

import database_utils

def build_overview_prompt(raw_text: str, update_overview = ""):
    # Prompt for the model to identify relevant data for the OVERVIEW table
    overview_prompt = f"""
    The text comes from a PDF invoice so formatting may be inconsistent.
    Your job is to record the overall details about the invoice, not about the individual products.
    {update_overview}
    Extract the following details from the text:
    - Invoice Date
    - Invoice Number
    - Invoice Company
    - Invoice Total
    Text: {raw_text}
    Provide the data in a JSON format with keys: invoice_date, invoice_number, invoice_company, invoice_total.
    """
    return overview_prompt

def build_products_prompt(raw_text: str, update_products= ""):
     # Prompt for the model to identify relevant data for the PRODUCTS table
    product_prompt = f""" 
    The text comes from a PDF invoice so formatting may be inconsistent.
    Your job is to record the details about the products in the invoice and are not interested in the overall invoice details.
    {update_products}
    Extract the following details from the text:
    - Invoice Number
    - Product Name
    - Product Seller
    - Price of Product
    Text: {raw_text}
    There may be multiple products in the text. 
    Provide the data in a JSON format with keys: invoice_number, product_name, product_seller, product_amount. Invoice_number should be repeated for each product in the JSON output. 
    """
    return product_prompt

def extract_text_from_pdf():
    pass


async def run_agents(client, table_agent, reviewer_agent):

    termination = TextMentionTermination("TERMINATE")   # will need to change who terminates as the app develops
    
    # define agent team
    agent_team = MagenticOneGroupChat(
        [table_agent, reviewer_agent],  # add in database_agent, summary_agent after testing
        max_turns = 10,   # arbitrarily chosen
        termination_condition=termination,
        model_client=client,
    )

    # run the team, send to console
    await Console(agent_team.run_stream(task="Extract table data from text and insert into a database."))


async def main() -> None:
    
    # env variables
    load_dotenv(override=True)
    #API_HOST = os.getenv("API_HOST", "github")
    BASE_URL = os.getenv("BASE_URL")
    MODEL_NAME = os.getenv("MODEL_NAME")
    API_KEY = os.getenv("GITHUB_TOKEN")

    # use openai via github 
    client = OpenAIChatCompletionClient(
        model=MODEL_NAME, 
        api_key=API_KEY, 
        base_url=BASE_URL,
        temperature=0.2)

    # define the table creator agent
    table_agent = AssistantAgent(
        name="table_creator",
        model_client=client,
        description="A worker that extracts values from text to build tables.",
        system_message=f"""
        You are an expert in extracting structured data from text. 
        You must create two tables, one named overview and the other named products.
        Here is information about the overview table: {build_overview_prompt()} and here is the information on products table: {build_products_prompt()}.
        These tables will be submitted to the table reviewer agent for validation.
        If you are unable to extract the data from the text, return 'FAILED' along with a one sentence description of the failure reason.
        You will repeat the process of data extraction for each file in the "in_process" directory following direction from the summary agent.
        """ )

    # define the table reviewer agent
    reviewer_agent = AssistantAgent(
        name="table_reviewer",
        model_client=client,
        description="An agent that reviews the tables created by the table_creator agent.",
        system_message=f"""
        You are an expert in reviewing tabulized data. 
        You must review the tabulized data from the table_creator agent and provide feedback on the accuracy of the data. 
        The tabulized data must align with the existing data in the database table: XYZ, if any exist. 
        In some instances, the underlying text data may not contain invoice data or may have incomplete invoice data. In these cases it may be impossible for the table creator agent to create a table.  
        The invoices table should contain the following extracted data: company providing the invoice, invoice number, date of the invoice, and the invoice total for all products. 
        The prodcuts table should contain the following extracted data: product names, product sellers and product_amounts.
        If the data is accurate, return 'ACCURATE'. 
        If the data is inaccurate, return 'INACCURATE' and return a short description of the failure reason to provide feedback to the table creator agent.
        If the table_creator agent is unable to produce a correct table after three attempts, return 'FAILED' along with a one sentence description of the failure reason. 
        After the tables have been processed, you can respond with TERMINATE.
        """)
    '''This failure reason should be provided to the database updater agent.'''

    # run the agent 
    run_agents(client, table_agent, reviewer_agent)




'''
database_agent = AssistantAgent(
    name= "database_updater",
    model_client=client,
    tools = [database_utils.invoice_function],
    description="An agent that updates the database with the tabulized data.",
    system_message=f"""
    You are an expert in updating databases with tabulized data.
    You must wait for the table reviewer agent to provide feedback on the accuracy of the tabulized data created by the table creator agent.
    You must update the database tables 'files', 'invoices', and 'products' with the tabulized data created by the table creator agent.
    Start with the 'files' table and then update the 'invoices' table and finally the 'products' table, if applicable.
    The 'files' table should contain the status of 'processed' or 'failed' for each PDF file, a failure reason if applicable, and a count of the invoices and products found in the PDF file.
    There will always be one 'files' database entry for each PDF file analyzed by the table creator agent regardless of whether the invoices and products data is accurate or inaccurate.
    In some cases the 'invoices' and 'products' database entries may not exist and this is acceptable.
    If the invoice table data is ultimately deemed INACCURATE by the table reviewer agent, you must not update the database.
    If the products data is deemed INACCURATE by the table reviewer agent, you also must not update the database.
    For any particular file, if there is a failure in updating the invoices or products database tables rollback the previous database entries associated with that file and return 'FAILED' along with a one sentence description of the failure reason. 
    """ )
'''
'''
summary_agent = AssistantAgent(
    name="summary_agent",
    model_client=client,
    description="An agent that summarizes the results of the workflow.",
    system_message=f"""
    You are an expert in summarizing the results of workflows.
    You must summarize the results of the entire workflow based on the feedback from the table reviewer agent and the database updater agent.
    The agents will repeat the process of data extraction, review, and updating for each file in the "in_process" directory. 
    For each PDF file, if the data is deemed accurate by the table reviewer agent and updated in the database by the database updater agent, return 'SUCCESS' along with a summary of the number of invoices and products successfully processed for each file.
    If the data is deemed inaccurate by the table reviewer agent or not updated in the database by the database updater agent, return 'FAILURE' along with a summary of the feedback from the table reviewer agent and the database updater agent.
    There will be a single summary returned at the end of the workflow showing the end result for each PDF file.
    After all the files in the "in_process" directory have been processed, you can respond with TERMINATE.
    """ )
'''







if __name__ == "__main__":
    asyncio.run(run_agents())