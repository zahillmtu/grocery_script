#!python3
# Example api usage from google.com
from __future__ import print_function
import httplib2
import os
import io
import re
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

def find_dash_ln(fileName, dash_num):
    """Method to find the line number of the location of dashes
    in the text documents. The second argument is used to specify
    if finding the first or second set of dashes.

    If no dashes are found will return -1, otherwise returns line number
    """
    counter = 0

    with open(fileName, 'r') as file:
        for num, line in enumerate(file, 1):
            m1 = re.search('---+---', line)
            if m1:
                if (dash_num == 1):
                    return num
                elif (dash_num == 2 and counter == 1):
                    return num
                else:
                    counter = counter + 1

    return -1 # if here no TEST PROCEDURE found


def erase_content():
    """Erase the content between the first and second '---'
    ----------------------------
    This content will be erased
    ----------------------------
    """

    # Read in the file data
    with open(FILE_LOC, 'r') as fin:
        data = fin.read().splitlines(True)

    # Find the dash line numbers
    d_line1 = find_dash_ln(FILE_LOC, 1)
    if (d_line1 == -1):
        # ERROR
        print('ERROR: Could not find first line of dashes in file')
    d_line2 = find_dash_ln(FILE_LOC, 2)
    if (d_line2 == -1):
        # ERROR
        print('ERROR: Could not find second line of dashes in file')

    # Write the contents outside the dashes back to file
    with open(FILE_LOC, 'w') as fout:
        fout.writelines(data[:d_line1])
        fout.writelines('\n')
        fout.writelines(data[d_line2 - 1:])


def find_date():
    """ Find the date from the first line of the google Doc """

    # Read in the second line of the file
    f = open(FILE_LOC, 'r', encoding="utf-8-sig")
    print("Name of file: ", f.name)

    line = f.readline()
    print("The first line of the file: ", line)

    # Search the first line of code for the date
    # Code example given by Matt Mead
    m1 = re.search('.*?(\d+\/\d+\/\d+)', line)
    if m1:
        whole_date = m1.groups()[0]
    else:
        # The script can't find the date, most likely because it is not
        # formatted correctly or is not in the first line
        send_email('The date is not formatted properly')
        return

    groc_day = int(whole_date[0:2])
    groc_month = int(whole_date[3:5])
    groc_year = int(whole_date[6:10])
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
        # Clear out old grocery list
        erase_content()

    print()

    print((doc_date - date_today).days)
    # The purchase date should be a monday, so we need to send a reminder on Friday
    # If the date is 3 days out, send a reminder
    if ((doc_date - date_today).days == 3):
        print('It should be Friday Today')

    print()
    f.close()

    # Find the current date
    cur_date = time.strftime("%x")
    print(cur_date)

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

if __name__ == '__main__':
    main()

