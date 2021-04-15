from models import (
    Guild,
    Player,
    GuildInteraction,
    Sword,
    Transaction,
    Session
)
from sqlalchemy.sql.expression import func
import time

session = Session()

# player1 = Player(
#     id = 12,
#     name = 'acb',
#     money = 123
# )

# session.add(player1)
# session.commit()

# sword1 = Sword(
#     id = 12,
#     cost = 234
# )
# session.add(sword1)
# session.commit()

# sword = session.query(Player).order_by(func.random()).first()
# print(sword.name)

test = session.query(Player).all()
print(len(test))