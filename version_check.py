from selenium import webdriver

driver = webdriver.Chrome()
caps = driver.capabilities
browserVersion = caps["browserVersion"]
driverVersion = caps["chrome"]["chromedriverVersion"]
print(f"Chrome Browser Version: {browserVersion}")
print(f"Chrome Driver Version: {driverVersion}")

size = len(browserVersion)
if (browserVersion == driverVersion[:size]):
    print("The versions match...")
else:
    print("The version conflict found...")

driver.quit()
