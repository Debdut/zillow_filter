#!/usr/bin/env python

from lxml import html, etree
from lxml.html.clean import clean_html
import requests
import sys
import os
import zipcode
import re

HEADER = {'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:51.0) Gecko/20100101 Firefox/51.0'}

def get_all_buy_li (zcode):

    if zipcode.isequal(str(zcode)) == None:
        return None
    req_url = 'https://www.zillow.com/homes/for_sale/'+str(zcode)+'_rb/'
    page = requests.get (req_url, headers=HEADER)
    tree = html.fromstring (page.content)

    list_li = tree.xpath ('/html/body/div[@class="main-wrapper " and @id="wrapper"]/div[@class="search-content-container" and @id="container"]/div[@class="active-view"]/div[@id="c-column"]/div[@id="inner-c-column"]/div[@id="list-container-column"]/div[@class="active-view"]/div[@id="list-results-container"]/div[@id="list-container"]/div[@id="inner-list-container"]/div[@id="list-core-content-container"]/div[@id="list-results"]/div[@id="search-results"]/ul[@class="photo-cards"]/li')

    total_page = int (tree.xpath ('//ol[@class="zsg-pagination"]/li')[-2].getchildren()[0].text)
    for page_num in range (2,total_page+1):
        req_url = 'https://www.zillow.com/homes/for_sale/'+str(zcode)+'_rb/'+str(page_num)+'_p/'
        page = requests.get (req_url, headers=HEADER)
        tree = html.fromstring (page.content)
        list_li += tree.xpath ('/html/body/div[@class="main-wrapper " and @id="wrapper"]/div[@class="search-content-container" and @id="container"]/div[@class="active-view"]/div[@id="c-column"]/div[@id="inner-c-column"]/div[@id="list-container-column"]/div[@class="active-view"]/div[@id="list-results-container"]/div[@id="list-container"]/div[@id="inner-list-container"]/div[@id="list-core-content-container"]/div[@id="list-results"]/div[@id="search-results"]/ul[@class="photo-cards"]/li')

    return list_li


def get_all_zpid_price_zestimate (zcode, api_key):

    list_data = []
    for li_root in get_all_buy_li(zcode):

        link = 'zillow.com' + li_root.getchildren ()[0].getchildren ()[0].getchildren ()[3].attrib['href']
        zpid = str(li_root.getchildren ()[0].attrib['id'])[5:]
        if li_root.getchildren()[0].getchildren()[0].getchildren()[2].getchildren()[1].getchildren()[0].text[0] == '$':
            price = li_root.getchildren()[0].getchildren()[0].getchildren()[2].getchildren()[1].getchildren()[0].text[1:].replace(',', '')
            if price[-1] == 'K':
                price = int(price[:-1])*1000
            else:
                price = int(re.sub("[^0-9]", "", price))
        else:
            price = None

        zestimate = get_zestimate (zpid, api_key)

        if price != None and zestimate != None:
            list_data.append ([zpid, price, int(zestimate), link])

    list_data.sort (key=lambda x: (-x[2]+x[1])*1.00/x[1])

    return list_data


def get_zestimate (zpid, api_key):

    req_url = 'http://www.zillow.com/webservice/GetZestimate.htm?zws-id='+api_key+'&zpid='+str(zpid)
    xml = requests.get (req_url, headers=HEADER)
    tree = etree.fromstring (xml.content)

    if tree.xpath('//message/code')[0].text != '0':
        return None

    zestimate = tree.xpath ('//zestimate/amount')[0].text
    return zestimate

def creat_html (zipcode, api_key):

    html_str = ''
    with open('templates/output.html', 'r') as f:
        for line in f:
            html_str += line

    list_data = get_all_zpid_price_zestimate (zipcode, api_key)
    for data in list_data:
        html_str += '<li><a href="https://'+data[3]+'" target="_blank">'+data[3].split('/')[2]+' &emsp; $'+str(data[1])+' &emsp; $'+str(data[2])+' &emsp; '+str(int(-100*(-data[2]+data[1])/data[1]))+'%</a></li>\n'
    html_str += '</ul></div></body></html>'

    return html_str
