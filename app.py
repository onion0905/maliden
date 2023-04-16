from flask import Flask, render_template, request
from os import remove
import utils

app = Flask(__name__)
# app._static_folder = ""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    filename = file.filename
    file.save(filename)

    disased_filepath = utils.disassemble_exe(filename)
    text_filepath = utils.gen_processed_file(disased_filepath)
    #fs = open(text_filepath, "r").read()
    
    #remove(filename)
    # remove(disased_filepath)
    # remove(text_filepath)

    ans = utils.keras_inference(text_filepath)
    if ans: return "malware"
    else: return "benign ware"

if __name__ == '__main__':
    app.run("0.0.0.0", debug=True)