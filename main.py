import os
import sys_pdf
import agents.agent1_table_extractor as a1
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient, OpenAIChatCompletionClient


# The directories
base_dir = "pdf_inbox"  # where the user has stored the PDF invoices.
working_dir = "in_process"  # where the program moves the files while they are being processed.
completed_dir = "processed_invoices"  # where the program moves the files if they have been successfullly processed.
failed_dir = "failed_invoices"  # where the program moves the files if they have failed to be processed.

def sweep_to_in_process(base_dir):
    ''' This function moves all PDF files from the base directory to the in_process directory. '''
    for file_name in os.listdir(base_dir):
        os.rename(os.path.join(base_dir, file_name), os.path.join("in_process", file_name))


for file_name in os.listdir(working_dir):
    
    # Extract text from the PDF
    raw_text = sys_pdf.extract_text_from_pdf(file_name)

    # Call the agent 1 to create the tables
    agent1 = a1.Agent1PDFExtractor(raw_text)

    # call agent 2 to review the tables
    agent2 = ""

    # if response from agent2 is "success". 
    if agent2.response == "success":
        # write overview table to database
        # write product table to database
        # move the original PDF to the processed_invoices directory
        sys_pdf.move_file(working_dir, completed_dir, file_name)

    sys_pdf.move_file(self.working_dir, "processed", file_name)
    os.rename(os.path.join(directory, pdf_file), os.path.join("in_process", pdf_file))