import PyPDF2  # build a tool
import os
import shutil


def move_file(current_dir, target_dir, file_name):
	'''
	Move pdf file to another directory
	'''
	#shutil.copy2(os.path.join(current_dir, file_name), target_dir)
	shutil.move(os.path.join(current_dir, file_name), target_dir)


def extract_text_from_pdf(filename: str):
	"""
	Extracts text from a PDF file.
    Inputs:
    	- filename: pdf file name
    Outputs:
		- str. The text extracted from the pdf
    """
	text = ""
	with open(filename, 'rb') as file:
		reader = PyPDF2.PdfReader(file)
		for page in reader.pages:
			text += page.extract_text()
	return text


def to_working_dir(source_dir, target_dir):
    '''Searches the pdf_inbox directory. If there are files, moves to in_process directory for agent use'''
    
    n_files_source = len(os.listdir(source_dir))

    try:
        if n_files_source > 0:   # are there files?
            for file_name in os.listdir(source_dir):   # move files from source to target
                move_file(source_dir, target_dir, file_name)

            n_files_target = len(os.listdir(target_dir))
            if n_files_target == n_files_source:
                log_value = f"Files in inbox: {n_files_source}. Moved to working dir: {n_files_target}. "
                return True
        
        else:  # when there are no files in the inbox
            # make log entry
            return False
            
    except:
        # error moving files.
        error_msg = "There was an error accessing or moving the PDF files."
        print(error_msg)
        return False
    


def get_file_list(target_dir):
	'''Returns a list of the file names in the working directory'''
	
	file_list = []
	for file_name in os.listdir(target_dir):
		if file_name.endswith('.pdf'):
			file_list.append(file_name)
	return ", ".join(file_list)

