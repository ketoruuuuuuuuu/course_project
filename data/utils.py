from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pytz
import pandas as pd
from tqdm import trange
import random
import time
from PIL import Image
from io import BytesIO

def parse_offer(scraper,url):
    status = 1
    page = scraper.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    if soup.text.find("Captcha") > 0:
            print('Капча')
            status = 0
    elif soup.text.find('Объявление снято с публикации') > 0:
          print('Объявление снято с публикации')
          status = 0
    elif page.status_code == 200:
          print('Страница получена')
    else:
          print('Что-то пошло не так ({})'.format(page.status_code)) 
          status = 0 
    return soup,status


def get_date_of_post(soup):
    date_offer_full = soup.find('div',class_ = "a10a3f92e9--item--qLmCs").find('span')
    date_offer_full = date_offer_full.text
    date_offer = date_offer_full[date_offer_full.find(':')+2:]
    now = datetime.now(pytz.timezone('Europe/Moscow'))
    date_list = date_offer.split(',')
    if date_list[0] == 'вчера':
        vchera = now - timedelta(days=1)
        vchera = vchera.strftime("%d/%m/%Y")
        date_list[0] = vchera
    elif date_list[0] == 'сегодня':
        today = now.strftime("%d/%m/%Y")
        date_list[0] = today
    else:
        date_0 = date_list[0].split(' ')
        if date_0[1] == 'ноя':
            date_0 = '{}/11/2023'.format(date_0[0])
            date_list[0] = date_0
        if date_0[1] == 'дек':
            date_0 = '{}/12/2023'.format(date_0[0])
            date_list[0] = date_0
        if date_0[1] == 'янв':
            date_0 = '{}/1/2024'.format(date_0[0])
            date_list[0] = date_0
        if date_0[1] == 'фев':
            date_0 = '{}/2/2024'.format(date_0[0])
            date_list[0] = date_0
    date_offer = ' '.join(date_list)
    return(date_offer)

about_flat_info = 'a10a3f92e9--color_black_100--Ephi7 a10a3f92e9--lineHeight_6u--cedXD a10a3f92e9--fontWeight_normal--JEG_c a10a3f92e9--fontSize_16px--QNYmt a10a3f92e9--display_block--KYb25 a10a3f92e9--text--e4SBY a10a3f92e9--text_letterSpacing__0--cQxU5'
about_flat_type_info = 'a10a3f92e9--color_gray60_100--mYFjS a10a3f92e9--lineHeight_6u--cedXD a10a3f92e9--fontWeight_normal--JEG_c a10a3f92e9--fontSize_16px--QNYmt a10a3f92e9--display_block--KYb25 a10a3f92e9--text--e4SBY a10a3f92e9--text_letterSpacing__0--cQxU5'

#color2 HOUSE INFO                               
HOUSE_INFO = ['Жилая площадь','Площадь кухни','Высота потолков','Планировка','Санузел','Балкон/лоджия','Вид из окон','Ремонт','Год постройки','Тип дома','Аварийность','Парковка']

def create_h_dict(links):
    house_info_dict = {}
    house_info_dict['id'] = [0 for i in range(len(links))]
    for item in HOUSE_INFO:
        house_info_dict[item] = [None for i in range(len(links))]
    return(house_info_dict)

def get_house_info(soup,house_info_dict,i,about_flat_info,about_flat_type_info):
    len_home_info = len(soup.select('div[data-name="OfferSummaryInfoItem"]'))
    temp_info_dict = {}
    for h in range(len_home_info):
        type_info = soup.select('div[data-name="OfferSummaryInfoItem"]')[h].find('p', class_ = about_flat_type_info).text
        info = soup.select('div[data-name="OfferSummaryInfoItem"]')[h].find('p', class_ = about_flat_info).text
        if info != 'Нет информации' and type_info != 'Общая площадь':
            if type_info == 'Высота потолков':
                 if info.find(',') != -1:
                    info = info[0] + '.' + info[2]
                 else:
                     info = info[0]
            if type_info in ['Жилая площадь','Площадь кухни']:
                info = info.replace(',','.')
            if type_info == 'Санузел':
                 if info.find(',') != -1:
                    toilet = info.split(',')
                    info = int(toilet[0][0]) + int(toilet[1][1])
                 else:
                    info = int(info[0])
            temp_info_dict[type_info] = info
        # print('{}: {}'.format(type_info,info))
    for key in list(temp_info_dict.keys()):
            if key in HOUSE_INFO:
                house_info_dict[key][i] = temp_info_dict[key]

#color2 Features                          
FEATURES = ['Холодильник','Стиральная машина','Телевизор','Ванна','Мебель на кухне','Посудомоечная машина','Кондиционер','Интернет','Душевая кабина','Мебель в комнатах']

def create_f_dict(links):
    features_dict = {}
    features_dict['id'] = [0 for i in range(len(links))]
    for item in FEATURES:
        features_dict[item] = [0 for i in range(len(links))]
    return(features_dict)

def get_features(soup,features_dict,i):
    features = soup.select('div[data-name="FeaturesItem"]')
    for f in features:
        features_dict[f.text][i] = 1

#color2 photos                     
def get_photos(soup, id_,scraper):
    photos = soup.select('img[data-name="ThumbComponent"]')
    len_photos = len(photos)
    if len_photos > 10:
        len_photos = 10
    for i in trange(len_photos, desc= 'photos', colour= 'CYAN'):
        ph_link = photos[i].get('src')
        ph_link = ph_link[:-5] + '1' +ph_link[-4:]
        for i in range(5):
            try:
                r = scraper.get(ph_link)
                im = Image.open(BytesIO(r.content))
                im = im.resize((300,300), Image.LANCZOS)
                im.save('data/photos/{}_{}.jpg'.format(id_,i))
            except ConnectionError:
                time.sleep(3)
                pass
        # im = Image.open(BytesIO(r.content))
        # im = im.resize((300,300), Image.LANCZOS)
        # im.save('photos/{}_{}.jpg'.format(id_,i))
        rnd = 3*random.random()
        time.sleep(5+rnd)

#color2 DFS                              
def create_new_df(data):
    df2 = pd.DataFrame(data)
    df2['underground'] = df2['underground'].apply(lambda x: None if x == '' else x)
    df2 = df2.drop(['author','author_type','deal_type','commissions','accommodation_type'],axis = 1)
    try:
        df2 = df2.drop('residential_complex', axis = 1)
    except KeyError:
        pass
    return(df2)

def get_old_df(LOCATION,ROOM):
    if LOCATION == 'Ленобласть':
        city = 'LEN_OBL'
    else:
        city = 'SPB'
    df_old = pd.read_csv('data/cian_data_r_{}_c_{}.csv'.format(ROOM,city),index_col=0)
    return(df_old,city)

def update_dfs(df_old,df2):
    links = df2['link']
    links_to_drop = []
    curr_time = datetime.now(pytz.timezone('Europe/Moscow')).strftime("%d/%m/%Y %H:%M")
    for i in range(len(links)):
        url = links[i]
        old_links = list(df_old['link'])
        if url in old_links:
            if df_old[df_old['link'] == url]['price_per_month'].item() == df2['price_per_month'][i].item():
                df_old.loc[df_old['link'] == url,'time_parse'] = curr_time
                links_to_drop.append(url)
            else: 
                df_old = df_old.drop(df_old[df_old['link'] == url].index, axis = 0).reset_index(drop = True)
    df2 = df2.drop(df2[df2['link'].isin(links_to_drop)].index, axis = 0).reset_index(drop = True)
    print('Объявлений уже в данных: {}'.format(len(links_to_drop)))
    return df_old, df2
