from sqlalchemy import create_engine
import os

engine = create_engine(os.getenv("DATABASE_URL")) 

def invoice_to_db(data, pdf_path):
    ''' Inserts the newly extracted invoice data into the database'''
    pass

def 