from selenium import webdriver
import time
from selenium.webdriver.chrome.service import Service
from fake_useragent import UserAgent
from selenium.webdriver.common.by import By

useragent = UserAgent()
email = 'alexander.solodnikov@gmail.com'
password = 'Karabas19!'

# options
options = webdriver.ChromeOptions()
options.add_argument('log-level=3')
options.add_argument(f'user-agent={useragent.chrome}')

# driver_path
service = Service(
    executable_path=r'E:\DEV\PET_PROJECTS\selenium_parser\chromedriver\chromedriver.exe'
    )

# url
url = 'https://hh.ru/account/login'

# brouser
driver = webdriver.Chrome(service=service,
                          options=options)

# start
try:
    # driver.get('https://www.whatismybrowser.com/detect/what-is-my-user-agent/',
    driver.get(url=url)

    # input_email
    input_email = driver.find_element(By.XPATH, "/html/body/div[5]/div/div[3]/div[1]/div/div/div/div/div/div[1]/div[1]/div/div[2]/form/fieldset/input")
    input_email.clear()
    input_email.send_keys(email)
    time.sleep(1)

    # open_password
    password_button = driver.find_element(By.XPATH, "/html/body/div[5]/div/div[3]/div[1]/div/div/div/div/div/div[1]/div[1]/div/div[2]/form/div[4]/button[2]")
    password_button.click()
    time.sleep(1)

    # input_password
    input_password = driver.find_element(By.XPATH, "/html/body/div[5]/div/div[3]/div[1]/div/div/div/div/div/div[1]/div[1]/div/form/div[2]/fieldset/input")
    input_password.clear()
    input_password.send_keys(password)
    time.sleep(2)

    # enter
    enter_button = driver.find_element(By.XPATH, "/html/body/div[5]/div/div[3]/div[1]/div/div/div/div/div/div[1]/div[1]/div/form/div[6]/button[1]")
    enter_button.click()
    time.sleep(10)

except Exception as ex:
    print(ex)
finally:
    driver.close()
    driver.quit()
