from sqlalchemy import create_engine, Column, Integer, String, Float, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
import asyncio


class db_update:

    def __init__(self):
        """
        Initialize the database connection.
        """
        self.connect_to_db()


    def connect_to_db(self):
        """
        Connect to the database using SQLAlchemy.
        """
        # Load environment variables from .env file
        load_dotenv()
        DATABASE_URL = os.getenv('DATABASE_URL')
        if not DATABASE_URL:
            raise ValueError("DATABASE_URL is not set in the environment or .env file")

        Base = declarative_base()

        #create database 'engine'
        self.engine = create_engine(DATABASE_URL, echo=True)

       
    # Function to get a new session
    def get_session(self):
        # Create a configured "Session" class
        self.Session = sessionmaker(bind=self.engine)


    # add invoice overview values to invoice table
    def update_invoices_table(
            self,
            invoice_date: str,
            invoice_number: str,
            invoice_company: str,
            invoice_total: float):
        session = self.get_session()
        try: 
            query = text('''
                        INSERT INTO invoices (invoice_company, invoice_number, invoice_date, invoice_total) 
                        VALUES (:invoice_company, :invoice_number, :invoice_date, :invoice_total)
                        RETURNING id;
                        ''')
            result = result = session.execute(query, {
                    "invoice_company": invoice_company,
                    "invoice_number": invoice_number,
                    "invoice_date": invoice_date,
                    "invoice_total": invoice_total
                })
            invoice_id = result.scalar()  # Retrieve the id value
            session.commit()
            return invoice_id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()


    # add product invoice values to products table
    def update_products_table(
            self,
            invoice_id: str,
            product_name: str,
            product_seller: str,
            product_amount: float):
        """
        Update product details to the products table.
        """
        # the invoice_id value is the id returned from the invoice table upon insertion
        session = self.get_session()
        try: 
            query = text('''
                        INSERT INTO products (invoice_id, product_name, product_seller, product_amount) 
                        VALUES (:invoice_id, :product_name, :product_seller, :product_amount)
                        RETURNING id;
                        ''')
            result = result = session.execute(query, {
                    "invoice_id": invoice_id,
                    "product_name": product_name,
                    "product_seller": product_seller,
                    "product_amount": product_amount
                })
            product_id = result.scalar()  # Return the id value
            session.commit()
            return product_id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()


    def update_files_table(
            self,
            filename: str,
            status: str,
            fail_reason: str,
            number_invoices: int,
            number_products: int):
        """
        Update the files table with the given parameters.
        """
        # the invoice_id value is the id returned from the invoice table upon insertion
        session = self.get_session()
        try: 
            query = text('''
                        INSERT INTO files (filename, status, fail_reason, number_invoices, number_products) 
                        VALUES (:filename, :status, :fail_reason, :number_invoices, :number_products) 
                        RETURNING id;
                        ''')
            result = session.execute(query, {
                    "filename": filename,
                    "status": status,
                    "fail_reason": fail_reason,
                    "number_invoices": number_invoices,
                    "number_products": number_products
                })
            file_id = result.scalar()  # Return the id value, this id appended to start of filename
            session.commit()
            return file_id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()



'''  wrapper function NOT needed with autogen FunctionTool
# Define the function wrapper
async def invoice_function(
        invoice_company: str,
        invoice_number: str,
        invoice_date,
        invoice_total: float) -> str:
    """
    Wraps the function call and handles any necessary pre or post processing
    """
    try:
        result = await add_to_invoice_table(invoice_company, invoice_number, invoice_date, invoice_total)
        return result
    except Exception as e:
        return f"An error occurred: {e}"
'''

