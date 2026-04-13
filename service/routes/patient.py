from flask import Blueprint, jsonify, request
from data import store

patient_bp = Blueprint("patient", __name__)


@patient_bp.route("/patient/create", methods=["POST"])
def create_patient():
    body = request.get_json(silent=True) or {}
    gender = body.get("gender")
    dob = body.get("dob")

    if not gender or not dob:
        return jsonify({"error": "gender and dob are required"}), 400

    new_id = max(store.patients.keys()) + 1 if store.patients else 1
    patient = {"id": new_id, "gender": gender, "dob": dob}
    store.patients[new_id] = patient
    store.conditions[new_id] = []

    return jsonify(patient), 201


@patient_bp.route("/patient/update", methods=["PUT"])
def update_patient():
    body = request.get_json(silent=True) or {}
    patient_id = body.get("id")

    if patient_id is None:
        return jsonify({"error": "id is required"}), 400

    patient = store.patients.get(patient_id)
    if patient is None:
        return jsonify({"error": "Patient not found"}), 404

    if "gender" in body:
        patient["gender"] = body["gender"]
    if "dob" in body:
        patient["dob"] = body["dob"]

    return jsonify(patient)


@patient_bp.route("/patient/list", methods=["GET"])
def list_patients():
    return jsonify(list(store.patients.values()))


@patient_bp.route("/patient/<int:patient_id>", methods=["GET"])
def get_patient(patient_id):
    patient = store.patients.get(patient_id)
    if patient is None:
        return jsonify({"error": "Patient not found"}), 404
    return jsonify(patient)


@patient_bp.route("/patient/<int:patient_id>/conditions", methods=["GET"])
def get_conditions(patient_id):
    if patient_id not in store.patients:
        return jsonify({"error": "Patient not found"}), 404
    return jsonify(store.conditions.get(patient_id, []))
