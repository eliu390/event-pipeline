#!/usr/bin/env python
import json
from kafka import KafkaProducer
from flask import Flask, request

app = Flask(__name__)
producer = KafkaProducer(bootstrap_servers='kafka:29092')


def log_to_kafka(topic, event):
    event.update(request.headers)
    producer.send(topic, json.dumps(event).encode())


def valid_int(param):
    try:
        num = int(param)
        return num >= 0
    except:
        return False
    

@app.route("/")
def default_response():
    default_event = {'event_type': 'default'}
    log_to_kafka('events', default_event)
    return "This is the default response!\n"


@app.route("/purchase_sword")
def purchase_sword():
    buyer_id = request.args.get('buyer_id')
    seller_id = request.args.get('seller_id')
    
    if !valid_int(buyer_id) or !valid_int(seller_id):
        return "Invalid params!"
    
    purchase_sword_event = {'event_type': 'purchase_sword', 'buyer_id': buyer_id, 'seller_id': seller_id}
    log_to_kafka('events', purchase_sword_event)
    return "Sword purchased from player " + seller_id + "!\n"


@app.route("/join_guild")
def join_guild():
    player_id = request.args.get('player_id')
    guild_id = request.args.get('guild_id')
    join = request.args.get('join') # join=1 means joining guild, join=0 means leaving guild
    
    if !valid_int(player_id) or !valid_int(guild_id) or !valid_int(join):
        return "Invalid params!"
    
    join_guild_event = {'event_type': 'join_guild', 'player_id': player_id, 'guild_id': guild_id, 'join': join}
    log_to_kafka('events', join_guild_event)
    if join == 1:
        return "Joined guild " + guild_id + "!\n"
    else:
        return "Left guild " + guild_id + "!\n"

