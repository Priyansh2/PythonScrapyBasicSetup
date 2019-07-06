# -*- coding: utf-8 -*-
import pdb
import scrapy
import requests as req
from bs4 import BeautifulSoup
import time

class WhatismybrowserSpider(scrapy.Spider):
	name = 'whatismybrowser'
	allowed_domains = ['developers.whatismybrowser.com']
	def scrape_urls(self,url,prefix_url):
		url_collection=[]
		r = req.get(url)
		if r.status_code == 200:
			soup = BeautifulSoup(r.content,'html.parser')
		else:
			soup = False
		if soup:
			table = soup.find('tbody')
			tds = table.findAll('a',{'class':'maybe-long'})
			for td in tds:
				software_name = td.text.strip()
				url_collection.append(prefix_url+td['href'])
		else:
			print("Invalid Url!!")
		return url_collection

	def start_requests(self):
		# Only chrome, firefox, opera, safari and internet explorer are supported
		# More browsers could be found at:
		# https://developers.whatismybrowser.com/useragents/explore/software_name/
		'''common_browsers_links = [
			'https://developers.whatismybrowser.com/useragents/explore/software_name/chrome/',
			'https://developers.whatismybrowser.com/useragents/explore/software_name/firefox/',
			'https://developers.whatismybrowser.com/useragents/explore/software_name/opera/',
			'https://developers.whatismybrowser.com/useragents/explore/software_name/safari/',
			'https://developers.whatismybrowser.com/useragents/explore/software_name/internet-explorer/'
		]'''
		base_url='https://developers.whatismybrowser.com/useragents/explore/software_name/'
		prefix_url='https://developers.whatismybrowser.com'
		common_browsers_links = self.scrape_urls(base_url,prefix_url)

		for link in common_browsers_links:
			yield scrapy.http.Request(link)

	def parse(self, response):
		#max_page = getattr(self, 'max_page', 100000000000000)
		ua_elems = response.xpath('.//table[contains(@class, "table-useragents")]/tbody/tr/td[contains(@class, "useragent")]/a')
		for ua_elem in ua_elems:
			try:
				ua = ua_elem.xpath('./text()').extract_first().strip()
				#self.logger.debug('[UserAgent] %s', ua)
				yield {'user_agent_string': ua.strip('"')}
			except Exception as e:
				self.logger.exception(e)

		next_page_elem = response.xpath('.//div[@id="pagination"]/span[contains(@class, "current")]/following-sibling::a')
		if next_page_elem:
			next_page_elem = next_page_elem[0]
			#try:
				#page = int(next_page_elem.xpath('./text()').extract_first().strip())
			#except ValueError:
				#page+=1
			#if page < max_page:
			next_page_url = next_page_elem.xpath('./@href').extract_first().strip()
			if not next_page_url.startswith('http'):
				next_page_url = 'https://developers.whatismybrowser.com' + next_page_url
			yield scrapy.http.Request(next_page_url)
