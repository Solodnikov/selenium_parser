import datetime
import re
import time
from typing import Dict, List, Set

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from tqdm import tqdm

from constants import INCORRECT_NAMES


def authorization_hh(
        driver: webdriver.Chrome,
        url: str,
        email: str,
        password: str,
        sleep_time: int = 2
) -> None:
    """ Прохождение авторизации. """

    print('Authorization...')
    driver.get(url=url)
    # input_email
    input_email = driver.find_element(By.NAME, "login")
    input_email.clear()
    input_email.send_keys(email)
    time.sleep(sleep_time)

    # open_password
    password_form = driver.find_element(
        By.XPATH,
        "//span[@data-qa='expand-login-by-password-text']"
    )
    password_form.click()
    time.sleep(sleep_time)

    # input_password
    input_password = driver.find_element(
        By.XPATH, "//input[@data-qa='login-input-password']")
    input_password.clear()
    input_password.send_keys(password)
    time.sleep(sleep_time)

    # enter
    enter_button = driver.find_element(
        By.CLASS_NAME, "account-login-actions").find_element(
            By.TAG_NAME, "button")
    enter_button.click()
    time.sleep(sleep_time)
    print('Authorization - Done')


def check_driver(
        driver: webdriver.Chrome,
        sleep_time: int = 2
) -> None:
    """ Переход на страницу проверки работы веб-драйвера. """
    driver.get('https://intoli.com/blog/' +
               'not-possible-to-block-chrome-headless/' +
               'chrome-headless-test.html')
    time.sleep(sleep_time)


def from_main_to_my_resumes(
        driver: webdriver.Chrome,
        sleep_time: int = 2
) -> None:
    """ Переход c главной страницы на страницу резюме. """
    print('Choosing my resume...')
    xpath_list = [
        "//div[@data-qa='mainmenu_myResumes']",
        "//a[@data-qa='mainmenu_myResumes']",
    ]
    my_resume_button = url_iterator(driver, xpath_list)
    time.sleep(sleep_time)
    my_resume_button.click()
    time.sleep(sleep_time)


def from_my_resumes_to_recomended_vacations(
        driver: webdriver.Chrome,
        sleep_time: int = 2
) -> None:
    """ Переход cо страницы резюме на список рекомендуемых вакансий. """
    print('Getting vacancies list...')
    xpath_list = [
        "//a[@data-qa='resume-recommendations__button_updateResume']",
        "//a[@data-qa='resume-recommendations__button_editResume']",
        "//a[@data-qa='resume-recommendations__button_respond']",
    ]
    for xpath in xpath_list:
        try:
            vacancies = driver.find_element(By.XPATH, xpath)
            break
        except NoSuchElementException:
            print('No such element')
    vacancies.click()
    time.sleep(sleep_time)


def get_pages_urls(
        driver: webdriver.Chrome
) -> List[str]:
    """
    Из 1 страницы списка вакансий
    формирует из пагинатораспикок страниц списков вакансий.
    """
    print('Getting pages urls...')
    paginator_block = driver.find_element(
        By.XPATH, "//*[contains(@class, 'magritte-number-pages-container')]"
    )
    # получаю последнюю страницу
    last_page_number = paginator_block.find_elements(
        By.TAG_NAME, "li")[-2].text
    # собираю список страниц
    url_form = driver.current_url
    pages_urls = []
    for page_number in range(0, (int(last_page_number))):
        url = f"{url_form}&page={page_number}"
        pages_urls.append(url)
    return pages_urls


def get_vacancy_number_from_url(
        page_url: str
) -> int | None:
    """
    Получаю номер вакансии из строки url адреса вакансии.
    """
    pattern = r"/vacancy/(\d+)"
    match = re.search(pattern, page_url)
    if match:
        return int(match.group(1))  # Номер вакансии
    return None


def get_vacancy_requirements(
        mess: str
) -> Set[str]:
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


