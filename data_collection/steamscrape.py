# -*- coding: utf-8 -*-
"""
Created on Sat Sep 12 15:17:39 2015

@author: ryan
"""

__author__ = 'Ryan'
import requests
import json
from bs4 import BeautifulSoup
from pprint import pprint as pp
import re

def drink_steamy_soup(page_id):
    session = requests.session()
    print 'making request'
    html = session.get("http://store.steampowered.com/app/%s/" % page_id, timeout=1).text
    print 'finished request'
    # Checking if I'm in the check age page (just checking if the check age form is in the html code)
    if ('<form action="http://store.steampowered.com/agecheck/app/%s/"' % page_id) in html:
            print 'posting age'
            # I'm being redirected to check age page
            # let's confirm my age with a POST:
            post_data = {
                     'snr':'1_agecheck_agecheck__age-gate',
                     'ageDay':1,
                     'ageMonth':'January',
                     'ageYear':'1960'
            }
            html = session.post('http://store.steampowered.com/agecheck/app/%s/' % page_id, post_data).text   
    soup = BeautifulSoup(html, "lxml")
    print 'returing steamy soup'
    return soup, html
    
def extract_info_games(page_id):
    '''Created by "Curro" on StackExchange after a request for help
    by myself'''
    # Create session
    new_id = None
    soup,html = drink_steamy_soup(page_id)
    
    if soup.title.string == 'Welcome to Steam':
        error_result = 'redirected_to_main_page'
        game_name = None
        tag_data = None
        new_id = None
        
    else:
        page_links = soup.find_all('link')
#       OLD CODE        
#        for item in page_links:
#            if 'app' in item.attrs['href']:
#                html_id = item.attrs['href'].split('/')[5]
        #see if this works for everything
        canonical_link_loc = -2
        last_link_part = 4
        html_id = page_links[canonical_link_loc].attrs['href'].split('/')[last_link_part]
        print html_id
        if not page_id == html_id:
            new_id = html_id
            print 'redirecting'
            page_id = new_id
            soup, html = drink_steamy_soup(page_id)
            print 'successfully grabbed %s' % str(page_id)
        
        game_name = soup.find("div", "apphub_AppName").string
        
        # Extracting javscript object (a json like object)
        start_tag = 'InitAppTagModal( %s,' % page_id
        end_tag = '],'
        startIndex = html.find(start_tag) + len(start_tag)
        endIndex = html.find(end_tag, startIndex) + len(end_tag) - 1
        raw_data = html[startIndex:endIndex]
            
        tag_data = json.loads(raw_data)
        
        '''Metascore scrape'''
        ms_div = soup.find("div", id = 'game_area_metascore')
        meta_score_find = re.findall ( '<span>(.*?)</span>', str(ms_div), re.DOTALL)
        if meta_score_find:
            metascore = int(meta_score_find[0])
        else:
            metascore = None
        
        
        '''General Details'''
        mydivs = soup.findAll("div", { "class" : "details_block" })
        
        
        developer = re.findall( '<b>Developer:(.*?)</a>', str(mydivs), re.DOTALL)
        developer2 = developer[0].split('">')[-1]
        
        publisher = re.findall( '<b>Developer:(.*?)</a>', str(mydivs), re.DOTALL)
        publisher2 = publisher[0].split('">')[-1]
        
        release_date = re.findall( '<b>Release Date:</b>(.*?)<br/>', str(mydivs[0]), re.DOTALL)        
        
        error_result = None
        
        out_dict = { 'game_name': game_name,
                    'developer': developer2,
                    'publisher': publisher2,
                    'release_date': release_date,
                    'new_id': new_id,
                    'meta_score': metascore,
                    'tag_data': tag_data
                    }
                    
        hs_out  =  {'html': html,
                      'soup': soup}
    
    return out_dict, hs_out,error_result