import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from fake_useragent import UserAgent
from functions import (authorization_hh, # noqa
                       check_driver,
                       from_main_to_my_resumes,
                       from_my_resumes_to_recomended_vacations,
                       get_pages_urls,
                       get_vacancy_info,
                       get_vacancy_number_from_url,
                       get_vacancy_urls_on_page,
                       get_vacancy_full_info,
                       vacancy_exist
                       )
from db import (session, create,
                create_obj_in_db)
from tqdm import tqdm


load_dotenv()

useragent = UserAgent()
email = os.getenv('EMAIL')
password = os.getenv('PASSWORD')

# options
options = webdriver.ChromeOptions()
options.add_argument('log-level=3')
options.add_argument(f'user-agent={useragent.chrome}')
# disable webdriver mode
options.add_argument('--disable-blink-features=AutomationControlled')
# headless mode
# options.add_argument('--headless')

# путь веб драйвера для пк
service = Service(
    executable_path=r'E:\DEV\PET_PROJECTS\selenium_parser\chromedriver\chromedriver.exe'  # noqa 
    )

# путь веб драйвера для ноута
# service = Service(
#     executable_path=r'C:\dev\PET_PROJECT\selenium_parser\chromedriver\chromedriver.exe'  # noqa
#     )

# url
url = 'https://hh.ru/account/login'

# brouser
driver = webdriver.Chrome(service=service,
                          options=options)


# start
try:
    # check_driver(driver)
    authorization_hh(driver, url, email, password)
    from_main_to_my_resumes(driver)
    from_my_resumes_to_recomended_vacations(driver)

    pages_urls = get_pages_urls(driver)
    for index, page_url in enumerate(pages_urls):
        print(f"Start collecting info from page {index}")
        urls_collection = get_vacancy_urls_on_page(page_url, driver)
        print(f"Creating vacancy objects from page {index}")
        for vacancy_url in tqdm(urls_collection):
            if not vacancy_exist(session, vacancy_url):
                try:
                    data = get_vacancy_full_info(vacancy_url, driver)
                    create_obj_in_db(data, session)
                except Exception:
                    continue
        print(f"Finished creating vacancy objects from page {index}")
    # print(pages_urls)
    
    # базовый сбор сведений о вакансиях
    # collection = collecting_simple_info(pages_urls, driver)
    # тестовый вариант работы
    # collection = collecting_test_info(pages_urls, driver)
    # обновленный сбор сведений о вакансиях
    # collection = get_vacancy_base_info(pages_urls, driver)
    
    # вынесен цикл операций в майн
    # print('Vacancy detail collecting...')
    # for vacancy_data in tqdm(collection):
    #     data = get_vacancy_info_ver2(vacancy_data, driver)
        # create_obj_in_db(data, session)
        # create_objs_in_db(data, session)
    # TODO проверить и внести данные 
    # TODO настроить внесение результата в БД
    # result = get_vacancy_info(collection, driver)
    # create(result, session)

except Exception as ex:
    print(ex)
finally:
    driver.close()
    driver.quit()
# TODO предусмотреть варинт не открывать страницы, если имется такакя спарсенная вакансия.
# TODO предусмотреть тайминг для парсинга вакансии после прохождения 200 ходов.
