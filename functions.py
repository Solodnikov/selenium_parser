import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from tqdm import tqdm
from db import session, create, Vacancy
import re
import datetime
from sqlalchemy.orm import Session


def authorization_hh(driver: webdriver.Chrome, url, email, password):
    """Авторизация в hh"""

    print('Authorization...')

    driver.get(url=url)
    # input_email
    input_email = driver.find_element(By.XPATH, "/html/body/div[5]/div/div[3]/div[1]/div/div/div/div/div/div[1]/div[1]/div/div[2]/form/fieldset/input") # noqa
    input_email.clear()
    input_email.send_keys(email)
    time.sleep(1)

    # open_password
    password_button = driver.find_element(By.XPATH, "/html/body/div[5]/div/div[3]/div[1]/div/div/div/div/div/div[1]/div[1]/div/div[2]/form/div[4]/button[2]") # noqa
    password_button.click()
    time.sleep(1)

    # input_password
    input_password = driver.find_element(By.XPATH, "/html/body/div[5]/div/div[3]/div[1]/div/div/div/div/div/div[1]/div[1]/div/form/div[2]/fieldset/input") # noqa
    input_password.clear()
    input_password.send_keys(password)
    time.sleep(1)

    # enter
    enter_button = driver.find_element(By.XPATH, "/html/body/div[5]/div/div[3]/div[1]/div/div/div/div/div/div[1]/div[1]/div/form/div[6]/button[1]") # noqa
    enter_button.click()

    time.sleep(1)
    print('Authorization - Done')


def check_driver(driver: webdriver.Chrome):
    """ Переход на страницу проверки работы веб-драйвера.
    """
    driver.get('https://intoli.com/blog/' +
               'not-possible-to-block-chrome-headless/' +
               'chrome-headless-test.html')
    time.sleep(1)


def from_main_to_my_resumes(driver: webdriver.Chrome):
    """ Переход c главной страницы на страницу резюме.
    """
    print('Choosing my resume...')
    my_resume_button = driver.find_element(By.XPATH,"//a[@data-qa='mainmenu_myResumes']") # noqa
    my_resume_button.click()
    time.sleep(1)


def from_my_resumes_to_recomended_vacations(driver: webdriver.Chrome):
    """ Переход cо страницы резюме на список рекомендуемых вакансий.
    """
    print('Getting vacancies list...')
    # vacancies = driver.find_element(By.XPATH,'/html/body/div[5]/div/div[3]/div[1]/div/div/div[1]/div[5]/div/div/div[6]/div/div[2]/a') # noqa
    vacancies = driver.find_element(By.XPATH, "/html/body/div[5]/div/div[3]/div[1]/div/div/div[1]/div[6]/div[1]/div/div[6]/div/div[2]/a")  # noqa
    vacancies.click()
    time.sleep(1)


def get_pages_urls(driver: webdriver.Chrome):
    """ Находясь на 1 страницы списка вакансий,
    получает адреса всех страниц списков вакансий с пагинатора.
    """
    print('Getting pages urls...')
    paginator_block = driver.find_element(By.XPATH, "//div[@data-qa='pager-block']") # noqa
    # получаю количество страниц
    last_page_number = paginator_block.find_elements(
        By.CLASS_NAME, 'pager-item-not-in-short-range')[-1].text
    url_form = driver.current_url
    # собираю список страниц
    pages_urls = []
    for page_number in range(0, (int(last_page_number))):
        url = f"{url_form}&page={page_number}"
        pages_urls.append(url)
    # возвращаю список страниц списков вакансий
    return pages_urls


def collecting_simple_info(pages_urls, driver: webdriver.Chrome):
    """ Формирует список, для дальнейшего парсинга сведений по вакансиям.
        Вариант 1 для сбора сведений для списка вакансий.
    """
    print('Vacancy data preparе...')
    vacancy_data = []
    print(f'Total pages to collect - {len(pages_urls)}')
    for page_index, page_url in enumerate(pages_urls):
        driver.get(url=page_url)
        vacancy_list = driver.find_elements(By.CLASS_NAME, 'vacancy-serp-item__layout') # noqa
        for vacancy_index, vacancy in enumerate(vacancy_list):
            name = vacancy.find_element(By.TAG_NAME, "a").text # noqa
            vacancy_url = vacancy.find_element(By.TAG_NAME, "a").get_attribute("href") # noqa
            vacancy_exp = vacancy.find_element(By.XPATH, "//div[@data-qa='vacancy-serp__vacancy-work-experience']").text # noqa
            vacancy_data.append([
                vacancy_index,
                name,
                vacancy_exp,
                vacancy_url]) # noqa
        print(f'Vacancy page {page_index} - collected.')
    print('Collecting pages data done.')
    return vacancy_data


