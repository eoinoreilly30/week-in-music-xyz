from elasticsearch import Elasticsearch
import requests, config, logging
from datetime import date

es = Elasticsearch()


def renew_access_token(user_id):
    document = es.get(index="users", doc_type="user", id=user_id)['_source']

    token_response = requests.post('https://accounts.spotify.com/api/token',
                                   headers={'Content-Type': 'application/x-www-form-urlencoded'},
                                   params={'grant_type': 'refresh_token',
                                           'refresh_token': document['refresh_token'],
                                           'redirect_uri': config.redirect_uri,
                                           'client_id': config.client_id,
                                           'client_secret': config.client_secret}).json()

    access_token = token_response['access_token']

    try:
        document['refresh_token'] = token_response['refresh_token']
    except KeyError:
        logging.info('no refresh_token for ' + user_id)

    document['access_token'] = access_token

    update_response = es.index(index='users', doc_type="user", id=user_id, body=document)

    logging.info('access_token ' + update_response + ' for ' + user_id)


def check_is_playing():
    users = es.search(index="users", body={"query": {"match_all": {}}})

    for user in users['hits']['hits']:
        document = user['_source']
        user_id = document['user_id']
        player_response = requests.get('https://api.spotify.com/v1/me/player',
                                       headers={'Authorization': 'Bearer ' + document['access_token']})
        player_response.encoding = 'utf-8'

        try:
            error = player_response.json()['error']
            renew_access_token(user_id)
        except (ValueError, KeyError):
            if player_response.text:
                if player_response.json()['is_playing']:
                    try:
                        document['playing_time_by_day'][
                            date.today().strftime("%j")] += config.player_polling_time_seconds
                    except KeyError:
                        document['playing_time_by_day'][
                            date.today().strftime("%j")] = config.player_polling_time_seconds

                    update_result = es.index(index="users", doc_type='user', id=user_id, body=document)['result']
                    logging.info('listening time ' + update_result + ' for ' + user_id)
                else:
                    logging.info('paused for user ' + user_id)
            else:
                logging.info('no player for user ' + user_id)
