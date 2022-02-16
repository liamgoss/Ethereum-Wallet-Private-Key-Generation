#!/home/Ethereum-Wallet-Private-Key-Generation/nullenv/bin/python
# Added above Shebang for my linux service that auto runs this via crontab
# Will it mess things up for running normally? Unsure, but remove if desired

from json import load
from flask import Flask, current_app, redirect, render_template, send_file, send_from_directory, url_for, abort
import os, sys, threading
from pathlib import Path

currentLocation = Path(__file__).parent.resolve()

currentLocation = str(currentLocation)[:-10]
sys.path.append(os.path.join(currentLocation, 'V2'))

from generateAndCheck import runAll, runGen, runTransCount

app = Flask(__name__)
# TODO: have an option to run indiviual testing to make the output prettier
#       or iterate through all balances and print them like the above code would have


# Customize these page names two to your liking
@app.route("/runGeneration")
# Upon viewing this page, the command will run and you'll be sent back to the directory page (home)
def runGeneration():
    runGenThread = threading.Thread(target=runGen)
    runGenThread.start()
    runGenThread.join() # Uncomment this if you wish to have the page "load" until it's complete
    return redirect('/')
    

@app.route("/runGenCheck")
def runGenCheck():
    runAllThread = threading.Thread(target=runAll)
    runAllThread.start()
    #runAllThread.join() # Uncomment this if you wish to have the page "load" until it's complete
    return redirect('/')

@app.route("/runGenTrans")
def runGenTrans():
    runTransThread = threading.Thread(target=runTransCount)
    runTransThread.start()
    #runTransThread.join() # Uncomment this if you wish to have the page "load" until it's complete
    return redirect('/')


 
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
    app.run(host='0.0.0.0') # remove host='0.0.0.0' if you do NOT want this server exposed to the network!