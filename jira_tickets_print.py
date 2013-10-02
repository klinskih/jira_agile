# -*- coding: utf-8 -*-
import contextlib
import urllib
import urllib2
from lxml import etree
from xml.dom.minidom import *
from quik import FileLoader
__author__ = 'kag'
class ApiClient(object):
    def __init__(self, srv_address='http://10.90.90.10', login='kag', password='123'):
        self.srv_address = srv_address
        self.login = login
        self.password = password
        self.cookie = None
        self.cookies = urllib2.HTTPCookieProcessor()
        self.opener = urllib2.build_opener(self.cookies)
        urllib2.install_opener(self.opener)

    def make_login(self):
        login_url = "%s/secure/Dashboard.jspa" % self.srv_address
        self.opener.open(login_url)

        #try:
        #token = [x.value for x in self.cookies.cookiejar if x.name == 'atl_token'][0]
        #except IndexError:
        #    return False, "no csrftoken"

        params = dict(os_username=self.login, os_password=self.password, \
                      this_is_the_login_form=True,
                      )
        encoded_params = urllib.urlencode(params)

        with contextlib.closing(self.opener.open(login_url, encoded_params)) as f:
            html = f.read()
            print html

    def call_api(self, api_url):
        auth_params={
            'os_username':self.login,
            'os_password':self.password
        }
        encoded_params = urllib.urlencode(auth_params)
        api_url = "%s/%s&%s" % (self.srv_address, api_url, encoded_params)
        with contextlib.closing(self.opener.open(api_url)) as f:
            xml = parseString(f.read())
            return xml
if __name__ == '__main__':
    client = ApiClient()
    xml_doc=client.call_api('sr/jira.issueviews:searchrequest-xml/10280/SearchRequest-10280.xml?tempMax=1000')
    tickets = xml_doc.getElementsByTagName('item')
    print_fields=['title','description','assignee','reporter','fixVersion']
    c={'tickets':[]}
    for ticket in tickets:
        print_params={}
        for field in print_fields:
            for f in ticket.getElementsByTagName(field):
                for node in f.childNodes:
                    print_params[field]=node.nodeValue
        c['tickets'].append(print_params)


    loader = FileLoader('')
    template = loader.load_template('tickets.html')
    f=open('result.html','w+')
    f.write(template.render(c,loader=loader).encode('utf-8'))
    f.close()
