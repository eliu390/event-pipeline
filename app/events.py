# Random event generator script.
import random
import os
import time
from models import Guild, Player, GuildInteraction, Sword, Transaction, Session
from sqlalchemy.sql.expression import func

session = Session()

EVENT_TYPES = ["add_player","add_sword","add_guild","join_guild","purchase_sword"]
GUILD_NAMES = ["BatCave","Butlers","BadGuys","BadGuys","GoodGuys","GoodGuys","Cops","SupermansTeam"]
PLAYER_NAMES = ["Bruce","Catwoman","Joker","Joker","Two-Face","PoisonIvy","MrFreeze","Alfred"]
counter = 0

while counter >= 0:
    counter += 1
    action = EVENT_TYPES[random.randint(0, len(EVENT_TYPES)-1)]
    
    if action == "add_sword":
        cost = random.randint(1,101)
        command = 'docker-compose exec mids curl "http://localhost:5000/add_sword?cost={}"'.format(cost)
        os.system(command)
    
    elif action == "add_player":
        draw = random.randint(0,len(PLAYER_NAMES)-1)
        player_name = PLAYER_NAMES[draw]
        money = random.randint(100,1001)
        command = 'docker-compose exec mids curl "http://localhost:5000/add_player?name={}{}&money={}"'.format(
            player_name,
            counter,
            money
        )
        os.system(command)
    
    elif action == "add_guild":
        draw = random.randint(0,len(GUILD_NAMES)-1)
        guild_name = GUILD_NAMES[draw]
        command = 'docker-compose exec mids curl "http://localhost:5000/add_guild?name={}{}"'.format(
            guild_name,
            counter
        )
        os.system(command)

    elif action == 'join_guild':
        if counter % 2 == 0: # join guild
            print('joining guild')
            player = session.query(Player).order_by(func.random()).first()
            guild = session.query(Guild).order_by(func.random()).first()
            command = 'docker-compose exec mids curl "http://localhost:5000/join_guild?player_id={}&guild_id={}&join=1"'.format(
                player.id,
                guild.id
            )
            os.system(command)
        else: # leave guild
            print('leaving guild')
            player = session.query(Player).order_by(func.random()).first()
            if player.guild_id:
                command = 'docker-compose exec mids curl "http://localhost:5000/join_guild?player_id={}&guild_id={}&join=0"'.format(
                    player.id,
                    player.guild_id
                )
                os.system(command)

    elif action == 'purchase_sword':
        print('purchase_sword')
        player = session.query(Player).order_by(func.random()).first()
        sword = session.query(Sword).order_by(func.random()).first()
        print(player)
        command = 'docker-compose exec mids curl "http://localhost:5000/purchase_sword?buyer_id={}&sword_id={}"'.format(
            player.id,
            sword.id
        )
        os.system(command)

    time.sleep(5)