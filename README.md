# PDF-to-Database

## The problem
A company regularly receives invoices in PDF format. The PDF invoices are the main record by which the company is compensated by their various servicers. The number of servicers is known and limited. The invoices contain the dollar amount distributed to the company for a particular service, called an 'account' internally. Additional information pertaining to the account, the date, and the servicer's name, among other data, are also included in the invoice PDF. Payment amounts in the PDF are manually entered into an Excel file. These values are then matched to expected payment amounts within the same spreadsheet. Discrepencies are flagged and followed up by staff to correct. These payments are estimated to be wrong 20% of the time and thus require immense scrutiny.

## Current methodology
The PDFs are recieved by eamil or downloadeed from the servicer, opened by the user, and then the invoice data are manually copied and pasted into a spreadhseet. This spreadsheet contains information on each of the accounts and the expected payment from the servicer to the account.  The expected payment was previously entered in by the user. The spreadsheet also holds associated account data such as the company personell responsible for the project and other aspects of the company business as defined by internal business logic. This informaiton is copy and pasted from other sources to create the spreadsheet. 

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
Build an AI multi-agent system that:
- Agent 1: Views the invoice PDF and reasons about the PDF and returns a pre-specified formatted table with the account details, invoice date, and invoice amount. 
- Agent 2: Reviews the formatted data passed by Agent 1. Agent 2 decides whether the data as formatted by Agent 1 makes sense to enter into a pre-specified database table. If it approves of the insert it then enters the invoice data into the database table. If agent 2 does not approve it will ask Agent 2 to repeat the PDF data extraction. If the second extraction fails, Agent 2 will log the failure into a database table and the file will be moved to another directory for user evaluation. 
- Agent 3: Compares the newly extracted values to the expected compensation values and flags any potential issues (if any). Issues include being paid less than or more than the expected value. Agent 2 then enters a value into the database table signifiying there was or was not a difference between the new extracted invoice value and the expected value. 
- Agent 3: After all the PDF files have been ran through and the data insrted into the database, Agent 4 will review the newly entered data (and those PDF files it could not extract), and will write a brief report on the outcome. This report should list any PDF fils that Agent 1 could not extract data from, any PDF ivoice data which was extracted and enterded into the database, and if there were any differences between the extracted invoice values and the expected values. If there are differences, Agent 3 will provide an explanation for each issue which can be copied by the user to send via email to the apprioriate service provider. This explanation should describe the invoice and discrepancy and request a correction to the invoice amount. 



## Workflow Detail
1. User manually saves an invoice PDF to a "to_be_extracted" directory.
2. Every night at 12am a bash file is runs a chron job. The bash file moves the files in the directory holding the PDF files to an "in_process" directory. Afterwards it runs a python file which contains the agent program. The agent program is built using the autogen framework. There is a planner agent that controls execution of the following agents. 
3. Agent 1 is named "table creator" and is called to open a PDF file from the "in_process" directory, read the contents, and populate a table or tables with the invoice data.
4. Agent 2 is named "table reviewer" and performs a validation check on Agent 1's work to be certain the extracted data format fits within the existing data structure expectations. This requires Agent 2 to examine the most recent 200 invoices in the database and the invoice PDF. If the extracted data passes Agent 2's review, i.e. the extracted data fit the expected formatting:
- Agent 2 inserts the invoice data into a database table named "invoices"
- Agent 2 updates the "extraction" database table with the filename, company name (extracted by Agent 1), invoice date, and flag for passing. 
- Agent 2 moves the invoice PDF to the "completed_extraction" directory. 

5. If Agent 2 fails Agent 1's extraction it refines the prompt for Agent 1 and asks Agent 1 to repeat the data extraction.
6. Agent 2 then evaluates Agent 1's new response. If Agent 2 approves theextraction, Agent 2 performs the steps outlined in number 4. If Agent 2 fails the extraction again:
- Agent 2 records the reason for the failure in the "extraction" table
- The invoice PDF file is moved to a directory named "failed_extraction". 
 
7. Agent 1 then repeats the cycle with the next PDF until all PDFs are read and uploaded to the database.
8. After all the PDF files have been extracted and evaulated, Agent 3 will write a brief report containing: 
- the number of files read with the number of files that passed and failed. 
- compare the invoices in the "expected_invoices" table with the newly entered invoices. If there are any differences between the newly extracted invoice dollar amounts and the expected dollar amounts then the agent will provide an explanation for each conflicting invoice. Each explaination should be two to three sentences. This report should be emailed to the user who will copy and send via email to the apprioriate service provider. This explanation should describe the invoice, the invoice discrepancy, and request a correction to the invoice amount. 

### Required Infrastructure
- database = postgres
- email = gmail
- multi-agent framework = autogen
- sql framework = sqlalchemy
- environment manager = conda
- store database and LLM connection strings in .env file (add to .gitignore)
- would prefer to use model context protocol to connect the database and email

