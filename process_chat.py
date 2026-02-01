from parser import BSParser
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class ProcessChat:
    def __init__(self, driver, chat_name: str):
        self.driver = driver
        self.chat_name = chat_name
        self.wait = WebDriverWait(self.driver, 10)
        self.search_box_xpath = '//div[@contenteditable="true"][@aria-label="Search input textbox"]' # or try [@data-tab="3"]

    def process_chat(self):
        try:
            search_box = self.wait.until(EC.element_to_be_clickable((By.XPATH, self.search_box_xpath)))
            search_box.click()
            # more robust than clear
            search_box.send_keys(Keys.CONTROL + "a")
            search_box.send_keys(Keys.BACKSPACE)
            time.sleep(1)
            
            print(f"Searching for {self.chat_name}...")
            search_box.send_keys(self.chat_name)
            time.sleep(1)

            chat_xpath = f'//span[@title="{self.chat_name}"]'
            try:
                chat_element = self.wait.until(EC.presence_of_element_located((By.XPATH, chat_xpath)))
                chat_element.click()
                print(f"Opened chat: {self.chat_name}")     
            except:
                print(f"Warning: chat '{self.chat_name}' not found in search results.")
                return None
            time.sleep(2) 
            # scrolling will be implemented here
            bsparser = BSParser(self.driver.page_source, outgoing=False)
            messages = bsparser.parse_messages()
            return messages

        except Exception as e:
            print(f"An error occurred while processing {self.chat_name}: {e}")
            return None