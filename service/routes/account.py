from flask import Blueprint, jsonify
from data import store

account_bp = Blueprint("account", __name__)


@account_bp.route("/account/list", methods=["GET"])
def list_accounts():
    return jsonify(list(store.accounts.values()))


@account_bp.route("/account/<string:account_id>", methods=["GET"])
def get_account(account_id):
    account = store.accounts.get(account_id)
    if account is None:
        return jsonify({"error": "Account not found"}), 404
    return jsonify(account)
