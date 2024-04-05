from random import randint
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException

options = Options()
options.add_argument('--no-sandbox')
# options.add_argument('--headless')
options.add_argument('--disable-dev-shm-usage')
options.add_argument("start-maximized")
options.add_argument("disable-infobars")
options.add_argument("--disable-extensions")
options.add_argument("--disable-gpu")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)

def login_to_linkedin(driver, username, password):
    print('\nSigning in... (Takes about 10 seconds)')
    url_to_sign_in_page = 'https://www.linkedin.com/login'
    driver.get(url_to_sign_in_page)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'session_key')))

    username_input = driver.find_element(By.NAME, 'session_key')
    password_input = driver.find_element(By.NAME, 'session_password')
    username_input.send_keys(username)
    password_input.send_keys(password)

    try:
        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
        submit_button.click()
    except TimeoutException:
        print("Timeout while trying to log in.")
    except ElementClickInterceptedException:
        print("Submit button was not clickable.")

    WebDriverWait(driver, 10).until(lambda d: d.current_url != url_to_sign_in_page)
    print('\nSuccessfully signed in!')

def chose_connect(driver, keywords, max_connect):
    print("\nBeginning connection request process...\nThere is a delay between requests intentionally to bypass bot detections.")
    i = 0
    page_number = 1

    while i < max_connect:
        try:
            keyword_query = "%20".join(keywords)
            url_link = f"https://www.linkedin.com/search/results/people/?keywords={keyword_query}&origin=SWITCH_SEARCH_VERTICAL&page={page_number}"
            driver.get(url_link)

            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "button")))
            all_buttons = driver.find_elements(By.TAG_NAME, "button")
            connect_buttons = [btn for btn in all_buttons if btn.text == "Connect"]

            if not connect_buttons:
                print(f"No 'Connect' buttons found on page {page_number}. Moving to next page.")
                page_number += 1
                continue

            for btn in connect_buttons:
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable(btn))
                btn.click()
                name = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']//strong")))
                print(f"Sending connection request to {name.text}")

                send_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Send now']")))
                send_button.click()
                close_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Dismiss']")))
                close_button.click()

                i += 1
                if i >= max_connect:
                    print(f"Reached the maximum number of connection requests: {i}")
                    return

                time.sleep(randint(4, 15))
            page_number += 1
        except TimeoutException as e:
            print("A timeout occurred while waiting for the page or elements.")
        except NoSuchElementException as e:
            print("An element could not be found on the page.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

def chose_withdraw(driver):
    print('Withdrawing all current connection requests!\nPlease be aware that there is an intentional delay to avoid being detected as a bot.')
    page_number = 1
    total_withdrawn = 0
    max_withdraw_attempts = 400

    while total_withdrawn < max_withdraw_attempts:
        try:
            withdraw_url = "https://www.linkedin.com/mynetwork/invitation-manager/sent/"
            driver.get(withdraw_url)

            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//button/span/span[1]")))
            all_buttons = driver.find_elements(By.XPATH, "//button/span/span[1]")
            withdraw_buttons = [btn for btn in all_buttons if btn.text == "Withdraw"]

            if not withdraw_buttons:
                print("No 'Withdraw' buttons found, may have reached the end of invitations.")
                break

            for btn in withdraw_buttons:
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable(btn))
                btn.click()
                confirm_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@data-control-name='withdraw_single']")))
                confirm_button.click()

                total_withdrawn += 1
                print(f"Withdrawn {total_withdrawn} invitations so far.")

                time.sleep(randint(6, 20))
                if total_withdrawn >= max_withdraw_attempts:
                    print("Reached the maximum number of withdrawal attempts.")
                    break

            page_number += 1
        except TimeoutException as e:
            print("A timeout occurred while waiting for the page or elements.")
        except NoSuchElementException as e:
            print("An element could not be found on the page.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

def main():
    # Selection = int(input('(1) Send Connection Requests \n(2) Withdraw all pending connections\nWhich would you like to do: '))
    # LoginUser = input('\nEnter your LinkedIn email: ')
    # LoginPass = input('\nEnter your LinkedIn Password: ')

    Selection = 1
    LoginUser = os.environ['LOGIN_USER']
    LoginPass = os.environ['LOGIN_PASS']

    login_to_linkedin(driver, LoginUser, LoginPass)

    if Selection == 1:
        KeywordNum = int(input('How many keywords would you like to use: '))
        Keywords = [input(f'Enter Keyword {x+1}: ') for x in range(KeywordNum)]
        maxConnect = int(input('\nHow many connection requests would you like to send? (Stay below 50 to be safe): '))
        chose_connect(driver, Keywords, maxConnect)
    elif Selection == 2:
        chose_withdraw(driver)

    driver.quit()

if __name__ == "__main__":
    main()