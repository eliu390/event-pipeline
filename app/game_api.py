#!/usr/bin/env python
import json
from kafka import KafkaProducer
from flask import Flask, request
from models.py import Guild, Player, GuildInteraction, Sword, Transaction, session

app = Flask(__name__)
producer = KafkaProducer(bootstrap_servers='kafka:29092')


def log_to_kafka(topic, event):
    event.update(request.headers)
    producer.send(topic, json.dumps(event).encode())


@app.route("/")
def default_response():
    default_event = {'event_type': 'default'}
    log_to_kafka('events', default_event)
    return "This is the default response!\n"


@app.route("/purchase_sword")
def purchase_sword():
    buyer_id = request.args.get('buyer_id')
    seller_id = request.args.get('seller_id') or 0 # if no seller_id, set to 0, means buying from NPC
    sword_id = request.args.get('sword_id')
    
    # validate buyer
    try:
        valid_buyer = (int(buyer_id) >= 0)
    except:
        raise Exception('Invalid buyer id {}\n'.format(buyer_id))
    try:
        buyer = session.query(Player).filter(id=buyer_id).one()
    except:
        raise Exception('Buyer with id {} does not exist\n'.format(buyer_id))
    
    # validate seller
    try:
        valid_seller = (int(seller_id) >= 0)
    except:
        raise Exception('Invalid seller id {}\n'.format(seller_id))
    try:
        if seller_id != 0:
            seller = session.query(Player).filter(id=seller_id).one()
    except: 
        raise Exception('Seller with id {} does not exist\n'.format(seller_id))
    
    # validate sword
    try:
        valid_sword = (int(sword_id) >= 0)
    except:
        raise Exception('Invalid sword id {}\n'.format(sword_id))
    try:
        sword = session.query(Sword).filter(id=sword_id).one()
    except:
        raise Exception('Sword with id {} does not exist\n'.format(sword_id))
    try:
        seller_has_sword = session.query(Sword).filter(id=sword_id, player_id=seller_id).one()
    except:
        raise Exception('Seller with id {} does not own sword with id {}\n'.format(seller_id, sword_id))
    if (sword.cost > buyer.money):
        raise Exception('Buyer with id {} cannot afford sword with id {} and cost {}\n'.format(buyer_id, sword_id, sword.cost))
    
    # update sword
    sword.player_id = buyer_id
        
    # update buyer
    buyer.money -= sword.cost
    
    # update seller
    seller.money += sword.cost
    
    # add transaction
    sword_transaction = Transaction(sword_id, buyer_id, seller_id)
    session.add(sword_transaction)
    session.commit()

    # send event to kafka
    purchase_sword_event = {'event_type': 'purchase_sword', 'buyer_id': buyer_id, 'seller_id': seller_id, 'sword_id': sword_id}
    log_to_kafka('events', purchase_sword_event)
    return 'Player {} purchased sword {} from seller {} for {} gold\n'.format(buyer_id, sword_id, seller_id, sword_cost)


@app.route("/join_guild")
def join_guild():
    player_id = request.args.get('player_id')
    guild_id = request.args.get('guild_id')
    join = request.args.get('join') # join=1 means joining guild, join=0 means leaving guild
    
    # validate player
    try:
        valid_player = (int(player_id) >= 0)
    except:
        raise Exception('Invalid player id {}\n'.format(player_id))
    try:
        player = session.query(Player).filter(id=player_id).one()
    except:
        raise Exception('Player with id {} does not exist\n'.format(player_id))

    # validate guild
    try:
        valid_guild = (int(guild_id) >= 0)
    except:
        raise Exception('Invalid guild id {}\n'.format(guild_id))
    try:
        guild = session.query(Guild).filter(id=guild_id).one()
    except:
        raise Exception('Guild with id {} does not exist\n'.format(guild_id))
    
    # validate join
    try:
        join = (int(join) == 1)
    except:
        raise Exception('Invalid join code {}\n'.format(join))
    
    # update player
    if join: # player can only join if not in a guild
        if player.guild_id != None:
            raise Exception('Player with id {} is already in a guild with id {}\n'.format(player_id, player.guild_id))
        else:
            player.guild_id = guild_id
    else: # player can only leave a guild they're in
        if player.guild_id == guild_id:
            player.guild_id = None
        else:
            raise Exception('Player with id {} is not in the guild with id {}\n'.format(player_id, guild_id))
    
    # add transaction
    guild_transaction = GuildInteraction(player_id, guild_id, join)
    session.add(guild_transaction)
    session.commit()
    
    # send event to kafka
    join_guild_event = {'event_type': 'join_guild', 'player_id': player_id, 'guild_id': guild_id, 'join': join}
    log_to_kafka('events', join_guild_event)
    if join:
        return 'Player with id {} joined guild with id {}\n'.format(player_id, guild_id)
    else:
        return 'Player with id {} left guild with id {}\n'.format(player_id, guild_id)

