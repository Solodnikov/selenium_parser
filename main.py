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
                       )
from crud import (vacancy_exist,
                  create_obj_in_db,
                  vacancy_old,
                  update_obj_in_db,
                  del_old_vacancies
                  )
import time
from db import session
from tqdm import tqdm
from constants import (LOGIN_URL,
                       WEB_DRIVER_PATH,
                       PARSE_PAUSE,
                       MAX_PARSE)


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

    parse_counter = 0  # счетчик для паузы парсера
    pages_urls = get_pages_urls(driver)

    for index, page_url in enumerate(pages_urls):
        print(f"Start collecting info from page {index}")
        # получаю список урл вакансий на странице
        urls_collection = get_vacancy_urls_on_page(page_url, driver)
        print(f"Creating vacancy objects from page {index}")

        for vacancy_url in tqdm(urls_collection):
            # если не исчерпан счетчик
            if parse_counter < MAX_PARSE:
                # если вакансия отсутствует в бд создаю запись
                if not vacancy_exist(session, vacancy_url):
                    try:
                        data = get_vacancy_full_info(vacancy_url, driver)
                        parse_counter += 1
                        create_obj_in_db(data, session)
                    except Exception:
                        continue
                # если вакансия устаревшая, обновляю сведения по ней
                elif vacancy_old(session, vacancy_url):
                    try:
                        data = get_vacancy_full_info(vacancy_url, driver)
                        parse_counter += 1
                        update_obj_in_db(data, session)
                    # если ошибка в получении обновления,
                    # то перехожу к обработке следующей вакансии
                    except Exception:
                        continue
            # если исчерпан счетчик, обновляем счетчик, выдерживаем паузу
            else:
                parse_counter = 0
                time.sleep(PARSE_PAUSE)

        print(f"Finished creating vacancy objects from page {index}")
    # после завершения обработки спарсенных вакансий
    # удаляю старые вакансии, которые по любым причинам не обновились
    del_old_vacancies(session)
except Exception as ex:
    print(ex)
finally:
    driver.close()
    driver.quit()

# TODO написать файл для логов
# TODO 5) проработать старт для куки
# TODO компанию работодателя добавить бы в базу данных?
# TODO 1) сделать список своих навыков и требований(? добавить поле в модель требований) # noqa
# TODO 2) сделать выгрузку наиболее подходящих вакансий под требования
# TODO 3) сделать модель реагирования на вакансию, например:
# - откликался и даты отклика(дата последнего отклика), количество откликов (до 3) # noqa
# - пригласили на собес и дата приглашения
# - отказали и дата отказа
# - получил офер
# TODO 6) сделать возможность наполнения бд исходя из самостоятельно сформулированных требований # noqa
# TODO 7) прикрутить телеграм бота для интерфейса для работы с базой данных
# TODO дополнить модель вакансии место расположение работы (город)
# TODO можно ли предусмотреть автоматический рестарт,
# на случай если приложение после запуска случайно упало
# TODO (!) снять данные работы каждой функции и засунуть файл или бд
# для улучшения работы и отслеживания прогресса
# TODO настроить асинхронный запрос парсера по вакансиям
# TODO настроить асинхронную работу с базой данных
# TODO предусмотреть функцию для очистки БД, будет ли работать каскадное удаление  # noqa
# для вакансий, для требований
