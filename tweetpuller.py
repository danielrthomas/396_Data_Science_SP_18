import base64
import requests
import sys
import csv

client_key = 'PVWE9FmBmQr9JLTFZhFhWmm1p'
client_secret = 'UcpPuhZ5RkKXPqkO89M64wF6Ta9vXrXcSCSZZZoqKR2n68lv1V'

class Location:
    def __init__(self, name, locstring):
        self.Name = name
        self.Geoloc = locstring

locations = {}
loc = Location("United States", "39.826182,-98.556542,2131mi")
locations[loc.Name] = loc
loc = Location("Great Britain", "53.945387,-2.521142,436mi")
locations[loc.Name] = loc
loc = Location("Australia", "-25.608874,134.361878,2235mi")
locations[loc.Name] = loc
loc = Location("Ireland", "53.501023,-8.017305,211mi")
locations[loc.Name] = loc
loc = Location("Canada", "64.323322,-96.104943,4339mi")
locations[loc.Name] = loc
loc = Location("South Africa", "-30,25,741mi")
locations[loc.Name] = loc
loc = Location("France", "46.760581,2.406532,583mi")
locations[loc.Name] = loc


def main():
    for key in locations:
        location = locations[key]
        path = location.Name.replace(' ','_')+'.csv'
        print '\n\n',location.Name,'\n'
        
        tweet_data = query(location)

        print '\n','Results: ',len(tweet_data)
        
        old_tweets = {}
        try:
            reader = csv.reader(open(path,'r'))
            for row in reader:
                old_tweets[row[0]] = row
        except Exception as e:
            print str(e)

        added_count = 0
        for tweet in tweet_data:
            if tweet['id_str'] not in old_tweets:
                old_tweets[tweet['id_str']] = [tweet['id_str'],tweet['text'].encode('utf-8')]
                added_count += 1
            
        writer = csv.writer(open(path,'w'))
        for key in old_tweets:
            try:
                writer.writerow(old_tweets[key])
            except Exception as e:
                print old_tweets[key][1], str(e)

        print "\nAdded "+str(added_count)+" to "+location.Name

        choice = ''
        count = -1

        while choice != 'y' and choice != 'n':
            choice = raw_input('\nDo you want to print the tweets for '+location.Name+'? (y/n)\n')

        if choice == 'y':
            while count < 0:
                count_a = raw_input("\nHow many?\n")
                try:
                    count = int(count_a)
                except Exception as e:
                    print str(e)

            for i in range(0,count):
                print '\n', tweet_data[i]['text'], ' | ', tweet_data[i]['place']

def query_helper(location,max_id=None):
    key_secret = '{}:{}'.format(client_key, client_secret).encode('ascii')
    b64_encoded_key = base64.b64encode(key_secret)
    b64_encoded_key = b64_encoded_key.decode('ascii')

    base_url = 'https://api.twitter.com/'
    auth_url = '{}oauth2/token'.format(base_url)

    auth_headers = {
        'Authorization': 'Basic {}'.format(b64_encoded_key),
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
    }

    auth_data = {
        'grant_type': 'client_credentials'
    }

    auth_resp = requests.post(auth_url, headers=auth_headers, data=auth_data)

    access_token = auth_resp.json()['access_token']

    search_headers = {
        'Authorization': 'Bearer {}'.format(access_token)    
    }
    search_params = {
    'q': '-RT -http import OR export OR tariff OR international trade',
    'count': 100,
    'result_type': 'recent'
    }
    search_params['geocode'] = location.Geoloc
    if max_id != None:
        search_params['max_id'] = max_id

    search_url = '{}1.1/search/tweets.json'.format(base_url)

    search_resp = requests.get(search_url, headers=search_headers, params=search_params)

    print 'Status Code: ',search_resp.status_code

    tweet_data = search_resp.json()

    return tweet_data,search_resp.status_code

def query(location):
    data = []
    tweet_data = query_helper(location)
    max_id = None
    call_count = 1
    while max_id != sys.maxint:
        max_id = sys.maxint
        add = False
        for tweet in tweet_data[0]['statuses']:
            add = True
            if max_id > tweet['id']:
                max_id = tweet['id']
        if add:
            data += tweet_data[0]['statuses']
            max_id -= 1
            tweet_data = query_helper(location,max_id)
        call_count += 1
    print "\nCalls made: ",call_count
    return data
