import random


from selenium import webdriver
import time

from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait


def ask(question):

    # Initialize the webdriver
    # Set the path to ChromeDriver
    # Path to your Chrome user profile
  # Replace with your profile path


    # Initialize the Chrome driver with options\
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(chrome_options)
    driver.get("https://komo.ai")
    print("searching the web...")
    # Refresh the page to apply the cookie
    driver.refresh()    # Navigate to the website

    # Wait for the page to load
    driver.implicitly_wait(10)
    # Find the input field
    input_field = driver.find_element(By.XPATH, '//input[@type="text"]')
    time.sleep(1)

    # Send the question to the input field

    input_field.send_keys(question)

    # Press the return key
    input_field.send_keys(Keys.RETURN)

    # Wait for the response to generate
    # Find all elements with the specified attribute
    #response_elements = driver.find_elements(By.XPATH, '//div[@dir="auto"]')
    #time.sleep(10)
    wait = WebDriverWait(driver, 10)
    wait.until(lambda driver: len(driver.find_elements(By.XPATH, '//div[@dir="auto"]')) == 3)

    while True:
        # Get the old text
        try:
            response_elements = driver.find_elements(By.XPATH, '//div[@dir="auto"]')
            text = [element.text for element in response_elements]
        except:
            continue
        # Wait 1 second
        time.sleep(1)

        # Get the new text
        try:
            response_elements = driver.find_elements(By.XPATH, '//div[@dir="auto"]')
            textNew = [element.text for element in response_elements]
        except:
            continue
        if text == textNew and text is not None:
            break

    # Close the webdriver

    return text[2]
question = input("Ask a statement to fact check: ")
a = ask("Fact check the following statement: "+question)
print(a)