#!/usr/bin/env python
from flask import Flask, request
from kafka import KafkaProducer
import json
from datetime import datetime
from models import (
    Guild,
    Player,
    GuildInteraction,
    Sword,
    Transaction,
    Session
)

app = Flask(__name__)
producer = KafkaProducer(bootstrap_servers='kafka:29092')

session = Session()

def log_to_kafka(topic, event):
    event_type = event.pop('event_type')
    event.update({'timestamp': datetime.now().strftime('%D %T')})
    producer.send(
        topic,
        json.dumps(
            {
                'event_type': event_type,
                'event_body': event,
            }
        ).encode()
    )

def validate_id(id_):
    id_ = int(id_)
    if not id_ > 0:
        raise Exception('id_ {} not greater than 0.'.format(id_))
    return id_

@app.route("/")
def default_response():
    default_event = {'event_type': 'default'}
    log_to_kafka('events', default_event)
    return "This is the default response!\n"


@app.route("/add_sword")
def add_sword():
    cost = request.args.get('cost')
    try:
        # not really an id, but it does what we want
        cost = validate_id(cost)
    except:
        raise Exception('Invalid cost {}\n'.format(cost))
        
    sword = Sword(cost=cost)
    session.add(sword)
    session.commit()
    
    log_to_kafka(
        'events',
        {
            'event_type': 'add_sword',
            'sword_id': sword.id,
            'cost': sword.cost,
        },
    )
    
    return 'Added a sword with id {} and cost {}\n'.format(
        sword.id, sword.cost,
    )

@app.route("/add_player")
def add_player():
    name = request.args.get('name')
    if name is None:
        raise Exception('The "name" argument is required.')
    
    money = request.args.get('money')
    try:
        # not really an id, but it does what we want
        money = validate_id(money)
    except Exception as e:
        raise e
        raise Exception('Invalid money {}\n'.format(money))
    
    player = Player(name=name, money=money)
    session.add(player)
    session.commit()
    
    log_to_kafka(
        'events',
        {
            'event_type': 'add_player',
            'player_id': player.id,
            'name': player.name,
            'money': player.money,
        },
    )
    return 'Added a player with id {}, name {}, and money {}\n'.format(
        player.id, player.name, player.money,
    )

@app.route("/add_guild")
def add_guild():
    name = request.args.get('name')
    if name is None:
        raise Exception('The "name" argument is required.')

    guild = Guild(name=name)
    session.add(guild)
    session.commit()
    
    log_to_kafka(
        'events',
        {
            'event_type': 'add_guild',
            'guild_id': guild.id,
            'name': guild.name,
        },
    )
    return 'Added a guild with id {} and name {}\n'.format(
        guild.id, guild.name,
    )

@app.route("/purchase_sword")
def purchase_sword():
    # validate buyer
    buyer_id = request.args.get('buyer_id')
    try:
        buyer_id = validate_id(buyer_id)
    except:
        raise Exception('Invalid buyer id {}\n'.format(buyer_id))
    try:
        buyer = session.query(Player).filter(Player.id == buyer_id).one()
    except:
        raise Exception('Buyer with id {} does not exist\n'.format(buyer_id))
    
    # validate sword
    sword_id = request.args.get('sword_id')
    try:
        sword_id = validate_id(sword_id)
    except:
        raise Exception('Invalid sword id {}\n'.format(sword_id))
    try:
        sword = session.query(Sword).filter(Sword.id == sword_id).one()
    except:
        raise Exception('Sword with id {} does not exist\n'.format(sword_id))
    
    if (sword.cost > buyer.money):
        raise Exception(
            'Buyer with id {} cannot afford sword with id {} and cost {}\n'.format(
                buyer_id, sword_id, sword.cost,
            )
        )

    # add transaction
    transaction = Transaction(
        sword_id=sword_id,
        buyer_id=buyer_id,
        seller_id=sword.player_id,
    )
    
    # update sword
    sword.player_id = buyer_id
        
    # update buyer
    buyer.money -= sword.cost
    
    # update seller
    seller = sword.player
    if seller:
        seller.money += sword.cost
    
    session.add(transaction)
    session.commit()

    # send event to kafka
    purchase_sword_event = {
        'event_type': 'purchase_sword',
        'buyer_id': buyer_id,
        'seller_id': sword.player_id,
        'sword_id': sword_id,
        'transaction_id': transaction.id,
    }
    log_to_kafka('events', purchase_sword_event)
    
    return 'Player {} purchased sword {} from seller {} for {} gold\n'.format(
        buyer_id, sword_id, sword.player_id, sword.cost,
    )


@app.route("/join_guild")
def join_guild():

    # validate player
    player_id = request.args.get('player_id')
    try:
        player_id = validate_id(player_id)
    except:
        raise Exception('Invalid player id {}\n'.format(player_id))
    try:
        player = session.query(Player).filter(Player.id == player_id).one()
    except Exception as e:
        return str(e)
        raise Exception('Player with id {} does not exist\n'.format(player_id))

    # validate guild
    guild_id = request.args.get('guild_id')
    try:
        guild_id = validate_id(guild_id)
    except:
        raise Exception('Invalid guild id {}\n'.format(guild_id))
    try:
        guild = session.query(Guild).filter(Guild.id == guild_id).one()
    except:
        raise Exception('Guild with id {} does not exist\n'.format(guild_id))
    
    # validate join
    join = request.args.get('join', 1)
    try:
        # join=1 means joining guild, join=0 means leaving guild
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
    guild_interaction = GuildInteraction(
        player_id=player_id,
        guild_id=guild_id,
        join=join,
    )
    session.add(guild_interaction)
    session.commit()
    
    # send event to kafka
    join_guild_event = {
        'event_type': 'join_guild',
        'player_id': player_id,
        'guild_id': guild_id,
        'join': join,
        'guild_interaction_id': guild_interaction.id,
    }
    log_to_kafka('events', join_guild_event)
    if join:
        return 'Player with id {} joined guild with id {}\n'.format(player_id, guild_id)
    else:
        return 'Player with id {} left guild with id {}\n'.format(player_id, guild_id)