def get_vacancy_info(vacancy_data: list, driver: webdriver.Chrome):
    """ Выполняет сбор детальных сведений по вакансии.
    """
    print('Vacancy detail collecting...')
    vacancy_detail_data = []
    # skill_list = []
    for vacancy in tqdm(vacancy_data):
        vac_index = vacancy[0]
        vac_name = vacancy[1]
        vac_exp = vacancy[2]
        vac_url = vacancy[-1]
        driver.get(url=vac_url)

        # получаю зп без налога
        try:
            vac_salary_net = driver.find_element(
                By.CLASS_NAME, "vacancy-title").find_element(
                    By.XPATH, "//span[@data-qa='vacancy-salary-compensation-type-net']") # noqa
            vac_salary_net = vac_salary_net.text
        except NoSuchElementException:
            vac_salary_net = None
        # если без налога не указана зп узнаю про зп с налогом
        if not vac_salary_net:
            try:
                vac_salary_gross = driver.find_element(
                    By.CLASS_NAME, "vacancy-title").find_element(
                        By.XPATH, "//span[@data-qa='vacancy-salary-compensation-type-gross']") # noqa
                vac_salary_gross = vac_salary_gross.text
            except NoSuchElementException:
                vac_salary_gross = None
        else:
            vac_salary_gross = None

        # получение сведений о навыках
        try:
            vac_skills = driver.find_element(
                By.CLASS_NAME, "bloko-tag-list").find_elements(
                    By.XPATH, "//span[@data-qa='bloko-tag__text']")
            # for skill in vac_skills:
            #     skill_list.append(skill.text)
            skill_list = [skill.text for skill in vac_skills]
            skills = ', '.join(skill_list)
        except NoSuchElementException:
            # vac_skills = None
            skills = None
        
        # выявление требований из вакансии
        try:
            mess = driver.find_element(By.XPATH, "//div[@data-qa='vacancy-description']").text  # noqa
            requirements = get_vacancy_requirements(mess)
            # проверка есть такое требование в базе данных
            # for requirement in requirements:
            #     if requirement
            # если нет то включить в базу данных

        except NoSuchElementException:
            # vac_skills = None
            mess = None

        vacancy_detail_data.append([vac_index,
                                    vac_name,
                                    vac_exp,
                                    vac_salary_net,
                                    vac_salary_gross,
                                    skills,
                                    vac_url])
        # пробую добавить в базу данных
    return vacancy_detail_data


def collecting_test_info(pages_urls, driver: webdriver.Chrome):
    """ Формирует список по вакансиям (список).
    """
    print('Vacancy test data preparе...')
    vacancy_data = []
    page_url_1 = pages_urls[0]
    driver.get(url=page_url_1)
    vacancy_list = driver.find_elements(By.CLASS_NAME, 'vacancy-serp-item__layout') # noqa
    for vacancy_index, vacancy in tqdm(enumerate(vacancy_list[:4])):
        name = vacancy.find_element(By.TAG_NAME, "a").text # noqa
        vacancy_url = vacancy.find_element(By.TAG_NAME, "a").get_attribute("href") # noqa
        vacancy_exp = vacancy.find_element(By.XPATH, "//div[@data-qa='vacancy-serp__vacancy-work-experience']").text # noqa
        vacancy_data.append([vacancy_index, name, vacancy_exp, vacancy_url]) # noqa
    print('Collecting test page data done.')
    return vacancy_data


