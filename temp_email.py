import requests
import random
import string
import time
import re

# Base URL for Mail.tm API
MAIL_TM_BASE_URL = "https://api.mail.tm"

# # Example Usage
# if __name__ == "__main__":
#     temp_email = TempEmail()
#     api_key = temp_email.fetch_api_key()

#     if api_key:
#         print(f"Successfully retrieved API key: {api_key}")
#     else:
#         print("API key retrieval failed.")

class TempEmail:
    """Class to handle temporary email creation, authentication, and message retrieval."""

    def __init__(self, password="securepassword"):
        self.domain = self.get_valid_domain()
        self.password = password
        self.email_address = self.generate_random_email()
        self.token = None
        self.account_id = None

        if self.domain:
            self.create_account()
            self.authenticate()

    def get_valid_domain(self):
        """Fetches a valid domain for creating an account."""
        response = requests.get(f"{MAIL_TM_BASE_URL}/domains")
        if response.status_code == 200:
            domains = response.json().get("hydra:member", [])
            if domains:
                return domains[0]["domain"]
        print("No valid domains available.")
        return None

    def generate_random_email(self):
        """Generates a random email address using the fetched domain."""
        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        return f"{username}@{self.domain}" if self.domain else None

    def create_account(self):
        """Creates a temporary email account."""
        url = f"{MAIL_TM_BASE_URL}/accounts"
        payload = {"address": self.email_address, "password": self.password}

        response = requests.post(url, json=payload)
        if response.status_code == 201:
            self.account_id = response.json()["id"]
            print(f"Account successfully created: {self.email_address}")
        else:
            print(f"Failed to create account ({self.email_address}):", response.text)

    def authenticate(self):
        """Retrieves an authentication token for the created account."""
        url = f"{MAIL_TM_BASE_URL}/token"
        payload = {"address": self.email_address, "password": self.password}

        response = requests.post(url, json=payload)
        if response.status_code == 200:
            self.token = response.json()["token"]
            print("Authentication successful!")
        else:
            print("Failed to get authentication token:", response.text)

    def get_messages(self):
        """Fetches messages from the inbox."""
        if not self.token:
            print("No authentication token found.")
            return None

        url = f"{MAIL_TM_BASE_URL}/messages"
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json().get("hydra:member", [])
        print("Failed to retrieve messages:", response.text)
        return None

    def get_full_message(self, message_id):
        """Retrieves the full message details by message ID."""
        if not self.token:
            print("No authentication token found.")
            return None

        url = f"{MAIL_TM_BASE_URL}/messages/{message_id}"
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        print(f"Failed to retrieve full message ({message_id}):", response.text)
        return None

    def extract_api_key(self, message_text):
        """Extracts the API key from the email message."""
        pattern = rf"Your API key for {re.escape(self.email_address)} is:\s*([\w\d]+)"
        match = re.search(pattern, message_text)
        return match.group(1) if match else None

    def fetch_api_key(self):
        """Checks for incoming messages and extracts the API key."""
        print("Checking for messages...")
        for _ in range(30):  # Wait up to 60 seconds
            messages = self.get_messages()
            if messages:
                print(f"{len(messages)} message(s) received!")
                for msg in messages:
                    full_msg = self.get_full_message(msg['id'])
                    if full_msg:
                        # print("\n **Full Message Details**")
                        # print(f"Subject: {full_msg['subject']}")
                        # print(f"From: {full_msg['from']['address']}")
                        # print(f"To: {[recipient['address'] for recipient in full_msg['to']]}")
                        # print(f"Date: {full_msg['createdAt']}")
                        # print("\n**Message Content:**\n")
                        # print(full_msg.get('text', 'No text content available'))
                        # print("\n--- End of Message ---\n")

                        api_key = self.extract_api_key(full_msg.get('text', ''))
                        if api_key:
                            print(f"Extracted API Key: {api_key}")
                            return api_key
                        else:
                            print("API Key not found in email.")
                break
            time.sleep(2)
        print("No messages received.")
        return None