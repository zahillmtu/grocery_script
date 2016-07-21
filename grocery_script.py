# Example api usage from google.com
from __future__ import print_function
import httplib2
import os 
import io
import time
from datetime import date # to compare dates
import smtplib # for sending emails
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from apiclient import discovery
from apiclient.http import MediaIoBaseDownload
import oauth2client
from oauth2client import client
from oauth2client import tools

import json

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Drive API Python Quickstart'
FILE_LOC = 'doc.txt' # Relative
# C:/Users/Zach/Documents/groceryList/
def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'drive-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def send_email(message):
    """ Send an email notification 
        Example taken from here: http://naelshiab.com/tutorial-send-email-python/
    """
    
    send_to = 'pswaregrocery@gmail.com'
    send_from = 'pswaregrocery@gmail.com'
    password = 'grpsware'

    fromaddr = 'pswaregrocery@gmail.com'
    toaddr = 'pswaregrocery@gmail.com'
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = 'Testing'

    body = message
    msg.attach(MIMEText(body, 'plain'))
 
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, password)
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()
    
    
def find_date():
    """ Find the date from the first line of the google Doc """
    
    # Read in the second line of the file
    f = open(FILE_LOC, 'r', encoding="utf-8-sig")
    print("Name of file: ", f.name)
    
    line = f.readline()
    print("The first line of the file: ", line)
    line2 = f.readline()
    print("The second line of the file: ", line2)
    
    groc_day = int(line2[0:2])
    groc_month = int(line2[3:5])
    groc_year = int(line2[6:10])
    print("groc_day: ", groc_day)
    print("groc_month: ", groc_month)
    print("groc_year: ", groc_year)
    
    date_today = date.today()
    doc_date = date(groc_year, groc_day, groc_month)
    
    print('Doc date: ', doc_date)
    print(date_today)
    # Check if date has passed, if so clear out if the day after
    if (doc_date < date_today):
        print('THE DATE HAS PASSED')
        # Send a reminder email
    
    print()
    
    print((doc_date - date_today).days)
    # The purchase date should be a monday, so we need to send a reminder on Friday
    # If the date is 3 days out, send a reminder
    if ((doc_date - date_today).days == 3):
        print('It should be Friday Today')
    
    
    print()
    f.close()
    
    f = open(FILE_LOC, 'a', encoding="utf-8-sig")
    f.write('I wrote this to the file\n')

    # Find the current date
    cur_date = time.strftime("%x")
    print(cur_date)
    
    f.close()
    
    return
    
def main():
    """Shows basic usage of the Google Drive API.

    Creates a Google Drive API service object and outputs the names and IDs
    for up to 10 files.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)

    #file_id = '1cxgbJZKnysKOKBDg-ZbV1E3S4B-iAG7XY-1x7U8Yfsg' # For the grocery doc
    file_id = '18r3cUWKbMaWVYtNKLJjxZFHB2m7y1QJdkSPlrU197PA' # For the test doc

    request = service.files().export_media(fileId=file_id, mimeType='text/plain')
    
    response = request.execute()

    fh = open(FILE_LOC, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))
        
        
    fh.close()
    # Now read doc.txt to get information
    find_date()
    
    # Upload the file back
    update_request = service.files().update(fileId=file_id, media_body=FILE_LOC)
    
    update_response = update_request.execute()
    
    send_email('This goes in the email')

if __name__ == '__main__':
    main()

