from setup import SeleniumSession
from process_chat import ProcessChat
from process_llm import ProcessLLM
from push_msgs import PushMsg
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

home_path = "/home/vishwajitsarnobat"
original_profile_name = "Default"
chat_names = ["Hiring Alert(2nd Batch)", "Job / Intern Openings", "Batch(27/28/29) hiring"]
search_box_xpath = '//div[@contenteditable="true"][@data-tab="3"]' # or try [@aria-label="Search input textbox"]

session = SeleniumSession(home_path, original_profile_name)
driver = session.start()
driver.get("https://web.whatsapp.com")

# using search box to check if whatsapp loaded
print("Waiting for WhatsApp to load (Please scan QR code if needed)...")
wait = WebDriverWait(driver, 60) #login only
try:
    wait.until(EC.presence_of_element_located((By.XPATH, search_box_xpath)))
    print("WhatsApp loaded successfully.")
except:
    print("Timed out waiting for WhatsApp to load. Check your internet connection.")
    session.stop()
    exit()

for chat_name in chat_names:
    print('\n')
    chat = ProcessChat(driver, chat_name)
    messages = chat.process_chat()
    print(f"Received a total of {len(messages)} new messages.")
    # for msg in messages:
    #     print(msg)

    # messages will have unique new messages
    for msg in messages:
        llm = ProcessLLM(driver, msg)
        response = llm.process()
        if response == "Not relevant":
            print("Message was not relevant, hence not sent.")
        else:
            push_msgs = PushMsg(driver, response)
            push_msgs.push()

# just to clean UI
try:
    search_box = driver.find_element(By.XPATH, search_box_xpath)
    search_box.send_keys(Keys.CONTROL + "a")
    search_box.send_keys(Keys.BACKSPACE)
except:
    pass

input("Press enter to end the session.")
session.stop()