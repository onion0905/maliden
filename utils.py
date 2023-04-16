import re
import r2pipe
import pickle
import numpy as np
from tensorflow import keras

def _get_newline(line):  #line: str
    if line.startswith(";") or line == "":
        return ""
    ans = re.sub("\.", "_", line)  # 點替換成底線
    ans = re.sub("fcn_.*", "fcn_num", ans)
    ans = re.sub("[,.!?;*()]", "", ans)  # 去除所有標點符號
    ans = re.sub("\[.*]", "address", ans)  # 所有[.*]變成 address
    ans = ans.lower()
    line_words = list(filter(None, re.split('[ ,.!?;*()]', ans)))
    new_line_words = []
    i = -1
    while i < len(line_words):
        i += 1
        if i >= len(line_words):
            break
        instruction = line_words[i]  # 單一 word
        if instruction.startswith("0x") and i-1>=0 and line_words[i-1][0] == "j":
            new_line_words.append("address")
        elif instruction.startswith("0x") or (len(instruction)==1 and instruction.isnumeric()):
            new_line_words.append("number")
        else:
            new_line_words.append(instruction)

    new_line = " ".join(new_line_words)
    return new_line


def gen_processed_file(filepath):
    fp = open(filepath, "r").readlines()
    new_lines = []
    for line in fp:
        line = line.strip()
        if len(line) <= 12:
            pass
        elif line[12] == ";":
            pass
        elif line[0] == "/":  # start of a function
            linesp = line.split()
            function_name = linesp[2]
            if linesp[2] == "int" or linesp[2] == "void": 
                    function_name = linesp[3]
            new_lines.append(_get_newline(line[7:]))
        else:
            disased = " ".join(line[12:].split()[2:])
            if len(disased) == 0 or disased[0] == ";":
                pass
            else:
                ans = _get_newline(disased)
                new_lines.append(ans)
    print(len(new_lines))
    with open(f"text_{filepath[6:-4]}.txt", "a") as fw:
        for line in new_lines:
            fw.write(line + " ")

    return f"text_{filepath[6:-4]}.txt"


def disassemble_exe(filepath):
    r = r2pipe.open(filepath)
    r.cmd("aaa")
    r.cmd("afl")
    r.cmd("e asm.comments=False")
    print(f"disas_{filepath[:-4]}.txt")
    r.cmd(f"pdf @@f > disas_{filepath[:-4]}.txt")
    return f"disas_{filepath[:-4]}.txt"


def keras_inference(filepath):
    model_path = "keras_model\\binary_2gram.keras"
    text_layer_path = "keras_model\\text_vectorization_2gram.pickle"
    from_disk = pickle.load(open(text_layer_path, "rb"))
    text_vectorization = keras.layers.TextVectorization.from_config(from_disk['config'])
    text_vectorization.set_weights(from_disk['weights'])
    model = keras.models.load_model(model_path)
    
    data = open(filepath, "r").read()
    x = text_vectorization(data)
    input_data = np.random.rand(1, 20000)
    input_data[0] = x.numpy()

    ans = model.predict(input_data)
    if ans[0][0] >= 0.5: return True
    else: return False