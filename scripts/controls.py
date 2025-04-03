from flex import *
import time

last = time.time()

@loop(LoopType.FLEX)
def flex_loop():
    global last
    if time.time() - last > 10:
        info("hmm")
        info("okhm")
        last = time.time()
        for control in game.get_all_controls():
            info(str(control))
