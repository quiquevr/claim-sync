from flask import Flask
from routes.patient import patient_bp
from routes.account import account_bp
from routes.claim import claim_bp

app = Flask(__name__)
app.register_blueprint(patient_bp)
app.register_blueprint(account_bp)
app.register_blueprint(claim_bp)

if __name__ == "__main__":
    app.run(debug=True)
