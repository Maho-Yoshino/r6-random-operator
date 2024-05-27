import random, json, os, logging, math
from datetime import datetime
from typing import Literal
logger = logging.getLogger(__name__)
filename = f"r6randomop_{str(datetime.now().date()).replace("-","_")}.log"
log_format = "%(asctime)s::%(levelname)-8s:%(message)s"
logging.basicConfig(filename=filename, encoding='utf-8', level=logging.DEBUG, format=log_format, datefmt="%H:%M:%S")

json_name = "op_list.json"
#json_name = "operator_list.json"

def main():
    mode = input("Mode: ").lower()
    if mode == "":
        logging.error("Invalid mode input")
        raise ValueError(f"Not a valid input (empty string)")
    elif mode[0] == "a":
        mode = "attack"
        altmode = "defense"
        logging.info("Mode: attack")
    elif mode[0] == "d":
        mode = "defense"
        altmode = "attack"
        logging.info("Mode: defense")
    else:
        logging.error("Invalid mode input")
        raise ValueError(f"Not a valid input \"{mode}\"")
    rounds = 0
    gmode = input("Gamemode (for single operator enter \"o\"): ").lower()[0]
    rounds = {
        "rounds_per_side":0,
        "OT":0
    }
    if gmode == "q":
        rounds["rounds_per_side"] = 2
        rounds["OT"] = 1
        logging.info("Gamemode: Quick match")
    elif gmode == "s":
        rounds["rounds_per_side"] = 3
        rounds["OT"] = 1
        logging.info("Gamemode: Standard")
    elif gmode == "r":
        rounds["rounds_per_side"] = 3
        rounds["OT"] = 3
        logging.info("Gamemode: Ranked")
    elif gmode == "o":
        print(f"Random {mode} operator: {pick_random_op(mode, 1)}")
        return
    else:
        logging.error("Invalid gamemode")
        raise ValueError("Invalid gamemode")
    op_repeat = input("Repeating operators?: ").lower()[0]
    mode_ops = []
    altmode_ops = []
    rounds_per_side = rounds["rounds_per_side"]+rounds["OT"]
    for i in range(rounds["rounds_per_side"]+rounds["OT"]):
        mode_ops.append(pick_random_op(mode, rounds_per_side, mode_ops, True if op_repeat == "y" else False))
        altmode_ops.append(pick_random_op(altmode, rounds_per_side, altmode_ops, True if op_repeat == "y" else False))
    logging.debug("Created mode_ops and altmode_ops")
    for j in range(1, rounds["rounds_per_side"]+1):
        print(f"{mode} (round {j}): {mode_ops[j-1]}")
    for j in range(rounds["rounds_per_side"]+1, rounds["rounds_per_side"]*2+1):
        print(f"{altmode} (round {j}): {altmode_ops[j-rounds["rounds_per_side"]-1]}")
    for i in range(1, rounds["OT"]+1):
        round_num = rounds['rounds_per_side']*2+i
        print(f"{mode} (round {round_num} OT): {mode_ops[rounds['rounds_per_side']-1+i]}")
        print(f"{altmode} (round {round_num} OT): {altmode_ops[rounds['rounds_per_side']-1+i]}")
    logging.debug(mode_ops)
    logging.debug(altmode_ops)

def open_file():
    try: 
        with open(json_name, encoding="utf-8") as file:
            op_list = json.load(file)
            logging.info("operator_list.json loaded")
    except FileNotFoundError:
        logger.critical("operator_list.json missing")
        print(f"{json_name} does not exist")
        raise FileNotFoundError
    return op_list
def valid_operators(side:Literal["attack", "defense"]):
    valid_operators_l = [operator for operator, owned in op_list[side].items() if owned]
    logging.debug(f"valid_operators({side}): {valid_operators_l}")
    return valid_operators_l
def pick_random_op(side:Literal["attack", "defense"], rounds:int, exclusions:list = None, repeat:bool=False):
    if exclusions is None:
        exclusions = []
    logging.debug(f"pick random op:\tside: {side}\trepeat:{repeat}\trounds: {rounds}\texclusions: {exclusions}")
    v_op = valid_operators(side)
    operator = v_op[random.randint(0, len(v_op)-1)]
    while (operator in exclusions and len(v_op) > rounds-1) or (repeat and len(exclusions)!=0 and exclusions[-1] == operator):
        logging.debug(f"{operator} was already taken, retrying...")
        operator = v_op[random.randint(0, len(v_op)-1)]
    logging.debug(f"pick_random_operator({side}):{operator}")
    return operator
op_list = open_file()
def init():
    while True:
        try: 
            main()
        except FileNotFoundError:
            break
        tmp = input("")
        if tmp != "":
            os._exit(0)
init()