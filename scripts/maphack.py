from flex import *
from time import sleep

ran = False

@flex_tick
def tick():
    global ran
    if ran:
        return
    ran = True

    sleep(5)
    reveal_level()
