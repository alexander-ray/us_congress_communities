import json
import os
from scraper import create_amendment_dict
import csv

path = '/Users/alexray/Documents/data/'

with open(path+'legislators/party_lookup', 'r') as f:
    party_lookup = json.load(f)

numbers = [(3517, 99), (3773, 100), (3229, 101),
           (3442, 102), (2653, 103), (5439, 104),
           (3842, 105), (4367, 106), (4984, 107),
           (4088, 108), (5240, 109), (5704, 110),
           (4924, 111), (3450, 112), (4126, 113),
           (5186, 114), (4062, 115)]

'''
numbers = [(1006, 97), (1092, 98), (1243, 99),
           (917, 100), (911, 101), (891, 102),
           (942, 103), (1372, 104), (931, 105),
           (1067, 106), (632, 107), (812, 108),
           (1222, 109), (1185, 110), (786, 111),
           (1499, 112), (1155, 113), (1487, 114),
           (978, 115)]
'''
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
    with open('errored_senate2.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow([congress])
        writer.writerow(errored)
