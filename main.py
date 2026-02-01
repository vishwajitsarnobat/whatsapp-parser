from setup import SeleniumSession
# from parser import BSParser
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys  # Needed for robust clearing
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

home_path = "/home/vishwajitsarnobat"
original_profile_name = "Default"

session = SeleniumSession(home_path, original_profile_name)
driver = session.start()
driver.get("https://web.whatsapp.com")

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

group_names = ["Hiring Alert(2nd Batch)", "Job / Intern Openings", "Batch(27/28/29) hiring"]

wait = WebDriverWait(driver, 10) #normal interactions

for group_name in group_names:    
    try:
        search_box = wait.until(EC.element_to_be_clickable((By.XPATH, search_box_xpath)))
        search_box.click()
        # robust clear
        search_box.send_keys(Keys.CONTROL + "a")
        search_box.send_keys(Keys.BACKSPACE)
        driver.implicitly_wait(1)
        
        print(f"Searching for {group_name}...")
        search_box.send_keys(group_name)
        driver.implicitly_wait(1)
        
        group_xpath = f'//span[@title="{group_name}"]'
        try:
            group_element = wait.until(EC.presence_of_element_located((By.XPATH, group_xpath)))
            group_element.click()
            print(f"Opened chat: {group_name}")     
        except:
            print(f"Warning: Group '{group_name}' not found in search results.")
            continue

        # print(f"Page Source type: {type(driver.page_source)}")
        # BSParser(driver.page_source)
            
    except Exception as e:
        print(f"An error occurred while processing {group_name}: {e}")
        continue

try:
    search_box = driver.find_element(By.XPATH, search_box_xpath)
    search_box.send_keys(Keys.CONTROL + "a")
    search_box.send_keys(Keys.BACKSPACE)
except:
    pass

input("Press enter to end the session.")
session.stop()