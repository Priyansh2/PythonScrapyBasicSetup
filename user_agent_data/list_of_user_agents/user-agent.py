import requests as req
from bs4 import BeautifulSoup
import time

def getUa(br,url):
	#url = 'http://www.useragentstring.com/pages/useragentstring.php?name='+br
	r = req.get(url)
	if r.status_code == 200:
		soup = BeautifulSoup(r.content,'html.parser')
	else:
		soup = False
	if soup:
		div = soup.find('div',{'id':'liste'})
		lnk = div.findAll('a')
		if len(lnk)>0:
			print("No. of UA strings for ",br," : ",len(lnk))
			if len(br.split())>0:
				file="_".join(j.strip() for j in br.split())+'.txt'
			else:
				file = br+'.txt'
			f = open(file,"w")
			for ua in lnk:
				f.write(ua.text+'\n')
		#else:
			#print('no ua')
	#else:
		#print('No soup for '+br)

#lst = ['Firefox','Internet+Explorer','Opera','Safari','Chrome','Edge','Android+Webkit+Browser']
#for i in lst:
	#getUa(i)
	#time.sleep(20)
def retrieve_ua_links(url,allowed_br_list,disallowed_br_list):
	r = req.get(url)
	if r.status_code == 200:
		soup = BeautifulSoup(r.content,'html.parser')
	else:
		soup = False
	if soup:
		table = soup.find('table',{'id':'auswahl'})
		tds = table.findAll('td')
		br_td=None
		for td in tds:
			br_types = td.findAll('a',{'class':'unterMenuTitel'})
			for br_type in br_types:
				if br_type.text.strip() in allowed_br_list:
					br_td = td
					break
			if br_td:
				break
		if br_td:
			links = br_td.findAll('a')
			flag=1
			for link in links:
				if link.text.strip() in disallowed_br_list:
					flag=0
				elif link.text.strip() in allowed_br_list:
					if not flag:
						flag=1
				else:
					if flag:
						br = link.text.strip()
						url = 'http://www.useragentstring.com'+link['href']
						getUa(br,url)
						time.sleep(20)
		else:
			print("Not a suitable broser category!!")


allowed_br_list = ["BROWSERS","MOBILE BROWSERS"]
disallowed_br_list = ["CONSOLES","OFFLINE BROWSERS","E-MAIL CLIENTS"]
base_url='http://www.useragentstring.com/pages/useragentstring.php?'
retrieve_ua_links(base_url,allowed_br_list,disallowed_br_list)