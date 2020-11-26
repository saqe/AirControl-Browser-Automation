import os
from selenium import webdriver
from time import sleep

browser=webdriver.Firefox(executable_path =os.getenv('DRIVER_PATH'))
browser.get(os.getenv('STARTING_URL'))

# Login process starts here
username = browser.find_element_by_name("username")
username.clear()
username.send_keys(os.getenv('USERNAME'))

print("Please enter the passcode and click on Login")
print("Waiting for you to click on Login.")
while True:
    sleep(1*60)
    if browser.current_url == os.getenv('STARTING_URL'):
        continue
    elif browser.current_url == os.getenv('AFTER_LOGIN_URL'):
        break
    else:
        print("Something wrong happened")

print("Successfully logged-in")

browser.close()
