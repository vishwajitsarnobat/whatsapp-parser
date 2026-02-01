from parser import BSParser
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import hashlib
import os
import json
import sys
from pathlib import Path
from datetime import datetime

class ProcessChat:
    def __init__(self, driver, chat_name: str):
        self.driver = driver
        self.chat_name = chat_name
        self.wait = WebDriverWait(self.driver, 10)
        self.search_box_xpath = '//div[@contenteditable="true"][@data-tab="3"]' # or try [@aria-label="Search input textbox"]
        self.safe_name = "".join(c for c in self.chat_name if c.isalnum() or c in ('_')).strip()
        print("Safe name: ", self.safe_name)
        
        # create files if doesn't exist, using path for OS safety
        BASE_DIR = Path(__file__).resolve().parent
        base_path = BASE_DIR / "chats" / self.safe_name
        base_path.mkdir(parents=True, exist_ok=True)
        self.state_file = base_path / f"state_{self.safe_name}.json"
        self.history_file = base_path / f"history_{self.safe_name}.csv"
        self.hash_file = base_path / f"hashes_{self.safe_name}.txt"
        for file in (self.state_file, self.history_file, self.hash_file):
            file.touch(exist_ok=True)

        self.last_msg_time = self.load_last_msg_time()
        self.seen_hashes = self.load_hashes()
        
        self.curr_min_time = sys.maxsize
        self.curr_max_time = 0

        self.messages = []

    def load_last_msg_time(self):
        try:
            with open(self.state_file, 'r') as f:
                time_str = json.load(f)
                if not time_str:
                    return 0
                return self.string_to_epoch(time_str)
        except Exception as e:
            print(e)
            return 0
    
    def load_hashes(self):
        hashes = set()
        with open(self.hash_file, 'r') as f:
            for line in f:
                hashes.add(line.strip())
        return hashes

    # this is only where we will be dealing with whatsapp time format [4:20 pm, 01/02/2026]
    def update_min_max_times(self, msg_time: str):
        try:
            clean_str = msg_time.replace("[", "").replace("]", "").strip()
            dt_object = datetime.strptime(clean_str.upper(), "%I:%M %p, %d/%m/%Y")
            timestamp = int(dt_object.timestamp())
            
            if timestamp < self.curr_min_time:
                self.curr_min_time = timestamp
            if timestamp > self.curr_max_time:
                self.curr_max_time = timestamp
        # the whatsapp format is not perfect, hence the precaution
        except ValueError:
            print(f"Skipping invalid timestamp format: {msg_time}")

    def add_hash_to_file(self, msg_hash: str):
        with open(self.hash_file, 'a') as f:
            f.write(msg_hash + "\n")

    def MD5Hash(self, time: str, text: str):
        unique_string = f"{time}|{text}"
        return hashlib.md5(unique_string.encode('utf8')).hexdigest()

    def epoch_to_string(self, epoch_integer: int):
        dt_object = datetime.fromtimestamp(epoch_integer)
        return dt_object.strftime("%Y-%m-%d %H:%M:%S")

    def string_to_epoch(self, date_string):
        fmt = "%Y-%m-%d %H:%M:%S"
        dt_object = datetime.strptime(date_string, fmt)
        return int(dt_object.timestamp())

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
            
            while self.curr_min_time is None or self.last_msg_time <= self.curr_min_time:
                bsparser = BSParser(self.driver.page_source, outgoing=False)
                bsparser_messages = bsparser.parse_messages()
                
                msg_count = 0
                for msg in bsparser_messages:
                    msg_hash = self.MD5Hash(msg["time"], msg["text"])
                    if msg_hash not in self.seen_hashes:
                        msg_count += 1
                        self.messages.append(msg)
                        self.seen_hashes.add(msg_hash)
                        self.add_hash_to_file(msg_hash) # updating hashes in file
                        self.update_min_max_times(msg["time"])
                
                if msg_count == 0:
                    break

                try:
                    scroll_xpath = '//div[@data-scrolltracepolicy="wa.web.conversation.messages"]'
                    scroll_element = self.wait.until(EC.element_to_be_clickable((By.XPATH, scroll_xpath)))
                    scroll_element.click()
                    scroll_element.send_keys(Keys.PAGE_UP)
                    time.sleep(2)
                except Exception as e:
                    print(e)
                    print("Scrolling failed.")

        except Exception as e:
            print(f"An error occurred while processing {self.chat_name}: {e}")

        self.save_state()

        return self.messages
    
    # updating last max time and log
    def save_state(self):
        if self.curr_max_time != 0:
            with open(self.state_file, 'w') as f:
                json.dump(self.epoch_to_string(self.curr_max_time), f)
        
        if self.curr_min_time != sys.maxsize:
            with open(self.history_file, 'a') as f:
                f.write(f"{datetime.now()},{self.epoch_to_string(self.curr_min_time)},{self.epoch_to_string(self.curr_max_time)}\n")