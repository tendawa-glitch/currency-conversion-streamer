import yaml
import logging
from flask import Flask, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from kafka import KafkaProducer
import requests
import json
import time
# setting up logging with format
logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
    level=logging.INFO)
logger = logging.getLogger()



# initialise flask server
app = Flask(__name__)


# Loads yml file with configurations
with open('config.yml', 'r') as stream:
    config = yaml.safe_load(stream)
app.config.update(config)

# configuration for kafka 
producer = KafkaProducer(bootstrap_servers=[app.config['kafka_server_url']])
scheduler = BackgroundScheduler()

# convert curreny from one currency to another currency code with amout. 
@app.route('/from/<one_code>/to/<another_code>/with/<amount>')
def convert_currency(one_code,another_code,amount):
    endpoint_url=app.config['convert_url']%(another_code,one_code,amount)
    logger.info(f'Incoming request : '+endpoint_url)
    response = requests.request('GET',endpoint_url , headers={'apikey': app.config['api_key']}, data={}) 
    return response.json()


# defines fluctuation in currency from certain period.
@app.route('/fluctuation/<start_date>/<end_date>')
def fluctuate_currency(start_date,end_date):
    endpoint_url=app.config['fluctuate_url']%(start_date,end_date)
    logger.info(f'Incoming request : '+endpoint_url)
    response = requests.request('GET',endpoint_url , headers={'apikey': app.config['api_key']}, data={}) 
    return response.json()


# send message to Kafka Topic
def publish_message():
    topic_name=app.config['kafka_topic']
    endpoint_url=app.config['topic_api_url']
    response = requests.request('GET',endpoint_url , headers={'apikey': app.config['api_key']}, data={}) 
    producer.send(topic_name, json.dumps(response.json()).encode('utf-8'))
    time.sleep(10)
    logger.info('Message successfully sent to Kafka Topic : '+topic_name)

# main class.
if __name__ == '__main__':
    scheduler.add_job(func=publish_message, trigger="interval", seconds=20)
    scheduler.start()
    app.run(debug=True)