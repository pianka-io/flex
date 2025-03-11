import game
import math

GOLD = 0x20B

def pickup_gold_tick():
    player = game.get_player_unit()
    if not player:
        return

    for unit in game.get_item_table():
        if not unit or unit.id == 0:
            continue

        if unit.type == GOLD:
            distance = math.sqrt((unit.x - player.x) ** 2 + (unit.y - player.y) ** 2)
            if distance <= 5.0:
                game.interact(unit.id, 4)
                game.write_log("INF", f"Picking up gold at ({unit.x}, {unit.y})")

game.register_tick(pickup_gold_tick)
