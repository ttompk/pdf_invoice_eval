import os
import sys_pdf
base_dir = "pdf_inbox"
working_dir = "in_process"

def sweep_to_in_process(base_dir):
    ''' This function moves all PDF files from the directory to the in_process directory. '''
    for pdf_file in n_pdf_files(base_dir):
        os.rename(os.path.join(directory, pdf_file), os.path.join("in_process", pdf_file))


for filename in working_dir:
    for file_name in os.listdir(working_dir):
        # Extract text from the PDF
        text = sys_pdf.extract_text_from_pdf(file_name)

        # Call the LLM for extraction
        