def get_vacancy_base_info(pages_urls, driver: webdriver.Chrome):
    """ Получаю url и id вакансий.
    """
    print('Getting_vacancy_base_info...')
    vacancy_data = []
    print(f'Total pages to collect - {len(pages_urls)}')
    # Получить только текущую дату
    vac_date_parse = datetime.date.today()
    # Форматируем дату в строку
    vac_date_parse_str = vac_date_parse.strftime('%Y-%m-%d')
    # перебираю страницы списков вакансий
    pages_urls = pages_urls  # ОГРАНИЧЕНИЕ ДЛЯ ТЕСТА
    for page_index, page_url in enumerate(pages_urls):
        print(f'...start collecting from page {page_index}.')
        driver.get(url=page_url)
        vacancy_list = driver.find_elements(By.CLASS_NAME, 'vacancy-serp-item__layout') # noqa
    # перебираю данные о вакансиях на странице списка вакансий
        for vacancy in tqdm(vacancy_list):
            vac_name = vacancy.find_element(By.TAG_NAME, "a").text # noqa
            vac_url = vacancy.find_element(By.TAG_NAME, "a").get_attribute("href") # noqa
            vac_number = get_vacancy_number(vac_url)
            vac_exp = vacancy.find_element(By.XPATH, "//div[@data-qa='vacancy-serp__vacancy-work-experience']").text # noqa
            vacancy_data.append(
                {
                    'vac_name': vac_name,
                    'vac_url': vac_url,
                    'vac_number': vac_number,
                    'vac_exp': vac_exp,
                    'vac_date_parse': vac_date_parse_str
                }
            )
    # requirement
    # vac_salary_net
    # vac_salary_gross
        print(f'...base info collected from page {page_index}')
    print('Vacancies base info collected.')
    return vacancy_data


def get_vacancy_number_from_url(page_url: str) -> int:
    """ Получаю номер вакансии из строки url адреса вакансии.
    """
    pattern = r"/vacancy/(\d+)"
    match = re.search(pattern, page_url)
    if match:
        return int(match.group(1))  # Номер вакансии
    return None


def get_vacancy_requirements(mess: str) -> set:
    """Из строки вычленяет все латинские слова,
    возвращает список.
    Пассивная защита - если получено более 30 объектов,
    значит найдены не навыки, а что-то другое и вернет None"""
    pattern = r'[a-zA-Z-]{2,}+(?:[\s-]\d+(?:\.\d+)?)?(?:\sAPI)?(?:\.[a-zA-Z-]{1,10})?'
    requirements = set(re.findall(pattern, mess))
    if len(requirements) > 30:
        requirements = None
    return requirements


def get_vacancy_info_ver2(vacancy_data: list, driver: webdriver.Chrome):
    """ Выполняет сбор детальных сведений по вакансии.
    Обновленный сборщик сведений.
    """
    driver.get(url=vacancy_data['vac_url'])
    # получаю зп без налога
    try:
        vac_salary_net = driver.find_element(
            By.CLASS_NAME, "vacancy-title").find_element(
                By.XPATH, "//span[@data-qa='vacancy-salary-compensation-type-net']") # noqa
        vac_salary_net = vac_salary_net.text
    except NoSuchElementException:
        vac_salary_net = None

    # если без налога не указана зп узнаю про зп с налогом
    if not vac_salary_net:
        try:
            vac_salary_gross = driver.find_element(
                By.CLASS_NAME, "vacancy-title").find_element(
                    By.XPATH, "//span[@data-qa='vacancy-salary-compensation-type-gross']") # noqa
            vac_salary_gross = vac_salary_gross.text
        except NoSuchElementException:
            vac_salary_gross = None
    else:
        vac_salary_gross = None

    # получение сведений о навыках из раздела навыков
    try:
        vac_skills = driver.find_element(
            By.CLASS_NAME, "bloko-tag-list").find_elements(
                By.XPATH, "//span[@data-qa='bloko-tag__text']")
    # TODO: необходимо получить множество
        skill_set = set(skill.text for skill in vac_skills)
        # skills = ', '.join(skill_list)
    except NoSuchElementException:
        skill_set = None

    # выявление требований из вакансии
    try:
        mess = driver.find_element(By.XPATH, "//div[@data-qa='vacancy-description']").text  # noqa
        requirements = get_vacancy_requirements(mess)
    except NoSuchElementException:
        requirements = None

    if requirements and skill_set:
        for requirement in requirements:
            if requirement.lower() not in {skill.lower() for skill in skill_set}:
                skill_set.add(requirement)
        requirements_data = skill_set

    elif requirements:
        requirements_data = requirements
    else:
        requirements_data = skill_set

    vacancy_detail_data = {
        'vac_number': vacancy_data['vac_number'],
        'vac_url': vacancy_data['vac_url'],
        'vac_name': vacancy_data['vac_name'],
        'vac_exp': vacancy_data['vac_exp'],
        'vac_salary_net': vac_salary_net,
        'vac_salary_gross': vac_salary_gross,
        'vac_date_parse': vacancy_data['vac_date_parse'],
        'requirements': requirements_data
    }
    return vacancy_detail_data
    # TODO: зп пересчитывать сразу в одном формате - на руки
    # TODO: предусмотреть пересчет зп для уже внесенных позиций по которым зп с налогом
    # TODO: не проверять позиции, которые есть в БД
    # TODO: не проверять позиции, которые есть в БД, за исключением случая если давность дня 3
    # TODO: возможно учитывать требования к вакансии отдельно навыки и в тексте
    # TODO: научиться делить данные в тексте на обязательные и желательные дополнительно
    # TODO: если нет данных о зп ни с налогом ни без, вносить сведение об отсутствии данных


