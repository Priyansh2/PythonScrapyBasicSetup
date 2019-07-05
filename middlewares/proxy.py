import random
import logging
import requests as req
import time,json,re,os,sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from stem import Signal
from stem.control import Controller
from bs4 import BeautifulSoup
from scrapy.utils.project import get_project_settings
try:
	from urllib.request import urlopen
except ImportError:
	from urllib2 import urlopen

driver_path=os.path.join(os.getcwd(),"chromedriver")
#print(driver_path)
chrome_options = webdriver.ChromeOptions()
prefs={"profile.managed_default_content_settings.images": 2, 'disk-cache-size': 4096 }
chrome_options.add_experimental_option('prefs', prefs)
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--incognito')
chrome_options.add_argument('--headless')
EMAIL="priyanshagarwal02may@gmail.com"
PASSWORD="freeproxy"

class TorProxyMiddleware(object):

	def __init__(self):
		self.import_settings()
		self.req_counter = 0

	def change_ip_address(self):
		with Controller.from_port(port=self.control_port) as controller:
			controller.authenticate(self.password)
			controller.signal(Signal.NEWNYM)
			controller.close()

	def import_settings(self):
		settings = get_project_settings()
		self.password = settings['AUTH_PASSWORD']
		self.http_proxy = settings['HTTP_PROXY']
		self.control_port = settings['CONTROL_PORT']
		self.max_req_per_ip = settings['MAX_REQ_PER_IP']

		self.exit_nodes = settings['EXIT_NODES']
		if self.exit_nodes:
			with Controller.from_port(port=self.control_port) as controller:
				controller.authenticate(self.password)
				controller.set_conf('ExitNodes', self.exit_nodes)
				controller.close()

	def process_request(self, request, spider):
		self.req_counter += 1
		if self.max_req_per_ip is not None and self.req_counter > self.max_req_per_ip:
			self.req_counter = 0
			self.change_ip_address()

		request.meta['proxy'] = self.http_proxy
		logging.info('Using proxy: %s', request.meta['proxy'])
		return None

class HttpProxyMiddleware(object):
	## old code. Need to be re-implemented because www.proxydocker.com is changing dynamically
	proxies = []
	max_proxies = 100
	source = {'port': 8080,
	'type': 'http',
	'url':'https://www.proxydocker.com/en/proxylist/search?type=%s&anonymity=ELITE&port=%d&country=all&city=&state=all&need=BOT'
	}
	def __init__(self):
		self.query_proxies()

	def _build_source_url(self):
		return self.source['url'] % (self.source['type'], self.source['port'])

	def query_proxies(self):
		driver = webdriver.Chrome(executable_path =driver_path, chrome_options=chrome_options)
		driver.get(self._build_source_url())
		debug=False
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
					#print("ERROR OCCUR!!, Quitting the driver....")
					driver.quit()
				proxylist.append(temp)
				curr_cnt=len(proxylist)
				if cnt+curr_cnt==self.max_proxies:
					flag=1
					break
			if debug:
				page_num = int(driver.find_element_by_xpath('//*[@id="page_span"]').text.split("/")[0].replace("(",""))
				print("Number of proxy address on page",": ",page_num," is --> ",len(proxylist))
				print(proxylist,"\n\n")
			self.proxies+=proxylist
			if flag:
				#print("Max. Proxies limit reached!!, Quitting the driver...")
				break
			if curr_page_num!=total_pages:
				try:
					driver.find_element_by_link_text('Next page').click()
					time.sleep(0.5)
				except:
					#print("ERROR OCCUR!!, Quitting the driver...")
					driver.quit()
			curr_page_num+=1
			cnt=len(self.proxies)
		driver.quit()
		'''request = urlopen(self._build_source_url())
		if request.getcode() == 200:
			i = 0
			soup = BeautifulSoup(request, 'html.parser')
			for row in soup.find_all('tr'):
				cells = row.findAll('td')
				if len(cells) > 2:
					self.proxies.append({'address': cells[0].text.strip(),'protocol': cells[1].text.lower().strip()})
					i += 1
					if i == self.max_proxies:
						break
		request.close()'''

	def process_request(self, request, spider):
		proxy = random.choice(self.proxies)
		request.meta['proxy'] = proxy['protocol'] + '://' + proxy['address']
		logging.info('Using proxy: %s', request.meta['proxy'])

	def remove_failed_proxy(self, request, spider):
		failed_proxy = request.meta['proxy']
		logging.log(logging.DEBUG, 'Removing failed proxy...')
		try:
			i = 0
			for proxy in self.proxies:
				if proxy['address'] in failed_proxy:
					del self.proxies[i]
					proxies_num = len(self.proxies)
					logging.log(logging.DEBUG,'Removed failed proxy <%s>, %d proxies left', failed_proxy, proxies_num)
					if proxies_num == 0:
						self.query_proxies()
					return True
				i += 1
		except KeyError:
			logging.log(logging.ERROR, 'Error while removing failed proxy')
		return False

	def process_exception(self, request, exception, spider):
		if self.remove_failed_proxy(request, spider):
			return request
		return None

	def process_response(self, request, response, spider):
		# really brutal filter
		if response.status == 200:
			return response
		return request
