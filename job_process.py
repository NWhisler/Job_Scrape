import pandas as pd 
import numpy as np 
import os 
import re

job_sites = ['Indeed','Monster','CareerBuilder']
df_total = None
for site in job_sites:
	files = os.listdir('./'+site+'/jobs')
	for file in files:
		df = pd.read_json('./'+site+'/jobs/'+file)
		if df_total is not None:
			df_total = pd.concat([df_total,df],axis=0)
		else:
			df_total = df 
states = [re.split('\_',file)[0] for file in files]
idx = pd.Index(range(len(df_total))).unique()
df = pd.DataFrame(df_total.values,columns=list(df_total.columns),index=idx).drop_duplicates()
# city_states = {'Arizona':'AZ','California':'CA','Georgia':'GA','Illinois':'IL','Maryland':'MD','Massachusetts':'MA','New York State':\
# 				'NY','North Carolina':'NC','Virginia':'VA'}
# for state in list(city_states.keys()):
# 	df.iloc[df[df.Cities==state].index] = city_states[state]
top_companies = []
idx_state = {}
for state in states:
	df_state = df_total[df_total.States==state]
	companies = df_state.Companies.values
	cities = df_state.Cities.values
	company_location_count = {}
	company_state_count = {}
	jobs_city_count = {}
	city_company_job_count = {}
	for company in zip(companies,cities):
		company_location_count[company] = 1 + company_location_count.get(company,0)
	for company in companies:
		company_state_count[company] = 1 + company_state_count.get(company,0)
	for city in cities:
		jobs_city_count[city] = 1 + jobs_city_count.get(city,0)
	jobs = 0
	for company,count in company_location_count.items():
		city_company_job_count[company[1]] = []
	for company,count in company_location_count.items():
		city_company_job_count[company[1]].append((company[0],count))
		if count > jobs:
			jobs = count
			top_company = company
	company_state_jobs = 0
	for company,count in company_state_count.items():
		if count > company_state_jobs:
			company_state_jobs = count
			top_company_state = company
	city_state_jobs = 0
	for city,count in jobs_city_count.items():
		if count > city_state_jobs:
			city_state_jobs = count
			city_state = city
	idx_state[state] = [company_location_count,company_state_count,jobs_city_count,city_company_job_count]
	print('State: ',state)
	print('# of jobs: ',len(df_state))
	print('\n')
	print('Company w/ largest # of jobs: ',top_company_state)
	print('# of jobs: ',company_state_jobs)
	print('\n')
	print('Company w/ largest # of jobs in city: ',top_company[0])
	print('City: ',top_company[1])
	print('# of jobs: ',jobs)
	print('\n')
	print('City w/ largest # of jobs: ',city_state)
	print('# of jobs: ',city_state_jobs)
	print('-'*50)
while True:
	search = input('Search for a city? ')
	print('\n')
	if search == 'Y' or search == 'y':
		print('States: ')
		print('\n')
		for state in states:
			print(state,end=', ')
		print('\n')
		state_search = input('State ')
		print('\n')
		print('Cities: ')
		print('\n')
		try:
			for city in list(idx_state[state_search][2].keys()):
				print(city,end=', ')
		except:
			state_search = input('State ')
			print('\n')
			for city in list(idx_state[state_search][2].keys()):
				print(city,end=', ')
		print('\n')
		city_search = input('City: ')
		print('\n')
		try:
			print('# of jobs',idx_state[state_search][2][city_search])
		except:
			city_search = input('City: ')
			print('\n')
			print('# of jobs',idx_state[state_search][2][city_search])
		print('\n')
		print('Employers: ')
		print('\n')
		companies = []
		jobs = []
		for company in idx_state[state_search][3][city_search]:
			companies.append(company[0])
			jobs.append(company[1])
		companies = np.array(companies)
		jobs = np.array(jobs)
		index = np.argsort(jobs)
		for idx in index:
			print('Company: ',companies[idx])
			print('# of jobs: ',jobs[idx])
			print('\n')
	else:
		break