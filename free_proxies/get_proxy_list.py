import requests as req
from bs4 import BeautifulSoup
import time,json,re,os,sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


driver_path=os.path.join(os.getcwd(),"chromedriver")
options = webdriver.ChromeOptions()
prefs={"profile.managed_default_content_settings.images": 2, 'disk-cache-size': 4096 }
options.add_experimental_option('prefs', prefs)
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')
##This one is another hub for getting fresh proxies every 15 minutes
#url='https://raw.githubusercontent.com/fate0/proxylist/master/proxy.list'
def extract_free_proxies(url):
	r = req.get(url)
	if r.status_code == 200:
		json_raw_data = r.content.split(b'\n')
		for item in json_raw_data:
			item = item.decode('utf-8')
			if item:
				j = json.loads(item)
				ip = j['host']
				port = j['port']
				proxy_type = j['type']
	else:
		print("Invalid URL!!")
url1='https://www.proxydocker.com/en/proxylist/search?type=http&anonymity=ELITE&port=8080&country=all&city=&state=all&need=all'
url2='https://www.proxydocker.com/en/proxylist/search?type=http&anonymity=ELITE&port=8080&country=India&city=&state=all&need=all'

EMAIL="priyanshagarwal02may@gmail.com"
PASSWORD="freeproxy"

def scrape_proxies(url,debug=False,max_proxies=100):
	all_proxies=[]
	driver = webdriver.Chrome(executable_path =driver_path, chrome_options=options)
	driver.get(url)
	if driver.find_elements_by_link_text('Log in'):
		driver.find_elements_by_link_text('Log in')[0].click()
		username = driver.find_element_by_id("username")
		username.clear()
		username.send_keys(EMAIL)
		password = driver.find_element_by_id("password")
		password.clear()
		password.send_keys(PASSWORD)
		driver.find_element_by_xpath('//*[@id="login-dp"]/li/div/div/form/fieldset/button').click()
	total_pages = int(driver.find_element_by_xpath('//*[@id="page_span"]').text.split("/")[1].replace(")",""))
	curr_page_num = int(driver.find_element_by_xpath('//*[@id="page_span"]').text.split("/")[0].replace("(",""))
	cnt=0
	flag=0
	while curr_page_num<=total_pages:
		page_limit = len(driver.find_elements_by_xpath('//*[@id="proxylist_table"]/tr')) # maximum number of pages on one webpage
		proxylist=[]
		curr_cnt=0
		for i in range(1,page_limit+1):
			temp={}
			try:
				temp["address"] = driver.find_element_by_xpath("//table/tbody/tr["+str(i)+"]/td[1]").text.strip()
				temp["protocol"] =driver.find_element_by_xpath("//table/tbody/tr["+str(i)+"]/td[2]").text.lower().strip()
			except:
				print("ERROR OCCUR!!, Quitting the driver....")
				driver.quit()
			proxylist.append(temp)
			curr_cnt=len(proxylist)
			#print(curr_cnt,cnt)
			if cnt+curr_cnt==max_proxies:
				#print("lol")
				flag=1
				break
		if debug:
			page_num = int(driver.find_element_by_xpath('//*[@id="page_span"]').text.split("/")[0].replace("(",""))
			print("Number of proxy address on page",": ",page_num," is --> ",len(proxylist))
			print(proxylist,"\n\n")
		all_proxies+=proxylist
		if flag:
			print("Max. Proxies limit reached!!, Quitting the driver...")
			break
		if curr_page_num!=total_pages:
			try:
				driver.find_element_by_link_text('Next page').click()
				time.sleep(0.5)
			except:
				print("ERROR OCCUR!!, Quitting the driver...")
				driver.quit()
		curr_page_num+=1
		cnt=len(all_proxies)
	driver.quit()
	return all_proxies
proxylist = scrape_proxies(url2,debug=True)
print("Retrieved No. of proxies: ",len(proxylist))