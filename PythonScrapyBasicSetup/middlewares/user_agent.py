import random
from xml.dom import minidom
from scrapy.utils.project import get_project_settings
import os
class RandomUserAgentMiddleware(object):
    settings = get_project_settings()
    script_path=os.path.dirname(os.path.realpath(__file__))

    source_path = script_path[0:len(script_path)-11]+'data/user_agents.xml'

    def __init__(self, *args, **kwargs):
        xmldoc = minidom.parse(self.source_path)
        items = xmldoc.getElementsByTagName('useragent')
        user_agents = [item.attributes['value'].value for item in items]

        self.settings.set('USER_AGENT_LIST', user_agents)

    def process_request(self, request, spider):
        user_agent = random.choice(self.settings.get('USER_AGENT_LIST'))
        if user_agent:
            request.headers.setdefault('User-Agent', user_agent)
