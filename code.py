import os
from selenium import webdriver
from time import sleep
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import csv

from dotenv import load_dotenv
load_dotenv()

CSV_FILE_NAME=str(datetime.today())[:13]+'.csv'
CSV_FILE_HEADER=['TOT/TA','STA','ARCID','ATYP','RM','ADEP','ADES','D','T','ARF','IOBT','LV','U','E/CTOT','X','F','S','CL','A/TTOT','AT','TOBT','TSAT','TT','Delay','R','Opp','W','MSG','REGUL+','O','','Impacted']

def init(overwrite=False):
  if not os.path.exists(CSV_FILE_NAME) or overwrite:
    with open(CSV_FILE_NAME,'w',newline='',encoding='utf-8-sig') as csvfile:
      filewriter = csv.DictWriter(csvfile, fieldnames=CSV_FILE_HEADER)
      filewriter.writeheader()

def writeRow(rowDict,removeExtra=False):
  with open(CSV_FILE_NAME,'a',newline='',encoding='utf-8-sig') as csvfile:
    filewriter = csv.DictWriter(csvfile, fieldnames=CSV_FILE_HEADER)
    if removeExtra:
      extra_header=set(rowDict.keys())-set(CSV_FILE_HEADER)
      if extra_header != set(): print(extra_header)
      for e in extra_header:
        del rowDict[e]
    filewriter.writerow(rowDict)

init(True)

airdromes=set(pd.read_csv(os.getenv('GSHEET_LINK'))['Airdrome'].tolist())

browser=webdriver.Firefox(executable_path = os.getenv('DRIVER_PATH'))
browser.get(os.getenv('STARTING_URL'))

# Login process starts here
username = browser.find_element_by_name("username")
username.clear()
username.send_keys(os.getenv('USER'))

print("Please enter the passcode and click on Login")
print("Waiting for you to click on Login.")
while True:
    sleep(1*60)
    if browser.current_url == os.getenv('STARTING_URL'):
        continue
    else:
        break
print("Successfully logged-in")
# Naivigate to dashbaard
browser.get(os.getenv('DASHBOARD_LINK'))
# Click on Tacticals
browser.find_element_by_id('TAC').click()
# Open Flight lists new window
browser.find_element_by_id(os.getenv('ID_FLIGHT_LIST')).click()
# Switch to Flight List.
for window in browser.window_handles:
    browser.switch_to.window(window)
    if browser.title=='Flight List':
        break
# Switch to Aerodrome Tab.
AERODROME=browser.find_element_by_xpath(os.getenv('XPATH_AERODROME'))
if AERODROME.text=='Aerodrome': AERODROME.click()
else:   print("Something wrong happened with XPATH")


INPUT_AERODROME = browser.find_element_by_id(os.getenv('ID_INPUT_AERODROME'))
INPUT_WEF       = browser.find_element_by_id(os.getenv('ID_INPUT_WEF'))
INPUT_UNT       = browser.find_element_by_id(os.getenv('ID_INPUT_UNT'))
SEARCH_BUTTON   = browser.find_element_by_id(os.getenv('ID_SEARCH_BUTTON'))

INPUT_AERODROME.clear()

INPUT_WEF.clear()
INPUT_UNT.clear()
INPUT_WEF.send_keys('0000')
INPUT_UNT.send_keys('0000')

for airdrome in airdromes:
  sleep(1*60)
  print(airdrome,end='')
  
  INPUT_AERODROME.clear()
  INPUT_AERODROME.send_keys(airdrome)
  SEARCH_BUTTON.click()

  pageParser=BeautifulSoup(browser.page_source,'html.parser')
  # TODO Add id for total flights here
  print(' ',pageParser.find('').getText())

  #  TODO Add id here
  for record in pageParser.find('table',id='').findAll('tr', {'id': not None}):
    # First two coloumns were empty
    record_line=[td.getText().strip() for td in record.findAll('td', {'id': not None})[2:]]
    # Related keys are assigned to all of the fields
    dataRecord=dict(zip(CSV_FILE_HEADER, record_line)) 
    writeRow(dataRecord)

"""
browser.close()
"""
