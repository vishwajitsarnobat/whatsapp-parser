from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import os
from datetime import datetime

class PushMsg:
    def __init__(self, driver, messages: list):
        self.driver = driver
        self.messages = messages
        self.wait = WebDriverWait(self.driver, 10)
        self.search_box_xpath = '//div[@contenteditable="true"][@data-tab="3"]' 
        self.my_chat_name = "Vishwajit Sarnobat" 
        self.sent_jobs_file = "sent_jobs.json"

    def format_message(self, job_dict):
        return (
            f"*Role:* {job_dict.get('role_title', 'N/A')}\n"
            f"*Remote:* {'Yes' if job_dict.get('is_remote') else 'No'}\n"
            f"*Paid:* {'Yes' if job_dict.get('is_paid') else 'No'}\n"
            f"*Link:* {', '.join(job_dict.get('links', []))}\n"
            f"*Why:* {job_dict.get('match_reason', 'Matches profile')}"
        )

    def save_to_json(self, sent_data):
        existing_data = []
        if os.path.exists(self.sent_jobs_file) and os.stat(self.sent_jobs_file).st_size > 0:
            try:
                with open(self.sent_jobs_file, 'r') as f:
                    existing_data = json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: {self.sent_jobs_file} was corrupt. Starting fresh.")
                existing_data = []

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for msg in sent_data:
            msg['sent_at'] = timestamp
            existing_data.append(msg)

        with open(self.sent_jobs_file, 'w') as f:
            json.dump(existing_data, f, indent=4)
        print(f"Saved {len(sent_data)} messages to {self.sent_jobs_file}")

    def push(self):
        if not self.messages:
            print("No messages to push.")
            return

        try:
            search_box = self.wait.until(EC.element_to_be_clickable((By.XPATH, self.search_box_xpath)))
            search_box.click()
            search_box.send_keys(Keys.CONTROL + "a")
            search_box.send_keys(Keys.BACKSPACE)
            time.sleep(1)

            print(f"Opening chat with {self.my_chat_name}...")
            search_box.send_keys(self.my_chat_name)
            time.sleep(2)

            chat_xpath = f'//span[@title="{self.my_chat_name}"]'
            try:
                target_chat = self.wait.until(EC.presence_of_element_located((By.XPATH, chat_xpath)))
                target_chat.click()
            except:
                print(f"Could not find chat '{self.my_chat_name}'. Stopping push.")
                return

            message_box_xpath = '//div[@contenteditable="true"][@data-tab="10"]'
            message_box = self.wait.until(EC.element_to_be_clickable((By.XPATH, message_box_xpath)))

            sent_batch = []
            for msg_data in self.messages:
                formatted_text = self.format_message(msg_data)
                
                try:
                    message_box.click()
                    lines = formatted_text.split('\n')
                    for i, line in enumerate(lines):
                        message_box.send_keys(line)
                        if i < len(lines) - 1:
                            message_box.send_keys(Keys.SHIFT, Keys.ENTER) #newline
                    
                    time.sleep(0.5)
                    message_box.send_keys(Keys.ENTER) #send
                    time.sleep(1)
                    
                    sent_batch.append(msg_data)
                    print(f"Sent job: {msg_data.get('role_title')}")
                    
                except Exception as e:
                    print(f"Failed to send a message: {e}")
                    message_box = self.driver.find_element(By.XPATH, message_box_xpath)

            self.save_to_json(sent_batch)

        except Exception as e:
            print(f"PushMsg Error: {e}")