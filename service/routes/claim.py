from flask import Blueprint, jsonify, request
from data import store

claim_bp = Blueprint("claim", __name__)

UPDATABLE_FIELDS = {"ehr_status", "clearing_house_status", "payer_status"}


@claim_bp.route("/claim/list", methods=["GET"])
def list_claims():
    return jsonify(list(store.claims.values()))


@claim_bp.route("/claim/<string:claim_id>", methods=["GET"])
def get_claim(claim_id):
    claim = store.claims.get(claim_id)
    if claim is None:
        return jsonify({"error": "Claim not found"}), 404
    return jsonify(claim)


@claim_bp.route("/claim/<string:claim_id>/update", methods=["PUT"])
def update_claim(claim_id):
    claim = store.claims.get(claim_id)
    if claim is None:
        return jsonify({"error": "Claim not found"}), 404

    body = request.get_json(silent=True) or {}
    unknown = set(body.keys()) - UPDATABLE_FIELDS
    if unknown:
        return jsonify({"error": f"Fields not allowed for update: {sorted(unknown)}"}), 400

    for field in UPDATABLE_FIELDS:
        if field in body:
            claim[field] = body[field]

    return jsonify(claim)
