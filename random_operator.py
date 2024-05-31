import random, json, os, logging
from datetime import datetime
from typing import Literal
# -============Logging=============-
logger = logging.getLogger(__name__)
filename = f"r6randomop_{str(datetime.now().date()).replace("-","_")}.log"
log_format = "%(asctime)s::%(levelname)-8s:%(message)s"
with open(filename, "w") as tmp:
    tmp.write("")
logging.basicConfig(filename=filename, encoding='utf-8', level=logging.DEBUG, format=log_format, datefmt="%H:%M:%S")
# -=============Debug==============-
debug:bool=False
if debug:
    json_name = "op_list.json"
else:
    json_name = "operator_list.json"
# -==========Main Code=============-
def main():
    mode, altmode, op_repeat, rounds = data_processing()
    if None in [mode, altmode, op_repeat, rounds]:
        return
    mode_ops = []
    altmode_ops = []
    rounds_per_side = rounds["rounds_per_side"]+rounds["OT"]
    for _ in range(rounds_per_side*5+1):
        mode_ops.append(pick_random_op(mode, rounds_per_side, mode_ops, True if op_repeat == "y" else False))
        altmode_ops.append(pick_random_op(altmode, rounds_per_side, altmode_ops, True if op_repeat == "y" else False))
    for j in range(1, rounds["rounds_per_side"]*2+rounds["OT"]+1):
        if j<=rounds["rounds_per_side"]:
            print(f"round {j} ({mode}): {';'.join(mode_ops[j-1])}")
        elif j>rounds["rounds_per_side"]*2:
            print(f"round {j} (overtime)")
            print(f"\t{mode}: {';'.join(mode_ops[j])}")
            print(f"\t{altmode}: {';'.join(altmode_ops[j])}")
        else:
            print(f"round {j} ({altmode}): {';'.join(altmode_ops[j-rounds["rounds_per_side"]-1])}")

def data_processing():
    if debug:
        return "attack","defense", False, {"rounds_per_side":2,"OT":1}
    else:
        mode = input("Mode: ").lower()
        if mode == "":
            logging.error("Invalid mode input")
            raise ValueError(f"Not a valid input (empty string)")
        mode = "attack" if mode[0].lower()=="a" else "defense"
        altmode = "defense" if mode == "attack" else "attack"
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
            return None, None, None, None
        else:
            logging.error("Invalid gamemode")
            raise ValueError("Invalid gamemode")
        op_repeat = input("Repeating operators?: ").lower()[0]
        return mode, altmode, op_repeat, rounds

def open_file():
    try: 
        with open(json_name, encoding="utf-8") as file:
            op_list = json.load(file)
            logging.info(f"{json_name} loaded")
    except FileNotFoundError:
        logger.critical(f"{json_name} missing")
        print(f"{json_name} does not exist")
    else:
        return op_list
def valid_operators(side:Literal["attack", "defense"]):
    valid_operators_l = [operator for operator, owned in op_list[side].items() if owned]
    logging.debug(f"valid_operators({side}): {valid_operators_l}")
    return valid_operators_l
def pick_random_op(side:Literal["attack", "defense"], rounds:int, exclusions:list = None, repeat:bool=False):
    if exclusions is None:
        exclusions = []
    operators = []
    v_op = valid_operators(side)
    if (len(v_op)<2 and repeat) or (len(v_op)<5 and not repeat):
        logging.error(f"Not enough operators to start ({side})")
        raise ValueError(f"Not enough operators to start ({side})")
    logging.debug(f"pick random op:\tside: {side}\trepeat:{repeat}\trounds: {rounds}\texclusions: {exclusions}")
    for _ in range(5):
        operator = v_op[random.randint(0, len(v_op)-1)]
        while (len(v_op)>2 and repeat and exclusions and operator != exclusions[-1]) or (len(v_op)>5 and not repeat and exclusions and operator not in exclusions):
            operator = v_op[random.randint(0, len(v_op)-1)]
        else:
            operators.append(operator)
        if len(v_op)>6:
            v_op.remove(operator)
        logging.debug(f"pick_random_operator({side}):{operator}")
    return operators
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
if __name__ == "__main__":
    init()