import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from random import randint
import time

# Initialize the Chrome driver with appropriate options for visible mode
def init_driver():
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')

    #chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("disable-infobars")
    driver = webdriver.Chrome(options=chrome_options)
    print(f"Driver initialized with options: {chrome_options.arguments}")
    return driver

# Function to log in to LinkedIn using Selenium
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

# Function to send connection requests on LinkedIn
def send_connection_requests(driver, keywords, max_connect):
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

# Streamlit application setup and logic
def main():
    st.set_page_config(page_title="LinkedIn Automation Tool", layout="wide")
    st.sidebar.header('User Settings')
    username = st.sidebar.text_input("LinkedIn Username")
    password = st.sidebar.text_input("LinkedIn Password", type="password")

    st.title('LinkedIn Automation Tool')
    st.write('Streamline your LinkedIn interactions with AI-driven automation.')

    keywords_input = st.text_input('Enter keywords separated by commas')
    max_connections = st.number_input('Number of connection requests', min_value=1, max_value=100, value=10)
    send_requests = st.button('Send Connection Requests')

    if send_requests and username and password and keywords_input:
        with st.spinner("Processing..."):
            driver = init_driver()
            login_to_linkedin(driver, username, password)
            keywords_list = [keyword.strip() for keyword in keywords_input.split(',')]
            send_connection_requests(driver, keywords_list, max_connections)
            driver.quit()
            st.success("Connection requests sent successfully!")
    elif send_requests:
        st.error("Please fill out all fields.")

if __name__ == "__main__":
    main()