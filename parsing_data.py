
import re 
from bs4 import BeautifulSoup
import json
import requests
import pandas as pd 


#Разбор пробной страницы

url = 'https://www.autopriwos.by/catalogue/auto-parts-by-make-model-name/bmw/3-e46/cd-cheyndzher.html'


req = requests.get(url)


soup = BeautifulSoup(req.text, 'lxml')


soup.find_all('span', class_ = 'label label-default')




# Собераем ссылки на все категории. Они лежат на тестовой странице
all_parts_categories = soup.find('div', class_ = 'column300').find_all('a')

lst_of_links = []
for i in all_parts_categories:
    categories_link = i.get('href')
    lst_of_links.append(categories_link)

lst_of_links[0]

# Собираем количество объявлений в категории
count_by_categories = {}

for link in lst_of_links:
    url = link
    req = requests.get(url)
    soup_of_categories = BeautifulSoup(req.text, 'lxml')
    category = soup_of_categories.find('h1').text
    count_of_parts = soup_of_categories.find('span', class_ = 'label label-default').text.strip().split(':')[-1]
    count_by_categories[category] = count_of_parts


# Всё информация по объявлениям лежит в блоках tr 
lst_tr = soup.find('table',class_ = 'table table-hover' ).find('tbody').find_all('tr')




# Пробую достать артикул объявления
re.search("Артикул (\d+)", lst_tr[1].find('td').find('a').find('img').get('alt')).group(1)


# Создаю списки VIN, арьткул, цена(новая,старая) 
lst_of_artculs = []
for i in lst_tr:
    lst_of_artculs.append(int(re.search("Артикул (\d+)", i.find('td').find('a').find('img').get('alt')).group(1)))

lst_of_prices = []
for i in lst_tr:
    m = []
    m.append(float(i.find('div', class_ = 'text-success').text[:5].replace(',','.')))
    m.append(float(i.find('div', class_ = 'strike text-muted small').text[:5].replace(',','.')))
    lst_of_prices.append(m)

lst_of_VIN = []
for i in lst_tr:
    lst_of_VIN.append(re.search(r"VIN\s([A-Z0-9]+)" , i.find('td', itemprop = 'description').text).group(1))


# конвертируем в int количество объявлений 
for i in count_by_categories:
    count_by_categories[i] = int(count_by_categories[i])
    


a = list(count_by_categories.keys())

b = list(count_by_categories.values())

df = pd.DataFrame({'categories': a,
                   'parts_coutn': b})





# Словарь для одного артикула
articul_1 = {'Category':'CD-чейнджер б/у BMW 3 E46', 'Articul': 53402846, 'New price': 5000, 'Old price': 6000, 'VIN': 'WBAAL31040FH14142'}

# Словарь для другого артикула
articul_2 = {'Category':'CD-чейнджер б/у BMW 3 E46','Articul': 53412846, 'New price': 6000, 'Old price': 7000, 'VIN': 'WBABX92050PN83367'}

# Список из словарей для разных артикулов
articuls = [articul_1, articul_2]

# Создание DataFrame из списка словарей
df = pd.DataFrame(articuls)




# Собираю пробный датасет
lst_of_categories = a 
lst_of_artculs
lst_of_prices
lst_of_VIN
end_lst = []

for i in range(len(lst_of_artculs)):
    dict_= {}
    dict_['lst_of_categories'.split('_')[-1]] = lst_of_categories[1]
    dict_['lst_of_artculs'.split('_')[-1]] = lst_of_artculs[i]
    dict_['new_'+'lst_of_prices'.split('_')[-1]] = lst_of_prices[i][0]
    dict_['old_'+'lst_of_prices'.split('_')[-1]] = lst_of_prices[i][1]
    dict_['lst_of_VIN'.split('_')[-1]] = lst_of_VIN[i]
    end_lst.append(dict_)

df = pd.DataFrame(end_lst)



# Итоговый код
lst_of_artculs = []
lst_of_prices = []
lst_of_VIN = []
data = []
for link in lst_of_links:
    url = link
    req = requests.get(url)
    m_soup = BeautifulSoup(req.text, 'lxml')
    if len(m_soup.find_all('span', class_ = 'label label-default')) > 1:
        count_of_pages = int(m_soup.find_all('span', class_ = 'label label-default')[1].text[-1])
        for i in range(1, count_of_pages+1):
            url = f'{link}?pg={i}'
            req = requests.get(url)
            soup = BeautifulSoup(req.text, 'lxml')
            lst_tr = soup.find('table',class_ = 'table table-hover' ).find('tbody').find_all('tr')
            for i in lst_tr:
                category = soup.find('h1').text[:-10]
                articuls = i.find('div', class_ = 'nowrap').find('a').text
                if i.find('div', itemprop="offers").text.strip().lower() in ['звоните!','в пути!']:
                    new_price = None
                    old_price = None
                else:
                    new_price = i.find('div', class_ = 'text-success').text[:5].replace(',','.')
                    old_price = i.find('div', class_ = 'strike text-muted small').text[:5].replace(',','.')
                VIN = i.find('td', itemprop = 'description').text.split()[-1]
                data.append([category, articuls,new_price,old_price,VIN])
                
    else:
        lst_tr = m_soup.find('table',class_ = 'table table-hover' ).find('tbody').find_all('tr')
        for i in lst_tr:
            category = m_soup.find('h1').text[:-10]
            articuls = i.find('div', class_ = 'nowrap').find('a').text
            if  i.find('div', itemprop="offers").text.strip().lower() in ['звоните!','в пути!']:
                    new_price = None
                    old_price = None
            else:
                new_price = i.find('div', class_ = 'text-success').text[:5].replace(',','.')
                old_price = i.find('div', class_ = 'strike text-muted small').text[:5].replace(',','.')
            VIN = i.find('td', itemprop = 'description').text.split()[-1]
            data.append([category, articuls,new_price,old_price,VIN])
            


# Итоговой датасет
df = pd.DataFrame(data,columns=['category', 'articuls','new_price','old_price','vin'])



# Подчищаем vin
def replace_value(value):
    if not value.startswith('W'):
        return 'unknown_vin'
    return value

df['vin'] = df['vin'].apply(replace_value)



df = df.dropna().reset_index().drop('index', axis = 1)


df['new_price'] = df['new_price'].str.replace(' ','').astype(float)
df['old_price'] = df['old_price'].str.replace(' ','').astype(float)
df['discount'] = round( (1 - df['new_price'] / df['old_price']) *100,2)



# Сохроняем
df.to_csv('BMW_e46_parts_clean.csv', index=False)



