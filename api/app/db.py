from elasticsearch import Elasticsearch
import logging

es = Elasticsearch()

logging.basicConfig(filename='app.log', level=logging.INFO)


def add_user(user_id, access_token, refresh_token, email, scheduling_type):
    # TODO: check if user exists

    id = user_id + '-' + email
    doc = {
        'user_id': id,
        'access_token': access_token,
        'refresh_token': refresh_token,
        'email': email,
        'scheduling_type': scheduling_type,
        'playing_time_today_seconds': 0,
        'total_playing_time': {}
    }

    response = es.index(index='users', doc_type="user", id=id, body=doc)

    logging.info('Added user ' + id)
