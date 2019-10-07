import smtplib, ssl, config, logging
from elasticsearch import Elasticsearch
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

es = Elasticsearch()

logging.basicConfig(filename='app.log', level=logging.INFO)

intervals = (
    ('weeks', 604800),  # 60 * 60 * 24 * 7
    ('days', 86400),  # 60 * 60 * 24
    ('hours', 3600),  # 60 * 60
    ('minutes', 60),
    ('seconds', 1),
)


def display_time(seconds, granularity=2):
    result = []

    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip('s')
            result.append("{} {}".format(value, name))
    return ', '.join(result[:granularity])


def send_email(user_id):
    logging.info('sending email to ' + user_id)

    user = es.get(index="users", doc_type="user", id=user_id)['_source']
    listening_time = display_time(user['playing_time_today_seconds'], 5)
    receiver_email = user['email']

    message = MIMEMultipart("alternative")
    message["Subject"] = listening_time + ' listened'
    message["From"] = config.email
    message["To"] = receiver_email

    html = "<html><body><p>You've listened to " + listening_time + " of music</p></body></html>"

    message.attach(MIMEText(html, "html"))

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(config.email, config.email_password)
        server.sendmail(
            config.email, receiver_email, message.as_string()
        )

    logging.info('sent to ' + user_id)


def email_scheduler():
    users = es.search(index="users", body={"query": {"match_all": {}}})

    for user in users['hits']['hits']:
        send_email(user['_source']['user_id'])
