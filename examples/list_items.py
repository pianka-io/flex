from time import sleep
from flex import *

ran = False

@loop(LoopType.FLEX)
def tick():
    global ran
    if ran:
        return
    ran = True
    sleep(5) # probably not a great idea
    list_items()

def list_items():
    for item in get_all_items():
        write_log("INF", f"Item: {item.type.name} (ID: {item.id})")
        if item.owner is None:
            write_log("INF", f"  No owner")
        else:
            write_log("INF", f"  Owner id: {item.owner.id}")
        write_log("INF", f"  Quality: {item.quality.name}")
        write_log("INF", f"  Level: {item.level}")
        write_log("INF", f"  Flags: {item.flags}")
        for stat in item.stats:
            write_log("INF", f"  Stat: {stat.type.name}, Value: {stat.value}")
