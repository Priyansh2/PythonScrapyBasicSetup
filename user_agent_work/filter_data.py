import os,sys,re,json
from collections import Counter,defaultdict
data1 = open("user_agents.txt","r").read().split("\n")
#print(len(data1))
data1_user_agents=list(set(data1))
data2 = json.load(open("user-agents.json","r"))
#print(len(data2))
data2_user_agents=[]
for item in data2:
	try:
		ua  = item['userAgent']
		data1_user_agents.append(ua)
	except:
		print(item)
#=[item["userAgent"] for item in data2]
data1_user_agents.extend(data1_user_agents)
filterd_user_agents = sorted(list(set(data1_user_agents)))
print(len(filterd_user_agents))
fd = open("filtered_ua.txt","w")
for ua in filterd_user_agents:
	ua = ua.strip()
	if ua:
		fd.write(ua+"\n")
fd.close()
