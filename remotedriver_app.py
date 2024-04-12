import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import numpy as np
import time
import logging
from datetime import datetime
import os

# Ensure directories for logs and screenshots
log_directory = "logs"
screenshots_directory = "screenshots"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)
if not os.path.exists(screenshots_directory):
    os.makedirs(screenshots_directory)

# Logging configuration
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
filename = f"{log_directory}/log_{timestamp}.log"
logging.basicConfig(filename=filename, level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s', filemode='w')
logger = logging.getLogger(__name__)

def human_like_delay():
    mean_time = 10
    std_dev = 3
    sleep_time = abs(np.random.normal(mean_time, std_dev))
    logger.info(f"Delay introduced for {sleep_time:.2f} seconds to mimic human behavior.")
    time.sleep(sleep_time)

def init_driver():
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("disable-infobars")
    selenium_grid_url = "http://66.228.58.4:4444/wd/hub"
    driver = webdriver.Remote(command_executor=selenium_grid_url, options=chrome_options)
    logger.info("WebDriver initialized.")
    return driver

def login_to_linkedin(driver, username, password):
    logger = logging.getLogger(__name__)
    logger.info(f"Logging in to LinkedIn as {username}")
    url_to_sign_in_page = 'https://www.linkedin.com/login'

    time.sleep(15)
    driver.get_screenshot_as_file(f'{screenshots_directory}/login_page.png')
    driver.get(url_to_sign_in_page)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'session_key')))

    username_input = driver.find_element(By.NAME, 'session_key')
    password_input = driver.find_element(By.NAME, 'session_password')
    username_input.send_keys(username)
    password_input.send_keys(password)

    time.sleep(5)

    driver.get_screenshot_as_file(f'{screenshots_directory}/login_page_with_creds.png')
    try:
        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
        submit_button.click()
    except TimeoutException:
        logger.error("Timeout while trying to log in.")
    except NoSuchElementException:
        logger.error("Submit button was not clickable.")

    WebDriverWait(driver, 10).until(lambda d: d.current_url != url_to_sign_in_page)
    logger.info("Successfully signed in!")
    time.sleep(15)
    driver.get_screenshot_as_file(f'{screenshots_directory}/after_successful_login.png')


def send_connection_requests(driver, keywords, max_connect):
    i, page_number = 0, 1
    while i < max_connect:
        try:
            keyword_query = "%20".join(keywords)
            url_link = f"https://www.linkedin.com/search/results/people/?keywords={keyword_query}&page={page_number}"
            driver.get(url_link)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "button")))
            connect_buttons = [btn for btn in driver.find_elements(By.TAG_NAME, "button") if btn.text == "Connect"]

            if not connect_buttons:
                logger.info(f"No connect buttons found on page {page_number}. Moving to next page.")
                page_number += 1
                continue

            for btn in connect_buttons:
                btn.click()
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']//strong")))
                send_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Send now']")))
                send_button.click()
                close_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Dismiss']")))
                close_button.click()

                i += 1
                if i >= max_connect:
                    return
                human_like_delay()
            page_number += 1
        except TimeoutException as e:
            logger.error(f"Timeout error on page {page_number}: {e}")
        except NoSuchElementException as e:
            logger.error(f"Element not found error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            break

def main():
    st.set_page_config(page_title="LinkedIn Automation Tool", layout="wide")
    st.sidebar.header('User Settings')
    username = st.sidebar.text_input("LinkedIn Username")
    password = st.sidebar.text_input("LinkedIn Password", type="password")

    st.title('LinkedIn Automation Tool')
    st.write('Automate your LinkedIn interactions.')

    keywords_input = st.text_input('Enter keywords separated by commas')
    max_connections = st.number_input('Number of connection requests', min_value=1, max_value=100, value=10)
    send_requests = st.button('Send Connection Requests')

    if send_requests and username and password and keywords_input:
        with st.spinner("Processing..."):
            driver = init_driver()
            try:
                if login_to_linkedin(driver, username, password):
                    keywords_list = [keyword.strip() for keyword in keywords_input.split(',')]
                    send_connection_requests(driver, keywords_list, max_connections)
                    st.success("Connection requests sent successfully!")
                else:
                    st.error("Failed to log in to LinkedIn. Please check your credentials.")
            finally:
                driver.quit()
    elif send_requests:
        st.error("Please fill out all fields.")

if __name__ == "__main__":
    main()