def get_vacancy_urls_on_page(page_url: str, driver: webdriver.Chrome) -> list:
    """ Получаю список url вакансий на странице.
    """
    print('Getting page url...')
    driver.get(url=page_url)
    vacancy_data = []
    vacancy_list = driver.find_elements(By.CLASS_NAME, 'vacancy-serp-item__layout') # noqa
    for vacancy in tqdm(vacancy_list):
        try:
            vac_url = vacancy.find_element(By.TAG_NAME, "a").get_attribute("href") # noqa
        except Exception:
            continue
        vacancy_data.append(vac_url)
    return vacancy_data


def get_vacancy_full_info(vacancy_url: str, driver: webdriver.Chrome):
    """ По url получаю все сведения по вакансии.
    """
    print(f'получаю вседения по вакансии url {vacancy_url}')
    driver.get(vacancy_url)
    # БЛОК ПОЛУЧЕНИЯ ЗП
    # получаю зп без налога
    try:
        vac_salary_net = driver.find_element(
            By.CLASS_NAME, "vacancy-title").find_element(
                By.XPATH, "//span[@data-qa='vacancy-salary-compensation-type-net']") # noqa
        vac_salary_net = vac_salary_net.text
    except NoSuchElementException:
        vac_salary_net = None
    # если без налога не указана зп узнаю про зп с налогом
    if not vac_salary_net:
        try:
            vac_salary_gross = driver.find_element(
                By.CLASS_NAME, "vacancy-title").find_element(
                    By.XPATH, "//span[@data-qa='vacancy-salary-compensation-type-gross']") # noqa
            vac_salary_gross = vac_salary_gross.text
        except NoSuchElementException:
            vac_salary_gross = None
    else:
        vac_salary_gross = None
    
    # БЛОК ПОЛУЧЕНИЯ НАВЫКОВ
    # получение навыков из раздела навыков
    try:
        vac_skills = driver.find_element(
            By.CLASS_NAME, "bloko-tag-list").find_elements(
                By.XPATH, "//span[@data-qa='bloko-tag__text']")
        skill_set = set(skill.text for skill in vac_skills)
    except NoSuchElementException:
        skill_set = None
    # получение навыков из текста вакансии
    try:
        mess = driver.find_element(By.XPATH, "//div[@data-qa='vacancy-description']").text  # noqa
        requirements = get_vacancy_requirements(mess)
    except NoSuchElementException:
        requirements = None
    if requirements and skill_set:
        requirements_data = requirements | skill_set
    elif requirements:
        requirements_data = requirements
    else:
        requirements_data = skill_set

    # БЛОК ПОЛУЧЕНИЯ НОМЕРА ВАКАНСИИ
    vac_number = get_vacancy_number_from_url(vacancy_url)
    # БЛОК ПОЛУЧЕНИЯ НАЗВАНИЯ ВАКАНСИИ
    vac_name = driver.find_element(By.XPATH, "//h1[@data-qa='vacancy-title']").text  # noqa
    # БЛОК ПОЛУЧЕНИЯ ЭКСПЕРТИЗЫ
    vac_exp = driver.find_element(By.XPATH, "//span[@data-qa='vacancy-experience']").text  # noqa
    # БЛОК ПОЛУЧЕНИЯ ДАТЫ ПАРСИНГА
    vac_date_parse = datetime.date.today().strftime('%Y-%m-%d')

    vacancy_data = {
        'vac_number': vac_number,
        'vac_url': vacancy_url,
        'vac_name': vac_name,
        'vac_exp': vac_exp,
        'vac_salary_net': vac_salary_net,
        'vac_salary_gross': vac_salary_gross,
        'vac_date_parse': vac_date_parse,
        'requirements': requirements_data
    }
    return vacancy_data


def vacancy_exist(session: Session, vacancy_url: str) -> bool:
    """Проверяет есть ли в базе данных вакансия по url"""
    return session.query(Vacancy).filter_by(vac_url=vacancy_url).first()
