import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from tqdm import tqdm
from db import session, create


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
    """ Получает адреса страниц списка вакансий.
    """
    print('Getting pages urls...')
    paginator_block = driver.find_element(By.XPATH, "//div[@data-qa='pager-block']") # noqa
    # получаю количество страниц
    last_page_number = paginator_block.find_elements(
        By.CLASS_NAME, 'pager-item-not-in-short-range')[-1].text
    url_form = driver.current_url
    # собираю список страниц
    pages_urls = []
    for page_number in tqdm(range(0, (int(last_page_number)))):
        url = f"{url_form}&page={page_number}"
        pages_urls.append(url)
    return pages_urls


def collecting_simple_info(pages_urls, driver: webdriver.Chrome):
    """ Формирует список по вакансиям (список).
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
            vacancy_data.append([vacancy_index, name, vacancy_exp, vacancy_url]) # noqa
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
        vacancy_detail_data.append([vac_index, vac_name, vac_exp,
                                    vac_salary_net, vac_salary_gross,
                                    skills, vac_url])
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
