import requests
import re
import time
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup

regions = ['AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA','HI','ID','IL','IN','IA','KS','KY','LA','ME','MD','MA','MI','MN','MS','MO','MT'\
            ,'NE','NV','NH','NJ','NM','NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VT','VA','WA','WV','WI','WY']
for region in regions:
     page = 1
     url = 'https://www.careerbuilder.com/jobs-machine-learning-engineer-in-'+region+'?page_number='+str(page)
     r = requests.get(url)
     status_code = r.status_code
     df_total = None
     soup = BeautifulSoup(r.content,'html.parser')
     page_count = int(re.findall(r'\d+',soup.find('div',attrs={'class','row bump pagination'}).find('span',attrs={'class':'page-count'}).\
                    get_text())[1])
     while status_code == 200:
          titles = []
          companies = []
          location_list = []
          for div in soup.find_all('div',attrs={'class':'job-row'}):
               title_div = div.h2
               if title_div is not None:
                    titles.append(title_div.get_text().strip())
               else:
                    titles.append('None')
               company_div = div.find('div',attrs={'class':'columns large-2 medium-3 small-12'})
               if company_div is not None:
                    a_div = company_div.a
                    if a_div is not None:
                         companies.append(a_div.get_text())
                    else:
                         companies.append('None')
               else:
                    companies.append('None')
               location_div = div.find('div',attrs={'class':'columns end large-2 medium-3 small-12'})
               if location_div is not None:
                   h4_div = location_div.h4
                   if h4_div is not None:
                       location_list.append(h4_div.get_text().strip().split(','))
                   else:
                       location_list.append('None, None, None')
               else:
                    location_list.append('None, None, None')
          locations = []
          for city_state_list in location_list:
               cities_states = []
               for city_state in city_state_list:
                   cities_states.append(' '.join(re.findall('[a-zA-Z]+',city_state)))
               locations.append(cities_states)
          for location in locations:
               try:
                    location.remove('')
               except:
                    pass
          cities = []
          states = []
          for location in locations:
               if len(location) == 1:
                   cities.append(location[0])
                   states.append(region)
               elif len(location) <= 3:
                    if location[-1] == 'USA':
                         cities.append(location[0])
                         states.append(region)
                    else:
                         cities.append(location[0])
                         states.append(location[1])
               else:
                    cities.append(location[1])
                    states.append(location[2])
          df = pd.DataFrame(np.array([titles,companies,cities,states]).T,columns=['Titles','Companies','Cities','States']).\
               drop_duplicates()
          df_ml = df[((df.Titles.str.contains('Data'))|(df.Titles.str.contains('Machine Learning'))|(df.Titles.str.contains('Analyst')))&(\
                    df.Companies != 'None')]
          if df_total is not None:
               df_total = pd.concat([df_total,df_ml],axis=0).drop_duplicates()
          else:
               df_total = df_ml
          page += 1 
          if page == page_count+1:
               break
          time.sleep(10)
          url = 'https://www.careerbuilder.com/jobs-machine-learning-engineer-in-'+region+'?page_number='+str(page)
          r = requests.get(url)
          status_code = r.status_code
          soup = BeautifulSoup(r.content,'html.parser')       
     idx = pd.Index(range(len(df_total))).unique()
     df = pd.DataFrame(df_total.values,columns=list(df_total.columns),index=idx)
     df.to_json(region+'_jobs.json')