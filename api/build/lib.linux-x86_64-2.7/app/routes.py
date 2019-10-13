from flask import Flask, redirect, request
from apscheduler.schedulers.background import BackgroundScheduler
import requests, config, db, threading, spotify_functions, time, smtp_email, logging

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, filename='app.log', format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')


@app.route('/')
@app.route('/signup/<state>')
def signup(state):
    logging.info('Signing up ' + state)

    url = ('https://accounts.spotify.com/authorize?client_id=' + config.client_id
           + '&response_type=code&redirect_uri=' + config.redirect_uri
           + '&scope=' + config.scope
           + '&state=' + state)
    return redirect(url)


@app.route('/callback')
def callback():
    # TODO: handle errors

    auth_code = request.args.get('code')
    state = request.args.get('state').split(':')
    scheduling_type = state[0]
    email = state[1]

    token_response = requests.post('https://accounts.spotify.com/api/token',
                                   headers={'Content-Type': 'application/x-www-form-urlencoded'},
                                   params={'grant_type': 'authorization_code',
                                           'code': auth_code,
                                           'redirect_uri': config.redirect_uri,
                                           'client_id': config.client_id,
                                           'client_secret': config.client_secret}).json()

    access_token = token_response['access_token']
    refresh_token = token_response['refresh_token']

    user_info = requests.get('https://api.spotify.com/v1/me',
                             headers={'Authorization': 'Bearer ' + access_token}).json()

    user_id = user_info['display_name']

    db.add_user(user_id, access_token, refresh_token, email, scheduling_type)

    # redirect to success page here
    return "success"


if __name__ == '__main__':
    logging.info("Begin")

    scheduler = BackgroundScheduler(timezone='utc')
    scheduler.add_job(spotify_functions.check_is_playing, 'interval', seconds=config.player_polling_time_seconds)
    # scheduler.add_job(smtp_email.email_scheduler, 'cron', hour=19)
    scheduler.add_job(smtp_email.email_scheduler, 'interval', seconds=10)
    scheduler.start()

    try:
        app.run()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
