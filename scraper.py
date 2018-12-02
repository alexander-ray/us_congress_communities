from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import glob
import json
import os
import re


def create_amendment_dict(base_url, party_lookup):
    try:
        ret = {'sponsor': {}, 'cosponsors': []}
        # https://stackoverflow.com/questions/13055208/
        header = {'User-Agent': 'Mozilla/5.0'}
        req = Request(base_url, headers=header)
        page = urlopen(req)
        soup = BeautifulSoup(page, 'lxml')

        sponsor_link = soup.find_all('table', class_='standard01')[0].find(text=re.compile('Sponsor:')).find_next().find('a')['href']

        assert sponsor_link is not None, 'Can\'t find link to sponsor'
        sponsor_id = sponsor_link.split('/')[-1]

        ret['sponsor']['bioguide_id'] = sponsor_id
        if sponsor_id in party_lookup:
            ret['sponsor']['name'] = party_lookup[sponsor_id]['name']
            ret['sponsor']['state'] = party_lookup[sponsor_id]['state']
        else:
            text = soup.find_all('table', class_='standard01')[0].find(text=re.compile('Sponsor:')).find_next().text.split()
            ret['sponsor']['name'] = text[2] + ' ' + text[1]
            ret['sponsor']['state'] = text[3].split('-')[1]
        cosponsor_elements = soup.find_all('table', class_='item_table')
        for element in cosponsor_elements:
            cosponsor_link = element.find('a')['href']
            id = cosponsor_link.split('/')[-1]
            tmp = {'bioguide_id':id,
                   'name': party_lookup[id]['name'],
                   'state': party_lookup[id]['state']}
            ret['cosponsors'].append(tmp)

        return ret
    except Exception as e:
        return "Exception occurred \n" + str(e)


def create_amendment_url(congress, chamber, number):
    assert chamber == 's' or chamber == 'h', 'type must be s or h'
    if chamber == 's':
        chamber = 'senate-amendment'
    else:
        chamber = 'house-amendment'
    url = 'https://www.congress.gov/amendment/' + \
          str(congress) + 'th-congress/' + \
          chamber + '/' + str(number) + '/cosponsors'
    return url



path = '/Users/alexray/Documents/data/'

with open(path+'legislators/party_lookup', 'r') as f:
    party_lookup = json.load(f)

#print(create_amendment_dict('https://www.congress.gov/amendment/115th-congress/house-amendment/84/cosponsors', party_lookup))
#tmp('https://www.congress.gov/amendment/115th-congress/senate-amendment/727/cosponsors')