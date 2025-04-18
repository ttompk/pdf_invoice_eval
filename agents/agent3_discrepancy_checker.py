from sqlalchemy import create_engine
import os

engine = create_engine(os.getenv("DATABASE_URL"))

def check_discrepancies():
    '''This call to LLM will check for discrepancies in the data.'''
    pass
