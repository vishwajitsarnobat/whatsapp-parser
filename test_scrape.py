from setup import SeleniumSession
from bs4 import BeautifulSoup
import requests

url = "https://www.linkedin.com/posts/jhalaktiwarii_hello-everyone-we-are-looking-for-full-activity-7418604665195421696-jSN6?utm_source=social_share_send&utm_medium=android_app&rcm=ACoAADycfrABRlBqNYJY_zajd60RnmIXFeTtNDE&utm_campaign=whatsapp"
home_path = "/home/vishwajitsarnobat"
original_profile_name = "Default"
session = SeleniumSession(home_path, original_profile_name)
driver = session.start()
driver.get(url)
soup = BeautifulSoup(driver.page_source, "html.parser")
for script in soup(["script", "style"]):
    soup.extract(script)
raw_text = soup.get_text(separator=' ')
lines = (line.strip() for line in raw_text.splitlines())
clean_text = ' '.join(line for line in lines if line)
print(clean_text)