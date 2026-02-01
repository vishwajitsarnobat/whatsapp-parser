from bs4 import BeautifulSoup
import re

class BSParser:
    # incoming will always be processed, option to skip outgoing
    def __init__(self, page_source: str, outgoing=True):
        self.page_source = page_source
        self.outgoing = outgoing
        self.soup = BeautifulSoup(page_source, "html.parser")
        self.extracted_messages = []

    def parse_messages(self):
        if self.outgoing:
            incoming_bubbles = self.soup.select('div.message-in', 'div.message-out')
        else:
            incoming_bubbles = self.soup.select('div.message-in') # alternative: find_all

        for bubble in incoming_bubbles:
            message_data = {
                "time": None,
                "sender": None,
                "text": None,
                "links": []
            }
            
            # time, sender AND message in different containers
            time_sender_element = bubble.select_one('div[data-pre-plain-text]')
            if time_sender_element:
                time_sender = time_sender_element['data-pre-plain-text']
                pattern_match = re.search(r"\[(.*?)\]\s(.*?):", time_sender)
                message_data["time"] = pattern_match.group(1)
                message_data["sender"] = pattern_match.group(2)
            else:
                print("Time and pattern matching failed.")
            
            text_element = bubble.select_one('span[data-testid="selectable-text"]')
            if text_element:
                message_data["text"] = text_element.get_text()
                link_elements = text_element.find_all('a')
                for link_element in link_elements:
                    link = link_element.get("href")
                    if link:
                        message_data["links"].append(link)
                    else:
                        print("No link found in this message.")
            else:
                print("No text found in this message.")

            if message_data['text']:
                self.extracted_messages.append(message_data)
        
        return self.extracted_messages