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
# disable webdriver mode
options.add_argument('--disable-blink-features=AutomationControlled')


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
    # проверка работы веб драйвера
    driver.get('https://intoli.com/blog/' +
               'not-possible-to-block-chrome-headless/' +
               'chrome-headless-test.html')
    time.sleep(10)

    # disable webdriver mode


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

    time.sleep(1)

    # мои резюме
    my_resume_button = driver.find_element(By.XPATH,"//a[@data-qa='mainmenu_myResumes']")
    my_resume_button.click()
    time.sleep(1)

    # вакансии на 1 странице
    # vacancies = driver.find_element(By.XPATH,"//a[@data-qa='resume-recommendations__button_respond']")
    vacancies = driver.find_element(By.XPATH,'/html/body/div[5]/div/div[3]/div[1]/div/div/div[1]/div[5]/div/div/div[6]/div/div[2]/a')
    vacancies.click()
    time.sleep(10)

    # парсинг вакансий на странице
    vacancy_list = driver.find_elements(By.CLASS_NAME,'vacancy-serp-item__layout')
    for vacancy in vacancy_list:
        name = vacancy.find_element(By.XPATH, "//a[@data-qa='serp-item__title']").text # название
        # link = driver.find_element(By.LINK_TEXT, name)

        # vacancy.find_element(By.XPATH, "//a[@data-qa='serp-item__title']").text # зарплата может отсутствовать
        # vacancy.find_element(By.XPATH,"//a[@href]")
        # vacancy.find_element(By.XPATH,'//a[@href="'+url+'"]')



except Exception as ex:
    print(ex)
finally:
    driver.close()
    driver.quit()
