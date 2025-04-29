# source: https://github.com/Azure-Samples/python-ai-agent-frameworks-demos/blob/main/examples/autogen_magenticone.py
import asyncio
import os
from dotenv import load_dotenv

#import azure.identity
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import MagenticOneGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient, OpenAIChatCompletionClient


load_dotenv(override=True)
#API_HOST = os.getenv("API_HOST", "github")
BASE_URL = os.getenv("BASE_URL")
MODEL_NAME = os.getenv("GITHUB_MODEL")
API_KEY = os.getenv("GITHUB_TOKEN")

client = OpenAIChatCompletionClient(model=MODEL_NAME, api_key=API_KEY, base_url=BASE_URL)


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
    

table_agent = AssistantAgent(
    name="table creator",
    model_client=client,
    description="A worker that extracts values from text to build tables.",
    system_message=f"""
    You are an expert in extracting structured data from text. 
    You must create two tables, one named overview and the other named products.
    Here is information about the overview table: {build_overview_prompt} and here is the informaiton on products table: {build_products_prompt}.
    These tables will be submitted to the table reviewer agent for validation.
    If you are unable to extract the data from the text, return 'FAILED' along with a one sentence description of the failure reason.
    You will repeat the process of data extraction for each file in the "in_process" directory.
    """
)

reviewer_agent = AssistantAgent(
    name="table reviewer",
    model_client=client,
    description="An agent that reviews the tables created by the table creator agent.",
    system_message=f"""
    You are an expert in reviewing tabulized data. 
    You must review the tabulized data from the table creator agent and provide feedback on the accuracy of the data. 
    The tabulized data must align with the existing data in the database table: XYZ. 
    In some instances, the underlying text data may not contain invoice data or may have incomplete invoice data. In these cases it may be impossible for the table creator agent to create a table.  
    If the data is accurate, return 'ACCURATE'. 
    If the data is inaccurate, return 'INACCURATE' and provide a JSON object with the following keys: overview_feedback and products_feedback. Each key should contain a list of strings that describe the inaccuracies in the respective tables. The overview table contains invoice_date, invoice_number, invoice_company, invoice_total. The products table contains invoice_number, product_name, product_seller, product_amount.
    If the table creator agent is unable to produce a correct table after three attempts, return 'FAILED' along with a one sentence description of the failure reason. 
    """)

database_agent = AssistantAgent(
    name= "database updater",
    model_client=client,
    description="An agent that updates the database with the tabulized data.",
    system_message=f"""
    You are an expert in updating databases with tabulized data.
    You must update the database table overviews and products with the tabulized data from the table creator agent if the data is deemed accurate by the table reviewer agent.
    If the data is deemed inaccurate by the table reviewer agent, you must not update the database.
    If the data is deemed failed by the table reviewer agent, you must not update the database.
    You must return a JSON object with the following keys: overview_updated and products_updated. Each key should be a boolean value indicating whether the respective table was updated in the database.
    If there is a failure in updating the database, rollback the update and return a JSON object with the following keys: overview_updated, products_updated, and failure_reason. Each key should be a boolean value indicating whether the respective table was updated in the database and a string describing the failure reason.
    """)

summary_agent = AssistantAgent(
    name="summary agent",
    model_client=client,
    description="An agent that summarizes the results of the workflow.",
    system_message=f"""
    You are an expert in summarizing the results of workflows.
    You must summarize the results of the workflow based on the feedback from the table reviewer agent and the database updater agent.
    The agents will repeat the process of data extraction, review, and updating for each file in the "in_process" directory. 
    If the data is deemed accurate by the table reviewer agent and updated in the database by the database updater agent, return 'SUCCESS' along with a summary of the data that was updated in the database.
    If the data is deemed inaccurate by the table reviewer agent or not updated in the database by the database updater agent, return 'FAILURE' along with a summary of the feedback from the table reviewer agent and the database updater agent.
    After all the files in the "in_process" directory have been processed, you can respond with TERMINATE.
    """)

async def run_agents():
    termination = TextMentionTermination("TERMINATE")
    group_chat = MagenticOneGroupChat(
        [table_agent, reviewer_agent, database_agent, summary_agent],
        termination_condition=termination,
        model_client=client,
    )
    await Console(group_chat.run_stream(task="Extract table data from text and insert into a database."))