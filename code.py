import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from time import sleep
from random import randint

from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import csv

from dotenv import load_dotenv
load_dotenv()

CSV_FILE_NAME=str(datetime.today())[:13]+'.csv'
CSV_FILE_HEADER=['Search','TOT/TA','STA','ARCID','ATYP','RM','ADEP','ADES','D','T','ARF','IOBT','LV','U','E/CTOT','X','F','S','CL','A/TTOT','AT','TOBT','TSAT','TT','Delay','R','Opp','W','MSG','REGUL+','O','','Impacted']

delimiter=os.getenv('DELIMITER')

def init(overwrite=False):
  if not os.path.exists(CSV_FILE_NAME) or overwrite:
    with open(CSV_FILE_NAME,'w',newline='',encoding='utf-8-sig') as csvfile:
      filewriter = csv.DictWriter(csvfile, delimiter=delimiter, fieldnames=CSV_FILE_HEADER)
      filewriter.writeheader()

def writeRow(rowDict,removeExtra=False):
  with open(CSV_FILE_NAME,'a',newline='',encoding='utf-8-sig') as csvfile:
    filewriter = csv.DictWriter(csvfile, delimiter=delimiter, fieldnames=CSV_FILE_HEADER)
    
    if removeExtra:
      extra_header=set(rowDict.keys())-set(CSV_FILE_HEADER)
      if extra_header != set(): print(extra_header)
      for e in extra_header:
        del rowDict[e]
    filewriter.writerow(rowDict)

init(True)


print("[-] Loading list of airport Codes from Google Sheet")
airdromes=pd.read_csv(os.getenv('GSHEET_LINK'))['Airdrome'].dropna().tolist()


print("[-] Opening up the browser")
browser=webdriver.Firefox(executable_path = os.getenv('DRIVER_PATH'))
print("[-] Navigating to the website")
browser.get(os.getenv('STARTING_URL'))

# Login process starts here
username = browser.find_element_by_name("username")
username.clear()
username.send_keys(os.getenv('USER'))

print("[?] Please enter the passcode and click on Login")
while True:
  if browser.current_url == os.getenv('STARTING_URL'):
    print("[*] Waiting 30 seconds for user to Login.")
    sleep(30)
    continue
  else:break
  
print("[-] Successfully logged-in")
# Naivigate to dashbaard

print("[-] Navigating to Dashboard")
browser.get(os.getenv('DASHBOARD_LINK'))

# Wait for pageload
WebDriverWait(browser, 1000)\
  .until(EC.presence_of_element_located(\
    (By.ID, "TAC")))

print("[-] Moving to Tacticals Tab")

# Click on Tacticals
browser.find_element_by_id('TAC').click()

# Wait for Tacticals Tab to show up
WebDriverWait(browser, 50)\
  .until(EC.presence_of_element_located(\
    (By.ID, os.getenv('ID_FLIGHT_LIST'))))

print("[-] Showing a new windows for Flight List")
# Open Flight lists new window
browser.find_element_by_id(os.getenv('ID_FLIGHT_LIST')).click()

# Wait implicitly for 8 seconds for browser to load the window completely
sleep(8)

print("[-] Switched to Flight List Popup Window")

# Switch to Flight List.
for window in browser.window_handles:
    browser.switch_to.window(window)
    if browser.title=='Flight List':
        break

# Wait for Flight List page to fully loadup so we could click on Aerodrome Tab.
WebDriverWait(browser, 10)\
  .until(EC.presence_of_element_located(\
    (By.XPATH, os.getenv('XPATH_AERODROME'))))

# Switch to Aerodrome Tab.
AERODROME=browser.find_element_by_xpath(os.getenv('XPATH_AERODROME'))
if AERODROME.text=='Aerodrome': AERODROME.click()
else:   print("Something wrong happened with XPATH")

WebDriverWait(browser, 10)\
  .until(EC.presence_of_element_located(\
    (By.ID, os.getenv('ID_INPUT_AERODROME'))))

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
  print(airdrome,end='')
  
  INPUT_AERODROME.clear()
  INPUT_AERODROME.send_keys(airdrome)
  SEARCH_BUTTON.click()
  
  sleep(4)
  
  WebDriverWait(browser, 10)\
  .until(EC.presence_of_element_located(\
    (By.ID, os.getenv('ID_FLIGHTLIST_TABLE'))))
  
  pageParser=BeautifulSoup(browser.page_source,'html.parser')
  records=pageParser.find('table',id=os.getenv('ID_FLIGHTLIST_TABLE')).findAll('tr', {'id': not None})
  print(' ', len(records))
  for record in records:
    # First two coloumns were empty
    record_line=[td.getText().strip() for td in record.findAll('td', {'id': not None})[2:]]
    # Related keys are assigned to all of the fields
    dataRecord=dict(zip(CSV_FILE_HEADER, record_line))
    dataRecord['Search']=airdrome

    writeRow(dataRecord)

  SLEEP_SECONDS=randint( 0 ,40)
  print(f"[=] On Pause for {(SLEEP_SECONDS%3600)%60} seconds")
  sleep(SLEEP_SECONDS)

browser.close()