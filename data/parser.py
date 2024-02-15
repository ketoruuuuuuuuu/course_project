from utils import *
import cianparser
import cloudscraper
from tqdm import tqdm
# from IPython import display
import os




ROOMS = ['studio',1,2,3,4,5]
# ROOMS = [1,2,3,4,5]
LOCATIONS = ['Санкт-Петербург','Ленобласть']
# LOCATIONS = ['Ленобласть']
ADD_SETTINGS = {'sort_by' :'creation_data_from_newer_to_older'}

def main():
    for LOCATION in LOCATIONS:
        for ROOM in ROOMS:
            for page in range(1,55): #55 MAX
                # display.clear_output(wait=False)
                os.system('cls')
                data = cianparser.parse(deal_type="rent_long",accommodation_type="flat",location=LOCATION,rooms=ROOM,additional_settings=ADD_SETTINGS,
                start_page=page,
                end_page=page)

                #скип цикла, если страницы кончились
                if len(data) == 0:
                    continue
                df2 = create_new_df(data)
                print('Найдено объявлений: {}'.format(len(df2)))
                df_old, city = get_old_df(LOCATION,ROOM)
                df_old, df2 = update_dfs(df_old,df2)    
                links = df2['link']
                print('Объявлений на обработку: {}'.format(len(links)))
                house_info_dict = create_h_dict(links)
                features_dict = create_f_dict(links)
                ids_ = []
                date_info = []
                time_parse = []

                for i in range(len(links)):
                    print('-'*20,'{} | {}'.format(ROOM,city),'-'*20) 
                    url = links[i]
                    print('{}/{} '.format(i+1,len(links)),url)
                    id_ = url.split('/')[-2]
                    ids_.append(id_)
                    #чтобы не лочили запросы
                    scraper = cloudscraper.create_scraper()
                    rnd_name = random.choice(['dasha','masha','tosha','sasha','vasya','kolya','anna','fedya','bob','mark','grisha'])
                    rnd_dig = random.randint(100,9000)
                    scraper.headers = {'Accept-Language': 'en','User-Agent': '{}{}@gmail.com'.format(rnd_name,rnd_dig)}
                    soup, satatus = parse_offer(scraper,url)
                    #скип цикла, если страница не алё
                    if satatus == 0:
                        date_info.append('0')
                        time_parse.append('0')
                        continue
                    with tqdm(total=3,desc = 'info', colour = 'CYAN') as pbar:
                        date_offer = get_date_of_post(soup)
                        date_info.append(date_offer)
                        time_parse.append(datetime.now(pytz.timezone('Europe/Moscow')).strftime("%d/%m/%Y %H:%M"))
                        pbar.update(1)
                        get_house_info(soup,house_info_dict,i,about_flat_info,about_flat_type_info)
                        house_info_dict['id'][i] = id_
                        pbar.update(1)
                        get_features(soup,features_dict,i)
                        features_dict['id'][i] = id_
                        pbar.update(1)
                    get_photos(soup,id_,scraper)
                    rnd = 3*random.random()
                    time.sleep(5+rnd)
                    
                
                df_h = pd.DataFrame(house_info_dict)
                df_f = pd.DataFrame(features_dict)
                df2.insert(0,'id',ids_)
                df2.insert(1,'time_post',date_info)
                df2.insert(2,'time_parse',time_parse)
                df3_j1 = df2.join(df_f.set_index('id'),on = 'id')
                df3_j2 = df3_j1.join(df_h.set_index('id'),on = 'id')
                df4 = pd.concat([df_old,df3_j2]).reset_index(drop = True)
                df4.to_csv('data/cian_data_r_{}_c_{}.csv'.format(ROOM,city))

if __name__ == '__main__':
    main()