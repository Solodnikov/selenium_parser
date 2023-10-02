from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from fake_useragent import UserAgent
from functions import (authorization_hh, # noqa
                       check_driver,
                       from_main_to_my_resumes,
                       from_my_resumes_to_recomended_vacations,
                       get_pages_urls,
                       collecting_simple_info,
                       get_vacancy_info,
                       collecting_test_info)


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
    executable_path=r'E:\DEV\PET_PROJECTS\selenium_parser\chromedriver\chromedriver.exe'  # noqa
    )

# url
url = 'https://hh.ru/account/login'

# brouser
driver = webdriver.Chrome(service=service,
                          options=options)


# start
try:
    check_driver(driver)
    authorization_hh(driver, url, email, password)
    from_main_to_my_resumes(driver)
    from_my_resumes_to_recomended_vacations(driver)

    pages_urls = get_pages_urls(driver)
    # print(pages_urls)

    # collection = collecting_simple_info(pages_urls, driver)
    collection = collecting_test_info(pages_urls, driver)
    result = get_vacancy_info(collection, driver)
    print()

except Exception as ex:
    print(ex)
finally:
    driver.close()
    driver.quit()
