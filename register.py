import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from faker import Faker

# Initialize Faker for generating random names
fake = Faker()

# Base URL for API Key Registration
REGISTRATION_URL = "https://open.gsa.gov/api/regulationsgov/"

def find_shadow_element(driver, root_selector, element_selector):
    """Finds an element inside a Shadow DOM using JavaScript."""
    return driver.execute_script('''
        return document.querySelector(arguments[0]).shadowRoot.querySelector(arguments[1]);
    ''', root_selector, element_selector)

def fill_registration_form(email):
    """Launch browser, fill the form inside Shadow DOM, and submit automatically."""

    # Set up Chrome options (Non-Headless Mode)
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")  # Run in headless mode
    # chrome_options.add_argument("--start-maximized")  # Open browser in fullscreen

    # Initialize WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        print("Opening Regulations API Registration Page...")
        driver.get(REGISTRATION_URL)

        # Wait for page to load
        time.sleep(5)

        # Debug: Print Shadow DOM count
        shadow_roots = driver.execute_script('''
            return [...document.querySelectorAll("*")].filter(el => el.shadowRoot).map(el => el.shadowRoot);
        ''')
        print(f"Found {len(shadow_roots)} Shadow DOM elements.")

        # Find the shadow root element that contains the form
        shadow_root_selector = "div.api-umbrella-signup-embed-content-container"
        form_selector = "form"

        # Get the form inside the Shadow DOM
        form = find_shadow_element(driver, shadow_root_selector, form_selector)

        if not form:
            print("Could not find form inside Shadow DOM. Exiting.")
            return

        print("Found the form inside Shadow DOM!")

        # Generate random first and last name
        first_name = fake.first_name()
        last_name = fake.last_name()

        print(f"Using Name: {first_name} {last_name}")
        print(f"Using Email: {email}")

        # Fill in the form fields inside Shadow DOM
        driver.execute_script("arguments[0].querySelector('#user_first_name').value = arguments[1];", form, first_name)
        driver.execute_script("arguments[0].querySelector('#user_last_name').value = arguments[1];", form, last_name)
        driver.execute_script("arguments[0].querySelector('#user_email').value = arguments[1];", form, email)

        # Agree to Terms & Conditions inside Shadow DOM
        driver.execute_script("arguments[0].querySelector('#user_terms_and_conditions').click();", form)

        # Submit the form inside Shadow DOM
        driver.execute_script("arguments[0].querySelector('button[type=submit]').click();", form)

        print("Form submitted successfully!")

        # Wait to see if there's a confirmation message
        time.sleep(5)

    except Exception as e:
        print(f"Error: {e}")

    finally:
        driver.quit()
        print("Browser closed.")

# # Example Usage
# if __name__ == "__main__":
#     test_email = "ilenesalty235@mailpro.live"
#     fill_registration_form(test_email)
