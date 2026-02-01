from setup import SeleniumSession
from process_chat import ProcessChat
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

home_path = "/home/vishwajitsarnobat"
original_profile_name = "Default"
chat_names = ["Hiring Alert(2nd Batch)", "Job / Intern Openings", "Batch(27/28/29) hiring"]

session = SeleniumSession(home_path, original_profile_name)
driver = session.start()
driver.get("https://web.whatsapp.com")

# using search box to check if whatsapp loaded
print("Waiting for WhatsApp to load (Please scan QR code if needed)...")
wait = WebDriverWait(driver, 60) #login only
try:
    search_box_xpath = '//div[@contenteditable="true"][@aria-label="Search input textbox"]' # or try [@data-tab="3"]
    wait.until(EC.presence_of_element_located((By.XPATH, search_box_xpath)))
    print("WhatsApp loaded successfully.")
except:
    print("Timed out waiting for WhatsApp to load.")
    session.stop()
    exit()

for chat_name in chat_names:  
    chat = ProcessChat(driver, chat_name)
    messages = chat.process_chat()
    print(messages)

# just to clean UI
try:
    search_box = driver.find_element(By.XPATH, search_box_xpath)
    search_box.send_keys(Keys.CONTROL + "a")
    search_box.send_keys(Keys.BACKSPACE)
except:
    pass

input("Press enter to end the session.")
session.stop()