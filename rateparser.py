import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


def get_parse_rate_main():
    kzrate = 0
    headers = {
        'User-Agent': UserAgent().chrome
    }
    url = "https://mironline.ru/support/list/kursy_mir/"
    r = requests.get(url, headers=headers)                        # достаём код страницы
    soup = BeautifulSoup(r.text, 'lxml')
    rates_names = soup.find_all("p", style="text-align: left;")   # ищем названия всех валют
    rates = soup.find_all("p", style="text-align: center;")       # ищем курс всех валют
    for i in range(len(rates_names)):
        a = rates_names[i].text.strip()
        if a.count("Казахстанский тенге") > 0:
            kzrate = i
    rates_name = rates_names[kzrate].text.strip()                      # создаем переменную с названием казахстанского тенге
    raterubkz = 1/float(rates[kzrate].text.strip().replace(",", "."))  # создаем переменную с курсом реблей в тенге
    ratekzrub = float(rates[kzrate].text.strip().replace(",", "."))    # создаем переменную с курсом тенге в рубли
    return [rates_name, raterubkz, ratekzrub]


print(get_parse_rate_main())