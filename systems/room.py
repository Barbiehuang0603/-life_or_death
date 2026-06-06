import random

def generate_room():

    directions = ["front", "left", "right"]

    room = {}

    # 隨機兩個方向生成門
    door_positions = random.sample(directions, 2)

    # 隨機哪個是生門
    life_door = random.choice(door_positions)

    for d in directions:

        if d not in door_positions:
            room[d] = "wall"

        elif d == life_door:
            room[d] = "life"

        else:
            room[d] = "death"

    # 後方固定
    room["back"] = "back"

    return room