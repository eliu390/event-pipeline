# Random event generator script.
import random
import os
import time

EVENT_TYPES = ["add_guild", "add_player", "add_sword", "join_guild","purchase_sword"]
GUILD_NAMES = ["BatCave","Butlers","BadGuys","GoodGuys","Cops","SupermansTeam"]
PLAYER_NAMES = ["Bruce","Catwoman","Joker","Two-Face","PoisonIvy","MrFreeze","Alfred"]
counter = 2

while counter >= 1:

    action = random.randint(0, len(EVENT_TYPES)-1)

    
    
    if EVENT_TYPES[action] == "add_sword":
        cost = random.randint(1,101)
        command = 'docker-compose exec mids curl "http://localhost:5000/add_sword?cost='+str(cost)+'"'
        os.system(command)

    
    
    elif EVENT_TYPES[action] == "add_player":
        if len(PLAYER_NAMES) > 0:
            draw = random.randint(0,len(PLAYER_NAMES)-1)
            player_name = PLAYER_NAMES[draw]
            PLAYER_NAMES.pop(draw)
            money = random.randint(0,1001)
            command = 'docker-compose exec mids curl "http://localhost:5000/add_player?name='+str(player_name)+'&money='+str(money)+'"'
            os.system(command)
        else:
            draw = counter
            counter =+ 1
            player_name = "RandomPlayer"+str(draw)
            command = 'docker-compose exec mids curl "http://localhost:5000/add_player?name='+str(player_name)+'&money='+str(money)+'"'
            os.system(command)


    
    elif EVENT_TYPES[action] == "add_guild":
        if len(GUILD_NAMES) > 0:
            draw = random.randint(0,len(GUILD_NAMES)-1)
            guild_name = GUILD_NAMES[draw]
            GUILD_NAMES.pop(draw)
            command = 'docker-compose exec mids curl "http://localhost:5000/add_guild?name='+str(guild_name)+'"'
            os.system(command)
        else:
            draw = counter
            counter =+ 1
            guild_name = "RandomGuild"+str(draw)
            command = 'docker-compose exec mids curl "http://localhost:5000/add_guild?name='+str(guild_name)+'"'
            os.system(command)


    else:
        print("code tbd...")

    time.sleep(3)