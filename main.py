import requests
from bs4 import BeautifulSoup
import pandas as pd
import gspread
from df2gspread import df2gspread as d2g
from oauth2client.service_account import ServiceAccountCredentials
from requests_ip_rotator import ApiGateway, EXTRA_REGIONS
from lxml.html import fromstring
from itertools import cycle
import traceback


pd.set_option('display.max_columns', None)  # or 1000
pd.set_option('display.max_rows', None)  # or 1000

df_links = pd.read_excel("/Users/amit/Documents/bid_bot/data/links.xlsx")

column_names = ["Sr. No.","e-Published Date", "Closing Date", "Opening Date","Title and Ref.No./Tender ID","Organisation Chain"]

data = pd.DataFrame(columns = column_names)

url_main ="https://eprocure.gov.in/eprocure/app?page=FrontEndTendersByOrganisation&service=page"

initial_url =  "https://eprocure.gov.in/"


"""
def get_proxies():
	url = 'https://free-proxy-list.net/'
	response = requests.get(url)
	parser = fromstring(response.text)
	proxies = set()
	for i in parser.xpath('//tbody/tr')[:10]:
		if i.xpath('.//td[7][contains(text(),"yes")]'):
			#Grabbing IP and corresponding PORT
			proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
			proxies.add(proxy)
	return proxies
//*[@id="list"]/div/div[2]/div/table/tbody/tr[1]/td[1]
proxies = get_proxies()
print(proxies)

proxies = ["80.48.119.28:8080", "133.18.227.47:8080", "207.46.237.37:8000", "170.245.164.34:999", "51.15.242.202:8888", "20.210.113.32:8123",
"165.154.236.59:80"
,"165.154.235.178:80"
,"165.154.235.156:80"
,"219.78.228.211:80"
,"8.219.97.248:80"]
####@@@@
proxy_pool = cycle(proxies)
for i in range(1,11):
#Get a proxy from the pool
	proxy = next(proxy_pool)
	print("Request #%d"%i)
	try:
		response = requests.get(url_main,proxies={"http": proxy, "https": proxy})
		print(response.json())
	except:
	#Most free proxies will often get connection errors. You will have retry the entire request using another proxy to work. 
	#We will just skip retries as its beyond the scope of this tutorial and we are only downloading a single url 
		print("Skipping. Connnection error")
####$$$$$


"""
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0'
}
s=requests.Session()
s.proxies = {"https": "80.48.119.28:8080"}


def parser(url):
	global s
	page = s.get(url ,headers=headers)
	soup = BeautifulSoup(page.text, 'html.parser')
	links = soup.find_all('a', class_='link2', href= True)

	print(soup)
"""

	for i in links:
		#print(i)
		page_result = s.get(initial_url + i['href'], headers=headers)
		#print(page_result.text)
		soup_result = BeautifulSoup(page_result.text, 'html.parser')
		#print(soup_result)
		full_list = []
		for i in soup_result.find_all('tr', class_=['odd','even']):
			for j in i.find_all('td'):
				full_list.append(j.text)
		chunks = [full_list[x:x+6] for x in range(0, len(full_list), 6)]
		print(chunks)

		df = pd.DataFrame(chunks, columns=column_names)
		#df = df.iloc[: , 1:]
		data = data.append(df)
		data = data.drop('Sr. No.', axis = 1)
		print("complete")
	print("google writing started")

	scope = ['https://spreadsheets.google.com/feeds',
	         'https://www.googleapis.com/auth/drive']
	credentials = ServiceAccountCredentials.from_json_keyfile_name(
	    'jsonFileFromGoogle.json', scope)
	gc = gspread.authorize(credentials)

	spreadsheet_key = '1IS6eszS0GVv1Ia2iMieDtjsTn0bK1JspPAXrnR3zdIk'
	wks_name = 'Sheet1'
	d2g.upload(data, spreadsheet_key, wks_name, credentials=credentials, row_names=True)
"""


parser(url_main)

















