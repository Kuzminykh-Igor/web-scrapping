import json
import fake_headers
import requests
from bs4 import BeautifulSoup
import time
import unicodedata
import random
from progress.bar import IncrementalBar


def search_pages(url):
    '''
    Функция принимает на вход url поиска.
    Выдаёт файл "found_links.txt" с сылками на вакансии, в которых зарплата в нужной нам валюте.
    '''

    session = requests.Session()
    headers_gen = fake_headers.Headers(browser='chrome', os='win')
    response = session.get(url=url, headers=headers_gen.generate())
    hh_main = BeautifulSoup(response.text, 'lxml')

    pagination_count = int(hh_main.find_all('a', class_='bloko-button')[-2].text)

    bar = IncrementalBar('Выполняется функция search_pages', max=pagination_count, suffix='%(percent)d%%')

    urls = []
    for page in range(0, pagination_count):
        url = f'{URL}&page={page}'
        response = session.get(url=url, headers=headers_gen.generate())
        soup = BeautifulSoup(response.text, 'lxml')
        items = soup.find_all('div', class_='vacancy-serp-item__layout')

        for item in items:
            link_job = item.find('a', class_='serp-item__title').get('href')
            salary = item.find('span', class_='bloko-header-section-2').text
            if any([money in salary for money in MONEYS]):  # Проверка на определённую валюту.
                urls.append(link_job)
        time.sleep(random.randrange(3, 7))
        bar.next()

    with open('data/found_links.txt', 'w') as file:
        for url in urls:
            file.write(f'{url}\n')

    session.close()
    bar.finish()

    return 'Файл с сылками found_links.txt, для следующей работы, записан.'


def searches_for_keywords(file_path):
    '''
    Функция проходит по ссылкам вакансии в файле "found_links.txt".
    И проверяет описание вакансии на наличие ключевых слов.
    '''

    with open(file_path) as file:
        urls_list = [url.strip() for url in file.readlines()]

    bar = IncrementalBar('Выполняется функция searches_for_keywords', max=len(urls_list), suffix='%(percent)d%%')

    session = requests.Session()

    job_list = []
    for url in urls_list:
        headers_gen = fake_headers.Headers(browser='firefox', os='lin')
        response = session.get(url=url, headers=headers_gen.generate())
        soup = BeautifulSoup(response.text, "lxml")

        time.sleep(random.randrange(4, 9))

        desc = soup.find('div', attrs={'data-qa': 'vacancy-description'}).text
        title = soup.find('h1', class_='bloko-header-section-1').text
        salary = soup.find('span', class_='bloko-header-section-2 bloko-header-section-2_lite').text
        company_name = soup.find('span',
                                 attrs={'data-qa': 'bloko-header-2'},
                                 class_='bloko-header-section-2 bloko-header-section-2_lite').text
        try:
            address = soup.find(attrs={'data-qa': 'vacancy-view-location'}).text
        except Exception as _ex:
            address = soup.find(attrs={'data-qa': 'vacancy-view-raw-address'}).text

        if any([key in desc.lower() for key in KEYWORDS]):  # Проверка описания вакансии на ключевые слова.
            job_list.append(
                {
                    'Вакансия': title,
                    'Зарплата': unicodedata.normalize("NFKD", salary),
                    'Название компании': unicodedata.normalize("NFKD", company_name),
                    'Адрес': unicodedata.normalize("NFKD", address),
                    'Ссылка': url
                }
            )
        bar.next()

    with open('data/vacancy.json', 'w', encoding='utf-8', newline='') as file:
        json.dump(job_list, file, ensure_ascii=False, indent=2)

    session.close()
    bar.finish()

    return 'Готово!'


def main():
    # print(search_pages(url=URL))
    print(searches_for_keywords('data/found_links.txt'))


if __name__ == '__main__':
    URL = 'https://spb.hh.ru/search/vacancy?text=python&area=1&area=2&only_with_salary=true'
    MONEYS = ['$', '€']  # ['₽', '$', '€'].
    KEYWORDS = ['django', 'flask']
    main()