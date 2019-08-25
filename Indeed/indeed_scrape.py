import pandas as pd
import numpy as np 
import requests
import time
import re
from bs4 import BeautifulSoup

regions = ['NH','NJ','NM','NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VT','VA','WA','WV','WI','WY']
url = 'https://www.indeed.com/jobs?q=machine+learning+engineer&l='
for region in regions:
	df_total = None
	previous_titles = []
	page = 0
	r = requests.get(url+region+'&start='+str(page))
	status_code = r.status_code
	soup = BeautifulSoup(r.content,'html.parser')
	while status_code == 200:
		titles = []
		locations = []
		companies = []
		for div in soup.find_all('div',attrs={'class':'title'}):
				titles.append(div.get_text().strip())
		for div in soup.find_all('div',attrs={'class':'sjcl'}):
			if div.find('span',attrs={'class':'location'}) is not None:
				locations.append(div.find('span',attrs={'class':'location'}).get_text())
			elif div.find('div',attrs={'class':'location'}) is not None:
					locations.append(div.find('div',attrs={'class':'location'}).get_text())
			else:
				locations.append('None,None')
			if div.find('span',attrs={'class':'company'}) is not None:
				companies.append(div.find('span',attrs={'class':'company'}).get_text().strip())
			else:
				companies.append('None')
		location = [re.split('\,',location) for location in locations]
		cities = np.array([city[0] for city in location])
		states = []
		for state in location:
			if len(state) > 1:
				states.append(re.search('\w+',state[1]).group(0))
			else:
				states.append('None')
		titles = np.array(titles)
		companies = np.array(companies)
		df = pd.DataFrame(np.vstack([titles,companies,cities,states]).T,columns=['Titles','Companies','Cities','States']).drop_duplicates()
		if list(df.Titles.values) == list(previous_titles):
			break
		else:
			previous_titles = df.Titles.values
		if df_total is not None:
			df_total = pd.concat([df_total,df],axis=0).drop_duplicates()
		else:
			df_total = df
		page += 10
		time.sleep(10)
		r = requests.get(url+region+'&start='+str(page))
		status_code = r.status_code
		soup = BeautifulSoup(r.content,'html.parser')
	idx = pd.Index(range(len(df_total))).unique()
	df_total = pd.DataFrame(df_total.values,columns=list(df_total.columns),index=idx)
	df_total.to_json(region+'_'+'jobs.json')