from selenium import webdriver
from time import process_time_ns, sleep

import smtplib
import time
import imaplib
import email
import traceback
import json

from selenium.webdriver.common.action_chains import ActionChains


PHONE=""
PINCODE = ""
URL="https://selfregistration.cowin.gov.in/"


def read_email_from_gmail():

    ORG_EMAIL = "@gmail.com" 
    FROM_EMAIL = "" + ORG_EMAIL 
    FROM_PWD = "" 
    SMTP_SERVER = "imap.gmail.com" 
    SMTP_PORT = 993

    OTP = None

    try:
        mail = imaplib.IMAP4_SSL(SMTP_SERVER)
        mail.login(FROM_EMAIL,FROM_PWD)
        mail.select('inbox')

        data = mail.search(None, 'ALL')
        mail_ids = data[1]
        id_list = mail_ids[0].split()   
        first_email_id = int(id_list[0])
        latest_email_id = int(id_list[-1])

        try:

            for i in range(latest_email_id,first_email_id, -1):
                data = mail.fetch(str(i), '(RFC822)' )
                for response_part in data:
                    arr = response_part[0]
                    if isinstance(arr, tuple):
                        msg = email.message_from_string(str(arr[1],'utf-8'))
                        email_subject = msg['subject']
                        email_from = msg['from']
                        if "CoWIN" in email_from:
                            email_payload:str = msg.get_payload(decode=True).decode('UTF-8')
                            end = email_payload.rfind('}')
                            content = email_payload[0:end+1]
                            obj= json.loads(content)
                            OTP = obj["otp"]
                            mail.store(str(i), '+FLAGS', '\\Deleted') 
                            return OTP
        
        except Exception as e:

            print(str(e))

        finally:

            mail.expunge()                    

    except Exception as e:
        traceback.print_exc() 
        print(str(e))


def find_schedule(url, phonenumber, pincode):

    try:
        driver = None

        options = webdriver.ChromeOptions()
        options.add_argument("no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--start-maximized")
        options.add_argument("--headless")
        options.add_argument("window-size=1024,900")


        print("Starting headless chrome...")

        driver = webdriver.Chrome(options=options, executable_path="/home/rajdeeprath/chromedriver_linux64/chromedriver");
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'})
        
        print("Loading CoWIN website...")

        driver.get(url)
        driver.implicitly_wait(10)

        sleep(5)
        print("Entering phone number to request OTP...")
        mobinput = driver.find_element_by_xpath('//*[@id="mat-input-0"]')
        mobinput.send_keys(phonenumber)
        getotpbtn = driver.find_element_by_xpath('/html/body/app-root/ion-app/ion-router-outlet/app-login/ion-content/div/ion-grid/ion-row/ion-col/ion-grid/ion-row/ion-col[1]/ion-grid/form/ion-row/ion-col[2]/div/ion-button')
        getotpbtn.click()

        sleep(15)
        otp = read_email_from_gmail()

        if otp == None:
            raise Exception("Could not get OTP :(")

        print("OTP received! Enter OTP...")
        driver.implicitly_wait(5)
        otp_input = driver.find_element_by_xpath('/html/body/app-root/ion-app/ion-router-outlet/app-login/ion-content/div/ion-grid/ion-row/ion-col/ion-grid/ion-row/ion-col/ion-grid/form/ion-row/ion-col[2]/ion-item/mat-form-field/div/div[1]/div/input')
        otp_input.send_keys(otp)
        otp_submit_btn = driver.find_element_by_xpath('/html/body/app-root/ion-app/ion-router-outlet/app-login/ion-content/div/ion-grid/ion-row/ion-col/ion-grid/ion-row/ion-col/ion-grid/form/ion-row/ion-col[3]/div/ion-button')
        otp_submit_btn.click()

        sleep(5)
        print("Preparing to look for available schedules")
        driver.implicitly_wait(10)
        schedule_button=driver.find_element_by_xpath('/html/body/app-root/ion-app/ion-router-outlet/app-beneficiary-dashboard/ion-content/div/div/ion-grid/ion-row/ion-col/ion-grid[1]/ion-row[4]/ion-col/ion-grid/ion-row[4]/ion-col[2]/ul/li')
        hov = ActionChains(driver).move_to_element(schedule_button)
        hov.perform()
        schedule_button.click()

        sleep(5)
        print("Entering desired pincode " + pincode + " to look for specific centers")
        driver.implicitly_wait(5)
        search_pincode_input = driver.find_element_by_xpath('/html/body/app-root/ion-app/ion-router-outlet/app-appointment-table/ion-content/div/div/ion-grid/ion-row/ion-grid/ion-row/ion-col/ion-grid/ion-row/ion-col[2]/form/ion-grid[1]/ion-row[1]/ion-col[3]/mat-form-field/div/div[1]/div/input')
        search_pincode_input.send_keys(pincode)
        search_button = driver.find_element_by_xpath('/html/body/app-root/ion-app/ion-router-outlet/app-appointment-table/ion-content/div/div/ion-grid/ion-row/ion-grid/ion-row/ion-col/ion-grid/ion-row/ion-col[2]/form/ion-grid[1]/ion-row[1]/ion-col[4]/ion-button')
        search_button.click()

        driver.implicitly_wait(5)
        age_filter_btn = driver.find_element_by_xpath('/html/body/app-root/ion-app/ion-router-outlet/app-appointment-table/ion-content/div/div/ion-grid/ion-row/ion-grid/ion-row/ion-col/ion-grid/ion-row/ion-col[2]/form/ion-grid[1]/ion-row[2]/ion-col[1]/div/div[1]/label')
        age_filter_btn.click()
        

        sleep(5)
        driver.implicitly_wait(5)
        driver.get_screenshot_as_file("/home/rajdeeprath/screenshot.png")

    except Exception as e:

        print(str(e))

    finally:
        if driver != None:
            driver.quit()


print("Starting")
sleep(5)
find_schedule(URL, PHONE, PINCODE)
