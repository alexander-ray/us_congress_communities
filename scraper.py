import json
import os
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import re

HOUSE_COUNT_ID = 'facetItemchamberHousecount'
SENATE_COUNT_ID = 'facetItemchamberSenatecount'
LEG_COUNT_TYPES = ['bills', 'amendments', 'resolutions', 'joint-resolutions', 'concurrent-resolutions']
# Type shorthands for use creating paths
LEG_TYPE_SHORTHAND = {'bills': '', 'amendments': 'amendments', 'concurrent-resolutions': 'conres',
                  'joint-resolutions': 'jres', 'resolutions': 'res'}
COUNT_IDS = {'house': HOUSE_COUNT_ID, 'senate': SENATE_COUNT_ID}
CONGRESS_URL_SEARCH_FORMAT = 'https://www.congress.gov/search?q=%7B%22source%22%3A%22legislation%22%2C%22congress%22%3A%22{}%22%2C%22type%22%3A%22{}%22%7D'

def get_legislation_counts(congresses=range(93, 117)):
    print(f'Congresses: {list(congresses)}')
    header = {'User-Agent': 'Mozilla/5.0'}

    legislation_counts = {}
    for congress in congresses:
        print(f'Congress: {congress}')
        leg_type_counts = {}
        for leg_type in LEG_COUNT_TYPES:
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

        tables = soup.find_all('table', class_='standard01')
        # one of the strange "Reserved Bill"s
        if len(tables) == 0:
            return

        sponsor_link = tables[0].find(text=re.compile('Sponsor:')).find_next().find('a')['href']
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
            # if it exists, is just "cosponsors who withdrew"
            if len(element.find_all('thead', id='withdrawnThead')) != 0:
                break
            cosponsor_links = element.find_all('a', href=True)
            for cosponsor_link in cosponsor_links:
                cosponsor_link = cosponsor_link['href']
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

def save_legislation(base_path, party_lookup, legislation_id, congress, leg_type, chamber):
    # Variable for use in paths is the first letter of the chamber + the shorthand code for it
    path_var = chamber[0] + LEG_TYPE_SHORTHAND[leg_type]
    # Dir prefixes don't make much sense, but we persevere
    if leg_type == 'amendments':
        dir_prefix = 'a'
    elif leg_type == 'bills' and chamber == 'house':
        dir_prefix = 'hr'
        path_var = 'hr'
    else:
        dir_prefix = path_var

    if os.path.exists(f'{base_path}/bills/{congress}/{path_var}/{dir_prefix + str(legislation_id)}'):
        raise RuntimeError('already saved')

    url_path_param = 'amendment' if leg_type == 'amendments' else 'bill'
    path = f'https://www.congress.gov/{url_path_param}/' \
           f'{congress}th-congress/{chamber}-{leg_type.rstrip("s")}'  \
           f'/{legislation_id}/cosponsors'
    amendment = create_amendment_dict(path, party_lookup)
    if amendment is None:
        return

    if 'Error 404:' in amendment or 'Exception' in amendment:
        print(f'Error saving {path}: {amendment}')
        raise RuntimeError('Error creating amendment')

    os.makedirs(f'{base_path}/bills/{congress}/{path_var}/{dir_prefix + str(legislation_id)}')
    with open(f'{base_path}/bills/{congress}/{path_var}/{dir_prefix + str(legislation_id)}/data.json', 'w') as fout:
        fout.write(json.dumps(amendment))

def save_legislation_wrapper(base_path, congresses=range(93, 117), legislation_counts=None):
    base_path = base_path.rstrip()

    with open(base_path + '/legislators/party_lookup', 'r') as f:
        party_lookup = json.load(f)

    if legislation_counts is None:
        print('Retrieving legislation counts')
        legislation_counts = get_legislation_counts(congresses)
    else:
        print('Using existing legislation counts')
        legislation_counts = {k:v for k, v in legislation_counts.items() if k in set(congresses)}
    print('\nRetrieving legislation')
    for congress, leg_type_dict in legislation_counts.items():
        print(f'Congress: {congress}')
        for leg_type, chamber_dict in leg_type_dict.items():
            # Early congresses don't have amendments, save time
            if congress < 97 and leg_type == 'amendments':
                continue
            for chamber, count in chamber_dict.items():
                print(f'Attempting to save {count} {leg_type} for congress {congress} in the {chamber}')
                already_saved = 0
                errored = 0
                for i in range(1, count+1):
                    try:
                        save_legislation(base_path, party_lookup, i, congress, leg_type, chamber)
                    except RuntimeError as e:
                        if 'already saved' in str(e):
                            already_saved += 1
                        elif 'Error creating amendment' in str(e):
                            errored += 1
                        else:
                            raise RuntimeError()
                print(f'Saved {count-errored-already_saved} {leg_type} for congress {congress}')
                print(f'{already_saved} previously saved, {errored} errored')

def gap_checker(dir_path):
    file_numbers = set()

    for filename in os.listdir(dir_path):
        file_numbers.add(int(re.findall("\d+", filename)[0]))

    max_num = max(file_numbers)
    for i in range(1, max_num+1):
        if i not in file_numbers:
            print(i)

def merge_lookup_dicts(base_path, path_to_addition):
    with open(path_to_addition, 'r') as f:
        new_data = json.load(f)

    with open(base_path+'thomas_lookup', 'r') as f:
        thomas_lookup = json.load(f)
    with open(base_path+'bioguide_lookup', 'r') as f:
        bioguide_lookup = json.load(f)
    with open(base_path+'party_lookup', 'r') as f:
        party_lookup = json.load(f)

    for entry in new_data:
        print(entry)
        if 'bioguide' in entry['id'] and 'thomas' in entry['id']:
            thomas_lookup[entry['id']['bioguide']] = entry['id']['thomas']
            bioguide_lookup[entry['id']['thomas']] = entry['id']['bioguide']
        # Super early ones don't have party, so we skip
        elif 'bioguide' in entry['id'] and 'party' in entry['terms'][0]:
            party_lookup[entry['id']['bioguide']] = {
                'party': entry['terms'][0]['party'],
                'name': entry['name']['first'] + ' ' + entry['name']['last'],
                'state': entry['terms'][0]['state']
            }

    with open(base_path+'thomas_lookup_new', 'w') as fout:
        fout.write(json.dumps(thomas_lookup))
    with open(base_path+'bioguide_lookup_new', 'w') as fout:
        fout.write(json.dumps(bioguide_lookup))
    with open(base_path+'party_lookup_new', 'w') as fout:
        fout.write(json.dumps(party_lookup))