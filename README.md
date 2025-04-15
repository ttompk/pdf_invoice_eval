# PDF-to-Database

## The problem
A company regularly receives invoices in PDF format. The PDF invoices are the main record by which the company is compensated by their various servicers. The number of servicers is known and limited. The invoices contain the dollar amount distributed to the company for a particular service, called an 'account' internally. Additional information pertaining to the account, the date, and the servicer's name, among other data, are also included in the invoice PDF. Payment amounts in the PDF are manually entered into an Excel file. These values are then matched to expected payment amounts within the same spreadsheet. Discrepencies are flagged and followed up by staff to correct. These payments are estimated to be wrong 20% of the time and thus require immense scrutiny.

## Current methodology
The PDFs are recieved by eamil or downloadeed from the servicer, opened by the user, the invoice data are manually copied and pasted into a spreadhseet. This spreadsheet holds information on the accounts and the expected payment from the servicer to the account.  The spreadsheet holds associated account data such as the company personell responsible for the project and other aspects of the company business as defined by internal business logic. This informaiton is copy and pasted from other sources to create the spreadsheet. 

### Downsides and Upsides of current methodology
The current methodolology has several DOWNSIDES:  
1. Human error - copy and pasting into excel spreadsheets can introduce human error.
2. No immutable record - unless spreadsheets are being saved as flat files at regular intervals, then all invoice history is editable. The original invoices are presevered but the basis for business decisioning (the purpose of the spreadsheet) remains editable.
3. Lack of organized persistant memory - A loss of a spreadsheet could mean the loss of transactional history.
4. Inefficiency - Maintaining spreadhseets, opening PDF files, hand entering values into a sheet, reasoning on the values, and taking downstream actions are time wasters.
5. Spreadsheets lack downstream analytical value - There could be value in analyzing invoice and account information over time, or many other analyses, but without a central, organized, longitudinal data depository it is likely the effort will be too great for unknown rewards.

The following UPSIDES are observed:  
1. No need for infrastructure beyond current file server. 
2. No need for maintanence of coding files. 
3. No technical skills required.
4. The number of acount payments evaluated weekly is small, approxiametly 10-20. 


## Proposed Remedy
Build an AI multi-agent that:
- LLM call 1 reasons about the PDF and returns a pre-specified formatted table
- LLM call 2 reviews the formatted data, if passes then enters table values into a database, else repeat once more.
- LLM call 3 compares the newly extracted values to expected compensation values and alerts the user to the potential issue (if any) 
- If required, LLM call3 pre-populates an email response to send to servicer with request to correct


## Workflow Overview
1. User manually saves PDFs to pre-determined directory
2. A bash file is run as a chron job on a server that sweeps files to a new directory 
3. New PDF files are interpreted and data formatted
4. A second LLM call evaulates the newly 'formatted' data to determine if it fits within the existing data structure expectations
5. If data appear to fit, data are inserted into database, if not, the second LLM refines the context and prompt and asks the first LLM to repeat the data extraction.
6. The second response is then evaluated again amd if the data fits then is inserted into the database, else the file is moved to another directory and a reason logged for failure to extract.
7. Using extracted data, the LLM searches existing servicer contracts, previous payments in the database, and other relevant information to the project to determine whether the new values match expected values.
8. The agent findings are then logged and a report is generated for the user. 
9. repeate steps 3 to 8 until all PDFs have been evaluated


### Workflow Detail
1. User manually saves an invoice PDF to a directory. Currently, files are downloaded from servicers and saved to a MS OneDrive. Any emailed invoices must be manually uploaded to the directory unless using MS Power Automate ($15/month cost)
2. Every night at 12am a bash file is run aon a chron job. python program runs that moves the files in the directory holding the PDF files to a working directory.
3. A python program then opens a PDF, reads the data, and decides automatically which table(s) to create. 
The program performs validation checks to be certain the data were collected and formatted as intended. If there is an error, a file will be saved stating such and an email or other means of notification can be sent stating there was an issue with the read.
4. The original PDF is moved to the proper directory for storage. If it threw an error then it goes to the ‘Error’ pile for manual entry :(
5. The newly created table(s) is saved as a CSV files in the assigned directory.
6. The data in memory is upload to an existing table in a postgres relational database. Proper upload is validated. If an error is thrown then the error will be logged in a separate table in the database or logged elsewhere as needed.
7. Program then moves to the next PDF until all are read and uploaded to the database.

### What to do with these database tables? 
- View with Power BI (or whatever tool you use currently)
- If investing in the data visualization software is not desirable, then an automatic export from the database to excel files as needed, weekly or whatever, can be performed. 

### Required Infrastructure
- A sever to securely save the files (you are doing this already presumably). On the same server as above you’ll save: python files (logic files) and a bash file (the automation file).
- A postgres database (free).

### Maintenance
- The python files need to be maintained when: PDF files from new vendors are added or there is a significant change in existing PDF formatting. 
- Database needs to be ‘cleaned’ at least twice a year. This is just a review of the database health to prevent any issues.
- Data visualization software...I’m thinking it’s really cheap - $5 a month per user? - ...needs to be set up to see the data and perform analysis. However, the free/nearly free version of Power BI does not allow one to update data in the underlying database. One can forsee a need to update the database, e.g. when a invoice value is misread, a separate program would be needed. 
