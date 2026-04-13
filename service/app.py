from flask import Flask
from routes.patient import patient_bp
from routes.account import account_bp

app = Flask(__name__)
app.register_blueprint(patient_bp)
app.register_blueprint(account_bp)

if __name__ == "__main__":
    app.run(debug=True)
