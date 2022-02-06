from cProfile import run
from flask import Flask, redirect, render_template, send_file, send_from_directory, url_for, abort
import os, sys

cwd = os.getcwd()
sys.path.insert(0, os.path.join(cwd, 'V2'))
from generateAndCheck import runAll, runGen

app = Flask(__name__)
# Customize these two to your liking
# TODO: have an option to run indiviual testing to make the output prettier
#       or iterate through all balances and print them like the above code would have
@app.route("/runGeneration")
def runGeneration():
    # TODO: URGENT! Implement threading to fix signaling issue
    # ValueError: signal only works in main thread of the main interpreter
    runGen()
    redirect('/')

@app.route("/runGenCheck")
def runGenCheck():
    runAll()
    redirect('/')
 
@app.route('/', defaults={'req_path': ''})
@app.route('/<path:req_path>')

def dir_listing(req_path):
    BASE_DIR = os.path.dirname(os.path.realpath(__file__))
    STATIC_PATH = os.path.join(BASE_DIR, "static")
    print(STATIC_PATH)
    abs_path = os.path.join(STATIC_PATH, req_path)

    if not os.path.exists(abs_path):
        return abort(404)

    if os.path.isfile(abs_path):
        return send_file(abs_path)

    files = os.listdir(abs_path)
    return render_template('files.html', files=files)

if __name__ == "__main__":
    app.run()