def get_vacancy_urls_on_page(
        page_url: str,
        driver: webdriver.Chrome
) -> List[str]:
    """ Получаю список url вакансий на странице. """
    print('Getting page url...')
    driver.get(url=page_url)
    vacancy_data = []
    main_vacancies_block = driver.find_element(
        By.XPATH, "//div[@data-qa='vacancy-serp__results']"
    )
    vacancies_blocks = main_vacancies_block.find_elements(
        By.XPATH, "//*[contains(@class, 'vacancy-info')]"
    )
    for vacancy in tqdm(vacancies_blocks):
        try:
            vac_name = (
                vacancy.find_element(
                    By.XPATH,
                    "//span[@data-qa='serp-item__title-text']"
                ).text).lower()
            vac_name_words = vac_name.split()
            has_common = any(element.lower() in vac_name_words for element in INCORRECT_NAMES) # noqa
            # если имеются соответствия url такой вакансии не включается в перечень для парсинга  # noqa
            if has_common:
                continue
            vac_url = vacancy.find_element(
                By.TAG_NAME, "a").get_attribute("href")
        except Exception:
            continue
        vacancy_data.append(vac_url)
    return vacancy_data


def get_vacancy_full_info(
        vacancy_url: str,
        driver: webdriver.Chrome,
        sleep_time: int = 2
) -> Dict[str, str | int | None]:
    """ По url получаю все сведения по вакансии."""
    print(f'получаю вседения по вакансии url {vacancy_url}')
    driver.get(vacancy_url)
    time.sleep(sleep_time)

    # БЛОК ПОЛУЧЕНИЯ ЗП без налога
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
                    By.XPATH,
                    "//span[@data-qa='vacancy-salary-compensation-type-gross']") # noqa
            vac_salary_gross = vac_salary_gross.text
            max_match = re.search(r'до (\d+ ?)(\d+)?', vac_salary_gross)
            min_match = re.search(r'от (\d+ ?)(\d+)?', vac_salary_gross)
            if min_match:
                min_value = "".join(
                    item.strip() for item in min_match.groups()
                )
                min_value = int(min_value)
                min_value = round(min_value - min_value*0.13)
            if max_match:
                max_value = "".join(
                    item.strip() for item in max_match.groups()
                )
                max_value = int(max_value)
                max_value = round(max_value - max_value*0.13)
        except NoSuchElementException:
            max_value, min_value = None, None

    # БЛОК ПОЛУЧЕНИЯ НАВЫКОВ
    # получение навыков из раздела навыков
    try:
        vac_skills = driver.find_elements(
            By.XPATH,
            "//li[@data-qa='skills-element']"
        )
        skill_set = set(skill.text.lower() for skill in vac_skills)
    except NoSuchElementException:
        skill_set = None
    # получение навыков из текста вакансии
    try:
        mess = driver.find_element(
            By.XPATH,
            "//div[@data-qa='vacancy-description']").text
        requirements = get_vacancy_requirements(mess)
    except NoSuchElementException:
        requirements = None
    if requirements and skill_set:
        requirements_data = requirements | skill_set
    elif requirements:
        requirements_data = requirements
    else:
        requirements_data = skill_set
    # номер вакансии
    vac_number = get_vacancy_number_from_url(vacancy_url)
    # название вакансии
    vac_name = driver.find_element(By.XPATH, "//h1[@data-qa='vacancy-title']").text  # noqa
    # экспертиза вакансии
    vac_exp = driver.find_element(By.XPATH, "//span[@data-qa='vacancy-experience']").text  # noqa
    # дата парсинга
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


def url_iterator(
        driver: webdriver.Chrome,
        xpath_array: list,
        sleep_time: int = 2
) -> WebElement:
    """
    Предоставляет из списка XPATH WebElement.
    """
    for xpath in xpath_array:
        try:
            block = driver.find_element(By.XPATH, xpath)
            time.sleep(sleep_time)
            break
        except NoSuchElementException:
            print('No such element')
    return block
