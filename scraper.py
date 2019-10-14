import re
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup

HOUSE_COUNT_ID = 'facetItemchamberHousecount'
SENATE_COUNT_ID = 'facetItemchamberSenatecount'
TYPES = ['bills', 'amendments', 'resolutions', 'joint-resolutions', 'concurrent-resolutions']
COUNT_IDS = {'house': HOUSE_COUNT_ID, 'senate': SENATE_COUNT_ID}
CONGRESS_URL_SEARCH_FORMAT = 'https://www.congress.gov/search?q=%7B%22source%22%3A%22legislation%22%2C%22congress%22%3A%22{}%22%2C%22type%22%3A%22{}%22%7D'

def get_legislation_counts(congresses=range(93, 117)):
    print(f'Congresses: {list(congresses)}')
    header = {'User-Agent': 'Mozilla/5.0'}

    legislation_counts = {}
    for congress in congresses:
        print(f'Congress: {congress}')
        leg_type_counts = {}
        for leg_type in TYPES:
            print(f'Legislation type: {leg_type}')
            req = Request(CONGRESS_URL_SEARCH_FORMAT.format(congress, leg_type), headers=header)
            page = urlopen(req)
            soup = BeautifulSoup(page, 'lxml')
            counts = {}
            for k, v in COUNT_IDS.items():
                spans = soup.find_all('span', {'class': 'count', 'id': v})
                if len(spans) == 0:
                    print(f'No counts for {leg_type} in congress {congress}')
                    continue
                counts[k] = int(''.join([s for s in spans[0].contents[0] if s.isdigit()]))
            leg_type_counts[leg_type] = counts
        legislation_counts[congress] = leg_type_counts
    return legislation_counts

def create_amendment_dict(base_url, party_lookup):
    """
    Create dictionary of information on sponsors and cosponsors of a given amendment.
    :param base_url: URL to scrape. Ex. https://www.congress.gov/amendment/114th-congress/senate-amendment/5186/cosponsors
    :param party_lookup: Dictionary to afford info lookup by bioguide id
    :return: Dict
    """
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


'''
path = '/Users/alexray/Documents/data/'

with open(path+'legislators/party_lookup', 'r') as f:
    party_lookup = json.load(f)

numbers = [(3517, 99), (3773, 100), (3229, 101),
           (3442, 102), (2653, 103), (5439, 104),
           (3842, 105), (4367, 106), (4984, 107),
           (4088, 108), (5240, 109), (5704, 110),
           (4924, 111), (3450, 112), (4126, 113),
           (5186, 114), (4062, 115)]

for number, congress in numbers:
    leg_ids = list(range(1, number))
    congress = str(congress)
    print(congress)
    errored = []
    for leg_id in leg_ids:
        leg_id = str(leg_id)
        if os.path.exists(path + 'bills/' + str(congress) + '/samendments/a' + leg_id):
            continue
        amendment = create_amendment_dict('https://www.congress.gov/amendment/'+str(congress)+'th-congress/senate-amendment/'+leg_id+'/cosponsors', party_lookup)

        if 'Error 404:' in amendment or 'Exception' in amendment:
            errored.append(leg_id)
            continue
        if not os.path.exists(path + 'bills/' + str(congress) + '/samendments/a' + leg_id):
            os.makedirs(path + 'bills/' + str(congress) + '/samendments/a' + leg_id)
        with open(path + 'bills/' + str(congress) + '/samendments/a' + leg_id + '/data.json', 'w') as fout:
            fout.write(json.dumps(amendment))

    print('num errored: ' + str(len(errored)))
    with open('errored_senate3.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow([congress])
        writer.writerow(errored)
'''