from sqlalchemy import create_engine, Column, Integer, String, Float, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in the environment or .env file")

Base = declarative_base()

#create database 'engine'
engine = create_engine(DATABASE_URL, echo=True)

# Create a configured "Session" class
Session = sessionmaker(bind=engine)

# Function to get a new session
def get_session():
    return Session()


# add invoice overview values to invoice table
def add_to_invoice_table(
        invoice_company: str,
        invoice_number: str,
        invoice_date,
        invoice_total: float):
    session = get_session()
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
        boat_id = result.scalar()  # Retrieve the id value
        session.commit()
        return boat_id
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


# add product invoice values to products table
def add_to_products_table(
        invoice_id: str,
        product_name: str,
        product_seller: str,
        product_amount: float):
    # the invoice_id value is the id returned from the invoice table upon insertion
    session = get_session()
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
        boat_id = result.scalar()  # Return the id value
        session.commit()
        return boat_id
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()