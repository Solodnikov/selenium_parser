import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from fake_useragent import UserAgent
from functions import (authorization_hh, # noqa
                       from_main_to_my_resumes,
                       from_my_resumes_to_recomended_vacations,
                       get_pages_urls,
                       get_vacancy_urls_on_page,
                       get_vacancy_full_info,
                       vacancy_exist,
                       vacancy_old,
                       )
from db import session, create_obj_in_db, update_obj_in_db
from tqdm import tqdm
from constants import LOGIN_URL, WEB_DRIVER_PATH


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

# подключение веб драйвера
service = Service(
    executable_path=WEB_DRIVER_PATH
)

# brouser
driver = webdriver.Chrome(service=service,
                          options=options)

# start
try:
    authorization_hh(driver, LOGIN_URL, email, password)
    from_main_to_my_resumes(driver)
    from_my_resumes_to_recomended_vacations(driver)

    pages_urls = get_pages_urls(driver)
    for index, page_url in enumerate(pages_urls):
        print(f"Start collecting info from page {index}")
        # получаю список урл вакансий на странице
        urls_collection = get_vacancy_urls_on_page(page_url, driver)
        print(f"Creating vacancy objects from page {index}")
        for vacancy_url in tqdm(urls_collection):
            # если вакансия отсутствует в бд создаю запись
            if not vacancy_exist(session, vacancy_url):
                try:
                    data = get_vacancy_full_info(vacancy_url, driver)
                    create_obj_in_db(data, session)
                except Exception:
                    continue
            # если вакансия устаревшая, обновляю сведения по ней
            elif vacancy_old(session, vacancy_url):
                try:
                    data = get_vacancy_full_info(vacancy_url, driver)
                    update_obj_in_db(data, session)
                except Exception:
                    continue
        print(f"Finished creating vacancy objects from page {index}")

except Exception as ex:
    print(ex)
finally:
    driver.close()
    driver.quit()

# TODO предусмотреть варинт не открывать страницы, если имется такакя спарсенная вакансия. # noqa
# TODO предусмотреть тайминг для парсинга вакансии после прохождения 200 ходов.
# TODO проработать старт для куки
# TODO компанию работодателя добавить бы в базу данных?
