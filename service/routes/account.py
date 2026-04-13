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


@account_bp.route("/account/<string:account_id>/bot/<string:bot_type>/config", methods=["GET"])
def get_account_bot_config(account_id, bot_type):
    if store.accounts.get(account_id) is None:
        return jsonify({"error": "Account not found"}), 404
    if bot_type not in store.bot_types:
        return jsonify({"error": f"Unknown bot type: {bot_type}"}), 404
    configs = store.account_bot_configs.get((account_id, bot_type), [])
    return jsonify(configs)
