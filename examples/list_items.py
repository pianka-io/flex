from flex import *

ran = False

@flex_tick
def tick():
    global ran
    if ran:
        return
    ran = True

    for item in get_all_items():
        write_log("INF", f"Item: {item.type.name} (ID: {item.id})")
        for stat in item.stats:
            write_log("INF", f"  Stat: {stat.type.name}, Value: {stat.value}")
