import pandas as pd 
import numpy as np 
import requests
import re
import time
from bs4 import BeautifulSoup

regions = ['AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA','HI','ID','IL','IN','IA','KS','KY','LA','ME','MD','MA','MI','MN','MS','MO','MT'\
            ,'NE','NV','NH','NJ','NM','NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VT','VA','WA','WV','WI','WY']
for region in regions:
	titles = []
	companies = []
	locations = []
	url = 'https://www.monster.com/jobs/search/?q=machine-learning-engineer&where='+region+'&intcid=skr_navigation_nhpso_searchMain&stpage=\
		   1&page='
	page = 10
	r = requests.get(url+str(page))
	status_code = r.status_code
	soup = BeautifulSoup(r.content,'html.parser')
	jobs = int(re.search('\d+',soup.find('h2',attrs={'class':'figure'}).get_text()).group(0))
	pages = jobs//25
	df_total = None
	while status_code == 200:
		for div in soup.find_all('div',attrs={'class':'flex-row'}):
			title_div = div.find('h2',attrs={'class':'title'})
			if title_div is not None:
				a_div = title_div.find('a')
				if a_div is not None:
					titles.append(a_div.get_text())
				else:
					titles.append('None')
			else:
				titles.append('None')
			company_div = div.find('div',attrs={'class':'company'})
			if company_div is not None:
				span_div = company_div.find('span')
				if span_div is not None:
					companies.append(span_div.get_text())
				else:
					companies.append('None')
			else:
				companies.append('None')
			location_div = div.find('div',attrs={'class':'location'})
			if location_div is not None:
				span_div = location_div.find('span')
				if span_div is not None:
					locations.append(span_div.get_text())
				else:
					locations.append('None None')
			else:
				locations.append('None None')
		titles = [' '.join(re.findall('\w+',title)) for title in titles]
		locations = [' '.join(re.findall('\w+',location)) for location in locations]
		cities = [' '.join(location.split()[:-1]) for location in locations]
		states = [location.split()[-1] for location in locations]
		df = pd.DataFrame(np.array([titles,companies,cities,states]).T,columns=['Titles','Companies','Cities','States']).\
				drop_duplicates()
		df_ml = df[df.Titles.str.contains('Data')|df.Titles.str.contains('Machine Learning')|df.Titles.str.contains('Analyst')]
		if df_total is not None:
			df_total = pd.concat([df_total,df_ml],axis=0).drop_duplicates()
		else:
			df_total = df_ml
		page += 1
		if page == (pages+2):
			break
		time.sleep(10)
		r = requests.get(url+str(page))
		soup = BeautifulSoup(r.content,'html.parser')
		status_code = r.status_code
	idx = pd.Index(range(len(df_total))).unique()
	df = pd.DataFrame(df_total.values,columns=list(df_total.columns),index=idx)
	df.to_json(region+'_jobs.json')