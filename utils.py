import PyPDF2  # build a tool
import os
import shutil
from autogen_core.tools import FunctionTool


def move_file(current_dir, target_dir, file_name):
        '''
        Move pdf file to another directory
        '''
        #shutil.copy2(os.path.join(current_dir, file_name), target_dir)
        shutil.move(os.path.join(current_dir, file_name), target_dir)


def extract_text_from_pdf(file_path):
        """Extracts text from a PDF file."""
        text = ""
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text()
        return text



extract_tool = FunctionTool( extract_text_from_pdf, description = "Returns text from a PDF file.")
