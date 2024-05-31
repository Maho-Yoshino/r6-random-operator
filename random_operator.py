import random, json, os, logging, pprint
from datetime import datetime
from typing import Literal
import tkinter as tk
import tkinter.font as tkFont
# -============Logging=============-
logger = logging.getLogger(__name__)
filename = f"r6randomop_{str(datetime.now().date()).replace('-','_')}.log"
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
# -=====Open Operator List=========-
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
op_list = open_file()
# -==========GUI code==============-
root = tk.Tk()
root.title("R6 Random Operator Picker")
root.geometry("800x500")
root.resizable(0, 0)

def font_size(size:int):
    return tkFont.Font(size=size)
        
labels = []
def init():
    tk.Label(root, text="Select the gamemode:").grid(row=1,column=0)
    gmode=tk.StringVar()
    gmode.set("q")
    tk.Radiobutton(root, text="Quick match", variable=gmode, value="q").grid(row=2, column=0)
    tk.Radiobutton(root, text="Standard", variable=gmode, value="s").grid(row=3, column=0)
    tk.Radiobutton(root, text="Ranked", variable=gmode, value="r").grid(row=4, column=0)
    tk.Radiobutton(root, text="Single Operator", variable=gmode, value="o").grid(row=5, column=0)

    side = tk.StringVar()
    side.set("a")
    tk.Label(root, text="Select Starting side\n(Operator side in case of Single operator picking)").grid(row=6, column=0)
    tk.Radiobutton(root, text="Attack", variable=side, value="a").grid(row=7, column=0)
    tk.Radiobutton(root, text="Defense", variable=side, value="d").grid(row=8, column=0)

    repeat=tk.BooleanVar()
    repeat.set(True)
    tk.Label(root, text="Should the generated list have repeating operators?").grid(row=9, column=0)
    tk.Radiobutton(root, text="Yes", variable=repeat, value=True).grid(row=10, column=0)
    tk.Radiobutton(root, text="No", variable=repeat, value=False).grid(row=11, column=0)

    def data_processing(mode:Literal["a","d"], gamemode:Literal["q", "s", "r", "o"], repeating:bool):
        global labels
        if len(labels)!=0:
            for i in labels:
                i:tk.Widget
                i.grid_forget()
            labels = []
        mode = str(mode)
        mode = "attack" if mode.lower()=="a" else "defense"
        altmode = "defense" if mode.lower()=="a" else "attack"
        rounds = {
            "rounds_per_side":0,
            "OT":0
        }
        if gamemode == "q":
            rounds["rounds_per_side"] = 2
            rounds["OT"] = 1
            logging.info("Gamemode: Quick match")
        elif gamemode == "s":
            rounds["rounds_per_side"] = 3
            rounds["OT"] = 1
            logging.info("Gamemode: Standard")
        elif gamemode == "r":
            rounds["rounds_per_side"] = 3
            rounds["OT"] = 3
            logging.info("Gamemode: Ranked")
        elif gamemode == "o":
            return pick_random_op(mode, 1)
        operators = {
            "mode_normal":pick_random_op(mode, rounds["rounds_per_side"]),
            "altmode_normal":pick_random_op(altmode, rounds["rounds_per_side"]),
            "mode_OT":pick_random_op(mode, rounds["OT"]),
            "altmode_OT":pick_random_op(altmode, rounds["OT"])
        }
        for j in range(rounds["rounds_per_side"]*2+rounds["OT"]):
            if j in range(rounds["rounds_per_side"]*2):
                tmp = tk.Label(root, text=f"Round {j+1}", font=font_size(15), pady=10)
                labels.append(tmp)
                tmp.grid(column=3, row=j+1)
            else:
                tmp = tk.Label(root, text=f"Round {j+1} (OT)", font=font_size(15), pady=10)
                labels.append(tmp)
                tmp.grid(column=3, row=j+1)
            for col in range(5):
                if j<rounds["rounds_per_side"]:
                    tmp = tk.Label(root, text=operators["mode_normal"][j][col], pady=10)
                    labels.append(tmp)
                    tmp.grid(column=col+6, row=j+1)
                elif j<(rounds["rounds_per_side"]*2):
                    tmp = tk.Label(root, text=operators["altmode_normal"][j-rounds["rounds_per_side"]][col], pady=10)
                    labels.append(tmp)
                    tmp.grid(column=col+6, row=j+1)
                else:
                    j2 = j-(rounds["rounds_per_side"]*2+rounds["OT"])
                    tmp = tk.Label(root, text=operators["altmode_OT"][j2][col])
                    labels.append(tmp)
                    tmp.grid(column=col+6, row=j+1)
                    tmp = tk.Label(root, text=operators["mode_OT"][j2][col])
                    labels.append(tmp)
                    tmp.grid(column=col+6, row=j+2)
    def generate():
        errorlabel.config(text="")
        gmode_input = gmode.get()
        data_processing(side, gmode_input, bool(repeat))
    gen_button = tk.Button(root, text="Generate", command=generate)
    gen_button.grid(row=12,column=0)

    errorlabel = tk.Label(root, text="", fg="red", font=font_size(20))
    errorlabel.grid(row=15, column=0)

    gen_result_title = tk.Label(root, text="Results", font=font_size(15)).grid(row=0,column=6)

# -==========Old Code=============-
def valid_operators(side:Literal["attack", "defense"]):
    valid_operators_l = [operator for operator, owned in op_list[side].items() if owned]
    logging.debug(f"valid_operators({side}): {valid_operators_l}")
    return valid_operators_l
def pick_random_op(side:Literal["attack", "defense"], rounds:int, exclusions:list = None, repeat:bool=False):
    if exclusions is None:
        exclusions = []
    v_op = valid_operators(side)
    if (len(v_op)<2 and repeat) or (len(v_op)<5 and not repeat):
        logging.error(f"Not enough operators to start ({side})")
        raise ValueError(f"Not enough operators to start ({side})")
    #logging.debug(f"pick random op:\tside: {side}\trepeat:{repeat}\trounds: {rounds}\texclusions: {exclusions}")
    rounds_operators = []
    for _ in range(1, rounds+2):
        operators = []
        for _ in range(5):
            operator = v_op[random.randint(0, len(v_op)-1)]
            while (len(v_op)>2 and repeat and exclusions and operator != exclusions[-1]) or (len(v_op)>5 and not repeat and exclusions and operator not in exclusions)  :
                operator = v_op[random.randint(0, len(v_op)-1)]
            else:
                operators.append(operator)
            if len(v_op)>6:
                v_op.remove(operator)
            logging.debug(f"pick_random_operator({side}):{operator}")
        rounds_operators.append(operators)
    return rounds_operators
if __name__ == "__main__":
    init()
    root.mainloop()