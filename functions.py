import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from tqdm import tqdm
import re
import datetime
from constants import INCORRECT_NAMES


def authorization_hh(driver: webdriver.Chrome, url, email, password):
    """Авторизация в hh"""

    print('Authorization...')

    driver.get(url=url)
    # input_email
    input_email = driver.find_element(By.NAME, "login")
    input_email.clear()
    input_email.send_keys(email)
    time.sleep(1)

    # open_password
    open_password_form = driver.find_element(
        By.CLASS_NAME, 'account-login-actions').find_elements(
            By.TAG_NAME, 'button')[1]
    open_password_form.click()
    time.sleep(1)

    # input_password
    input_password = driver.find_element(
        By.XPATH, "//input[@data-qa='login-input-password']")
    input_password.clear()
    input_password.send_keys(password)
    time.sleep(1)

    # enter"
    enter_button = driver.find_element(
        By.CLASS_NAME,
        "account-login-actions").find_element(
            By.TAG_NAME, "button")
    enter_button.click()

    time.sleep(5)
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
    # my_resume_button = driver.find_element(By.XPATH,"//a[@data-qa='mainmenu_myResumes']") # noqa
    bar = driver.find_element(
        By.XPATH,
        "//span[@class='supernova-icon supernova-icon_mobile']"
    )
    bar.click()
    time.sleep(2)
    my_resume_button = driver.find_element(
        By.CLASS_NAME,
        'supernova-dropdown-option'
    )
    my_resume_button.click()
    time.sleep(2)


def from_my_resumes_to_recomended_vacations(driver: webdriver.Chrome):
    """ Переход cо страницы резюме на список рекомендуемых вакансий.
    """
    print('Getting vacancies list...')
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
    pattern = r'[a-zA-Z-]{2,}+(?:\sAPI)?(?:\.[a-zA-Z-]{1,10})?'
    requirements = set(re.findall(pattern, mess))
    if len(requirements) > 50:
        return None
    # Удаление дефисов в начале и конце слова
    requirements = {re.sub(r'^-+|-+$', '', requirement.lower()) for requirement in requirements}  # noqa
    return requirements


def get_vacancy_urls_on_page(page_url: str, driver: webdriver.Chrome) -> list:
    """ Получаю список url вакансий на странице.
    """
    print('Getting page url...')
    driver.get(url=page_url)
    vacancy_data = []
    vacancy_list = driver.find_elements(By.CLASS_NAME, 'vacancy-serp-item__layout') # noqa
    for vacancy in tqdm(vacancy_list):
        try:
            vac_name = (vacancy.find_element(By.XPATH, "//a[@data-qa='serp-item__title']").text).lower() # noqa
            vac_name_words = vac_name.split()
            has_common = any(element.lower() in vac_name_words for element in INCORRECT_NAMES) # noqa
            # если имеются соответствия url такой вакансии не включается в перечень для парсинга  # noqa
            if has_common:
                continue
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
    max_value, min_value = None, None
    try:
        vac_salary_net = driver.find_element(
            By.CLASS_NAME, "vacancy-title").find_element(
                By.XPATH, "//span[@data-qa='vacancy-salary-compensation-type-net']") # noqa
        vac_salary_net = vac_salary_net.text
        max_match = re.search(r'до (\d+ ?)(\d+)?', vac_salary_net)
        min_match = re.search(r'от (\d+ ?)(\d+)?', vac_salary_net)
        if min_match:
            min_value = "".join(item.strip() for item in min_match.groups())
            min_value = int(min_value)
        if max_match:
            max_value = "".join(item.strip() for item in max_match.groups())
            max_value = int(max_value)
    except NoSuchElementException:
        max_value, min_value = None, None

    # если без налога не указана зп узнаю про зп с налогом
    if not max_value and not min_value:
        try:
            vac_salary_gross = driver.find_element(
                By.CLASS_NAME, "vacancy-title").find_element(
                    By.XPATH, "//span[@data-qa='vacancy-salary-compensation-type-gross']") # noqa
            vac_salary_gross = vac_salary_gross.text
            max_match = re.search(r'до (\d+ ?)(\d+)?', vac_salary_gross)
            min_match = re.search(r'от (\d+ ?)(\d+)?', vac_salary_gross)
            if min_match:
                min_value = "".join(item.strip() for item in min_match.groups()) # noqa
                min_value = int(min_value)
                min_value = round(min_value - min_value*0.13)
            if max_match:
                max_value = "".join(item.strip() for item in max_match.groups()) # noqa
                max_value = int(max_value)
                max_value = round(max_value - max_value*0.13)
        except NoSuchElementException:
            max_value, min_value = None, None

    # БЛОК ПОЛУЧЕНИЯ НАВЫКОВ
    # получение навыков из раздела навыков
    try:
        vac_skills = driver.find_element(
            By.CLASS_NAME, "bloko-tag-list").find_elements(
                By.XPATH, "//span[@data-qa='bloko-tag__text']")
        skill_set = set(skill.text.lower() for skill in vac_skills)
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
        'vac_salary_min': min_value,
        'vac_salary_max': max_value,
        'vac_date_parse': vac_date_parse,
        'requirements': requirements_data
    }
    return vacancy_data
