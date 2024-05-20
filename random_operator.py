import random, json, os, logging, math
from datetime import datetime
from typing import Literal
logger = logging.getLogger(__name__)
now = datetime.now()
now_time = now.time()
filename = f"r6randomop_{str(now.date()).replace("-","_")}_{now.hour}_{now.minute}.log"
logging.basicConfig(filename=filename, encoding='utf-8', level=logging.DEBUG)
def main():
    mode = input("Mode: ").lower()
    if mode[0] == "a":
        mode = "attack"
        logging.info("Mode: attack")
    elif mode[0] == "d":
        mode = "defense"
        logging.info("Mode: defense")
    else:
        logging.error("Invalid mode input")
        raise ValueError(f"Not a valid input \"{mode}\"")
    rounds = 0
    gmode = input("Gamemode: ").lower()[0]
    if gmode == "q":
        rounds = 5
        logging.info("Gamemode: Quick match")
    elif gmode == "s":
        rounds = 7
        logging.info("Gamemode: Standard")
    elif gmode == "r":
        rounds = 9
        logging.info("Gamemode: Ranked")
    else:
        logging.error("Invalid gamemode")
        raise ValueError("Invalid gamemode")
    for i in range(1, rounds+1):
        if i == rounds:
            print(f"Attacker (round {i} (OT)): {pick_random_op('attack')}")
            print(f"Defender: (round {i}  (OT)): {pick_random_op('defense')}")
        elif math.floor(rounds/2)<i:
            print(f"Attacker (round {i}): {pick_random_op('attack')}")
        else:
            print(f"Defender: (round {i//2}): {pick_random_op('defense')}")


def open_file():
    try: 
        with open("operator_list.json", encoding="utf-8") as file:
            op_list = json.load(file)
            logging.info("operator_list.json loaded")
    except FileNotFoundError:
        logger.critical("operator_list.json missing")
        print("operator_list.json does not exist")
        raise FileNotFoundError
    return op_list
def valid_operators(side:Literal["attack", "defense"]):
    valid_operators_l = []
    for role, operators in op_list.items():
        for operator, owned in operators.items():
            if role == side and owned:
                valid_operators_l.append(operator)
    return valid_operators_l
def pick_random_op(side:Literal["attack", "defense"]):
    v_op = valid_operators(side)
    return v_op[random.randint(0, len(v_op)-1)]
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