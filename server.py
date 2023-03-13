import requests
from requests.adapters import HTTPAdapter, Retry
from bs4 import BeautifulSoup
import pandas as pd
import gspread
from df2gspread import df2gspread as d2g
from oauth2client.service_account import ServiceAccountCredentials
import datetime


start = datetime.datetime.now()
print("Start Time:\n")
print(start.strftime("%H:%M:%S"))

pd.set_option('display.max_columns', None)  # or 1000
pd.set_option('display.max_rows', None)  # or 1000

url_main ="https://etenders.hry.nic.in/nicgep/app?page=FrontEndTendersByOrganisation&service=page"
initial_url =  "https://etenders.hry.nic.in"
column_names = ["Sr. No.","e-Published Date", "Closing Date", "Opening Date","Title and Ref.No./Tender ID","Organisation Chain"]
column_names_2 = ["Sr. No.","e-Published Date", "Closing Date", "Opening Date","Title and Ref.No./Tender ID","Organisation Chain","Region"]

data = pd.DataFrame(columns = column_names_2)
restart="/eprocure/app?service=restart"
df_links = pd.read_excel("data/links.xlsx")
df_links = df_links.drop(index=14)



s=requests.Session()
s.cookies.clear()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
s.mount('http://', adapter)
s.mount('https://', adapter)
#s.mount(initial_url+restart)




def parser(url,reg):
	global data, s
	page = s.get(url)
	soup = BeautifulSoup(page.text, 'html.parser')
	links = soup.find_all('a', class_='link2', href= True)
	print("\n")
	print(reg+' Start')
	for i in links:
		#print(i)
		page_result = s.get(url.rsplit('/', 2)[0] + i['href'])
		#print(page_result.text)
		soup_result = BeautifulSoup(page_result.text, 'html.parser')
		#print(soup_result)
		full_list = []
		ten_list = []
		for i in soup_result.find_all('tr', class_=['odd','even']):
			for j in i.find_all('td'):
				full_list.append(j.text)
		chunks = [full_list[x:x+6] for x in range(0, len(full_list), 6)]
		#print(chunks)
		for i in soup_result.find_all('tr', class_=['odd','even']):
			b = i.find('a',href=True)
			c = b['href'].replace("&session=T","")
			d =  url.rsplit('/', 2)[0] + c
			ten_list.append(d)


		df = pd.DataFrame(chunks, columns=column_names)
		df = df.assign(Region=reg)
		df['Tender Details'] = ten_list
		#df = df.iloc[: , 1:]
		data = data.append(df, ignore_index=True)
		#print(data.tail(3))
	data = data.drop('Sr. No.', axis = 1)
	data = data[["Region","e-Published Date", "Closing Date", "Opening Date","Title and Ref.No./Tender ID","Organisation Chain","Tender Details"]]
	print(reg+ " completed")
	return data



def Gwriter(to_write):
	print("writing")
	scope = ['https://spreadsheets.google.com/feeds',
	         'https://www.googleapis.com/auth/drive']
	credentials = ServiceAccountCredentials.from_json_keyfile_name(
	    'jsonFileFromGoogle.json', scope)
	gc = gspread.authorize(credentials)

	spreadsheet_key = '1IS6eszS0GVv1Ia2iMieDtjsTn0bK1JspPAXrnR3zdIk'
	wks_name = 'Sheet1'
	d2g.upload(to_write, spreadsheet_key, wks_name, credentials=credentials,col_names=True, row_names=True)




for i, j in df_links.itertuples(index=False):
	try:
		parser(j,i)
	except:
		pass

print('\nParser Ready\n')


temp_list=[]
for i in data['Title and Ref.No./Tender ID']:
	if 'Consultancy' in i:
		temp_list.append('Consultancy')

	elif 'consultant' in i:
		temp_list.append('Consultancy')

	elif "Consultant" in i:
		temp_list.append('Consultancy')

	elif "consultancy" in i:
		temp_list.append('Consultancy')	
	
	elif "CONSULTANT" in i:
		temp_list.append('Consultancy')	

	elif "CONSULTANCY" in i:
		temp_list.append('Consultancy')	
	else:
		temp_list.append('Others')


print('\nPreparing tender type\n')

data['Tender Type'] = temp_list
print('\ndata completed\n')

data.to_excel("output.xlsx")

print("data written to file")
print(data.head())
End = datetime.datetime.now()
print("End Time:\n")
print(End.strftime("%H:%M:%S"))
"""

data_2= pd.read_excel("output.xlsx")
data_2 = data_2.drop(labels='Unnamed: 0',axis=1)
data_2 =data_2[["Region","e-Published Date", "Closing Date", "Opening Date","Title and Ref.No./Tender ID","Organisation Chain","Tender Type" ,"Tender Details"]]
data_2 = data_2.loc[data_2['Tender Type'] == 'Consultancy']
data_2=data_2.reset_index(drop=True)
print(data_2.head())
print("writing to G")
Gwriter(data_2)
print('\nAllcompleted\n')

End = datetime.datetime.now()
print("End Time:\n")
print(End.strftime("%H:%M:%S"))

"""






