import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, NoSuchElementException
from random import randint
import time
import logging
import numpy as np
import os
from datetime import datetime

# Create a directory for logs if it doesn't exist
log_directory = "logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# Generate a filename with the current date and time
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
filename = f"{log_directory}/log_{timestamp}.log"

# Set up logging configuration to write to a file
logging.basicConfig(
    filename=filename,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='w'  # 'w' for write mode
)

def human_like_delay():
    mean_time = 10
    std_dev = 3
    sleep_time = abs(np.random.normal(mean_time, std_dev))
    logging.debug(f"Sleeping for {sleep_time:.2f} seconds to mimic human interaction.")
    time.sleep(sleep_time)

def init_driver():
    logging.info("Initializing the Selenium driver.")
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("disable-infobars")

    selenium_grid_url = "http://66.228.58.4:4444/wd/hub"
    driver = webdriver.Remote(command_executor=selenium_grid_url, options=chrome_options)
    logging.info("Driver initialized successfully.")
    return driver

def login_to_linkedin(driver, username, password):
    attempts = 0
    max_attempts = 3
    while attempts < max_attempts:
        try:
            driver.get('https://www.linkedin.com/login')
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'session_key')))
            driver.find_element(By.NAME, 'session_key').send_keys(username)
            driver.find_element(By.NAME, 'session_password').send_keys(password)
            submit_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
            submit_button.click()
            WebDriverWait(driver, 10).until(lambda d: d.current_url != 'https://www.linkedin.com/login')
            logging.info("Successfully signed in.")
            return
        except TimeoutException:
            logging.warning(f"Login attempt {attempts + 1} failed, retrying...")
            attempts += 1
        except Exception as e:
            logging.error(f"Failed to sign in after maximum attempts. Error: {e}")

def send_connection_requests(driver, keywords, max_connect):
    logging.info("Starting the connection request process.")
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
                logging.warning(f"No 'Connect' buttons found on page {page_number}. Moving to next page.")
                page_number += 1
                continue

            for btn in connect_buttons:
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable(btn))
                btn.click()
                name = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']//strong")))
                logging.info(f"Sending connection request to {name.text}")

                send_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Send now']")))
                send_button.click()
                close_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Dismiss']")))
                close_button.click()

                i += 1
                if i >= max_connect:
                    logging.info(f"Reached the maximum number of connection requests: {i}")
                    return

                human_like_delay()
                page_number += 1
                except TimeoutException as e:
                logging.error(f"A timeout occurred while waiting for the page or elements. Error: {e}")
                except NoSuchElementException as e:
                logging.error(f"An element could not be found on the page. Error: {e}")
                except Exception as e:
                logging.error(f"An unexpected error occurred: {e}. Current URL: {driver.current_url}, Page Number: {page_number}")

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