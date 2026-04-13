import logging
from concurrent.futures import ThreadPoolExecutor

from flask import Flask
from routes.patient import patient_bp
from routes.account import account_bp
from routes.claim import claim_bp
from routes.bot import bot_bp
from bots.master_of_puppets import MasterOfPuppets

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.register_blueprint(patient_bp)
app.register_blueprint(account_bp)
app.register_blueprint(claim_bp)
app.register_blueprint(bot_bp)

mop = MasterOfPuppets(executor=ThreadPoolExecutor(max_workers=4))
app.extensions["mop"] = mop

if __name__ == "__main__":
    app.run(debug=True)
