# Random event generator script.
import random
import requests
import string
from sqlalchemy.sql.expression import func

from models import Guild, Player, Sword, session

EVENT_TYPES = ['add_player','add_sword','add_guild','join_guild','purchase_sword']
NUM_OBJECTS = 100

def get_random_word(length=10):
    return ''.join(
        random.choice(string.ascii_letters) for _ in range(length)
    )

counter = 0
while counter < NUM_OBJECTS:
    action = random.choice(EVENT_TYPES)
    if action == 'add_sword':
        params = {'cost': random.randint(1, 101)}
    elif action == 'add_player':
        params = {'money': random.randint(1, 101), 'name': get_random_word()}
    elif action == 'add_guild':
        params = {'name': get_random_word(10)}
    elif action == 'join_guild':
        if counter % 2: # join guild
            player = session.query(Player).filter(Player.guild_id == None).order_by(func.random()).first()
            if player is None:
                continue
            guild = session.query(Guild).order_by(func.random()).first()
            if guild is None:
                continue
            params = {'join': 1, 'player_id': player.id, 'guild_id': guild.id}
        else: # leave guild
            player = session.query(Player).filter(Player.guild_id != None).order_by(func.random()).first()
            if player is None:
                continue
            params = {'join': 0, 'player_id': player.id, 'guild_id': player.guild_id}
    elif action == 'purchase_sword':
        richest_player = session.query(Player).order_by(Player.money).first()
        if richest_player is None:
            continue
        sword = session.query(Sword).filter(Sword.cost <= richest_player.money).order_by(func.random()).first()
        if sword is None:
            continue
        buyer = session.query(Player).filter(Player.money >= sword.cost).order_by(func.random()).first()
        params = {'buyer_id': buyer.id, 'sword_id': sword.id}
    
    
    r = requests.get(
        'http://localhost:5000/{}'.format(action),
        params=params,
    )
    if r.status_code != 200:
        raise Exception('exception for event {}: {}\n\n{}'.format(action, r.reason, params))
    counter += 1
    session.expire_all()
