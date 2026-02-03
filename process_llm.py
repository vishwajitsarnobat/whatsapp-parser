from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from google import genai
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests
import json
import time
import os

class ProcessLLM:
    def __init__(self, driver, message: dict):
        self.driver = driver
        self.message = message
        self.message_text = message.get("text", "")
        self.links = message.get("links", [])
        self.prompts = {}

        try:
            with open("prompts.json", 'r') as f:
                self.prompts = json.load(f)
        except Exception as e:
            print(f"Failed to load prompts.json: {e}")
            return

        self.relevance_prompt = self.prompts.get("relevance_prompt", "")
        self.process_prompt = self.prompts.get("process_prompt", "")

        try:
            load_dotenv()
            self.api_key = os.getenv("api_key")
        except Exception as e:
            print(f"Failed to load API key: {e}")
        
        self.client = genai.Client(api_key=self.api_key)
        self.model = "gemini-2.5-flash"

    def scrape_link(self, url):
        print(f"Scraping link: {url}")
        original_window = self.driver.current_window_handle
        clean_text = ""

        try:
            # headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36'} #my actual header
            # response = requests.get(url, headers=headers, timeout=10)
            self.driver.switch_to.new_window('tab')
            self.driver.get(url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            for script in soup(["script", "style"]): # remove script/style elements
                script.extract()
            
            text = soup.get_text(separator=' ')
            lines = (line.strip() for line in text.splitlines())
            clean_text = ' '.join(chunk for chunk in lines if chunk)

            print(f"Text length: {len(clean_text)}")
            
        except Exception as e:
            print(f"Failed to scrape {url}: {e}")

        finally:
            if len(self.driver.window_handles) > 1:
                self.driver.close()
            self.driver.switch_to.window(original_window)
            print("Returned to original Whatsapp tab.")
        return clean_text

    def process(self):
        full_context = f"WHATSAPP MESSAGE:\n{self.message_text}\n\n"
        
        if self.links:
            print(f"Found {len(self.links)} links. Scraping content...")
            for link in self.links:
                scraped_content = self.scrape_link(link)
                if scraped_content:
                    full_context += f"SCRAPED CONTENT FROM {link}:\n{scraped_content}\n\n"

        job_extraction_schema = {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'links': {'type': 'array', 'items': {'type': 'string'}},
                    'role_title': {'type': 'string'},
                    'is_remote': {'type': 'boolean'},
                    'is_paid': {'type': 'boolean'},
                    'match_reason': {'type': 'string'}
                },
                'required': ['links', 'role_title', 'is_remote', 'is_paid', 'match_reason']
            }
        }

        try:
            # Free tier is approx 15 Requests Per Minute (1 req every 4 seconds)
            time.sleep(4) 
            
            final_prompt = self.process_prompt.format(message_content=full_context)
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=final_prompt,
                config={
                    'response_mime_type': 'application/json',
                    'response_schema': job_extraction_schema
                }
            )
            
            return json.loads(response.text)
            
        except Exception as e:
            if "429" in str(e):
                print("Rate Limit Hit! Sleeping for 60 seconds...")
                time.sleep(60)
                return self.process()
            print(f"Error processing details: {e}")
            return []