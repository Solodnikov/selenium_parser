from selenium import webdriver
import time
from selenium.webdriver.chrome.service import Service
from fake_useragent import UserAgent
from selenium.webdriver.common.by import By
from functions import (authorization_hh,
                       check_driver,
                       from_main_to_my_resumes,
                       from_my_resumes_to_recomended_vacations,
                       get_pages_urls,
                       collecting_simple_info,
                       get_vacancy_info)


useragent = UserAgent()
email = 'alexander.solodnikov@gmail.com'
password = 'Karabas19!'

# options
options = webdriver.ChromeOptions()
options.add_argument('log-level=3')
options.add_argument(f'user-agent={useragent.chrome}')
# disable webdriver mode
options.add_argument('--disable-blink-features=AutomationControlled')
# headless mode
# options.add_argument('--headless')

# driver.get('https://www.whatismybrowser.com/detect/what-is-my-user-agent/',
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
    check_driver(driver)
    # start_time = time.time()
    authorization_hh(driver, url, email, password)
    from_main_to_my_resumes(driver)
    from_my_resumes_to_recomended_vacations(driver)

    pages_urls = get_pages_urls(driver)
    print(pages_urls)

    collection = collecting_simple_info(pages_urls, driver)
    result = get_vacancy_info(collection, driver)

except Exception as ex:
    print(ex)
finally:
    driver.close()
    driver.quit()
