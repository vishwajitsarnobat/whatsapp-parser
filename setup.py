import shutil
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from typing import Optional

class SeleniumSession:
    def __init__(self, home_path: Optional[str] = None, profile_name: str = "Default"):
        if home_path is None:
            self.home_path = os.path.expanduser("~")
        else:
            self.home_path = home_path
            
        self.original_profile_name = profile_name
        self.chrome_data_path = os.path.join(self.home_path, ".config/google-chrome")
        self.copy_data_path = os.path.join(self.home_path, "selenium")
        self.original_profile_path = os.path.join(self.chrome_data_path, self.original_profile_name)
        self.temp_profile_name = f"temp_{self.original_profile_name}"
        self.copy_profile_path = os.path.join(self.copy_data_path, self.temp_profile_name)
        
        self.driver = None

    def start(self):
        """Manually starts the browser session."""
        print("Initializing session...")
        if os.path.exists(self.copy_data_path):
            shutil.rmtree(self.copy_data_path)
        
        os.makedirs(self.copy_data_path, exist_ok=True)
        print(f"Cloning profile from {self.original_profile_path}...")
        shutil.copytree(self.original_profile_path, self.copy_profile_path)

        options = Options()
        options.add_argument(f"--user-data-dir={self.copy_data_path}")
        options.add_argument(f"--profile-directory={self.temp_profile_name}")
        options.add_argument("--disable-extensions")
        
        self.driver = webdriver.Chrome(options=options)
        return self.driver

    def stop(self):
        """Manually closes the browser and cleans up files."""
        print("Stopping session...")
        if self.driver:
            self.driver.quit()
        
        if os.path.exists(self.copy_data_path):
            print("Cleaning up temporary files...")
            shutil.rmtree(self.copy_data_path)
            print("Cleanup complete.")
        else:
            print("Cleanup skipped (files already removed).")