import time
from flask import Blueprint, current_app, jsonify, request
from data import store

bot_bp = Blueprint("bot", __name__)


# ---------------------------------------------------------------------------
# GET /bot/types
# ---------------------------------------------------------------------------

@bot_bp.route("/bot/types", methods=["GET"])
def list_bot_types():
    return jsonify(list(store.bot_types.values()))


# ---------------------------------------------------------------------------
# GET /bot/<type>/account/list
# ---------------------------------------------------------------------------

@bot_bp.route("/bot/<string:bot_type>/account/list", methods=["GET"])
def list_bot_accounts(bot_type):
    if bot_type not in store.bot_types:
        return jsonify({"error": f"Unknown bot type: {bot_type}"}), 404

    instances = [
        inst for (t, _), inst in store.bot_instances.items()
        if t == bot_type
    ]
    return jsonify(instances)


# ---------------------------------------------------------------------------
# PUT /bot/<type>/account/<id>/schedule
# ---------------------------------------------------------------------------

@bot_bp.route("/bot/<string:bot_type>/account/<string:account_id>/schedule", methods=["PUT"])
def schedule_bot(bot_type, account_id):
    if bot_type not in store.bot_types:
        return jsonify({"error": f"Unknown bot type: {bot_type}"}), 404

    body = request.get_json(silent=True) or {}
    schedule = body.get("schedule", {})
    next_exec_date = int(time.time()) + schedule.get("interval_minutes", 60) * 60

    key = (bot_type, account_id)
    if key in store.bot_instances:
        instance = store.bot_instances[key]
        instance["schedule"] = schedule
        instance["max_concurrent_jobs"] = body.get("max_concurrent_jobs", instance["max_concurrent_jobs"])
        instance["priority"] = body.get("priority", instance["priority"])
        instance["next-exec-date"] = next_exec_date
        instance["status"] = "SCHEDULED"
    else:
        instance_id = store._bot_instance_id_seq
        store._bot_instance_id_seq += 1
        instance = {
            "bot-instance-id": instance_id,
            "bot_type": bot_type,
            "account_id": account_id,
            "schedule": schedule,
            "max_concurrent_jobs": body.get("max_concurrent_jobs", 1),
            "priority": body.get("priority", "normal"),
            "next-exec-date": next_exec_date,
            "stats": {"processed": 0},
            "status": "SCHEDULED",
        }
        store.bot_instances[key] = instance

    mop = current_app.extensions["mop"]
    mop.schedule(bot_type, account_id)

    return jsonify({
        "bot-instance-id": instance["bot-instance-id"],
        "next-exec-date": instance["next-exec-date"],
    })


# ---------------------------------------------------------------------------
# POST /bot/<type>/account/<id>/kill
# ---------------------------------------------------------------------------

@bot_bp.route("/bot/<string:bot_type>/account/<string:account_id>/kill", methods=["POST"])
def kill_bot(bot_type, account_id):
    if bot_type not in store.bot_types:
        return jsonify({"error": f"Unknown bot type: {bot_type}"}), 404

    key = (bot_type, account_id)
    instance = store.bot_instances.get(key)
    if instance is None:
        return jsonify({"error": "Bot instance not found"}), 404

    instance["status"] = "KILLED"
    instance["next-exec-date"] = None

    return jsonify({
        "bot-instance-id": instance["bot-instance-id"],
        "next-exec-date": None,
    })


# ---------------------------------------------------------------------------
# GET /bot/<type>/account/<id>/status
# ---------------------------------------------------------------------------

@bot_bp.route("/bot/<string:bot_type>/account/<string:account_id>/status", methods=["GET"])
def bot_status(bot_type, account_id):
    if bot_type not in store.bot_types:
        return jsonify({"error": f"Unknown bot type: {bot_type}"}), 404

    key = (bot_type, account_id)
    instance = store.bot_instances.get(key)
    if instance is None:
        return jsonify({"error": "Bot instance not found"}), 404

    return jsonify({
        "bot-instance-id": instance["bot-instance-id"],
        "next-exec-date": instance["next-exec-date"],
        "stats": instance["stats"],
        "status": instance["status"],
    })


# ---------------------------------------------------------------------------
# POST /puppet/master-of/start-all
# ---------------------------------------------------------------------------

@bot_bp.route("/puppet/master-of/start-all", methods=["POST"])
def start_all():
    mop = current_app.extensions["mop"]
    count = len(mop.schedule_entries)
    for instance in store.bot_instances.values():
        schedule = instance.get("schedule", {})
        instance["next-exec-date"] = int(time.time()) + schedule.get("interval_minutes", 60) * 60
        instance["status"] = "SCHEDULED"
    mop.restart_all()
    return jsonify({"affected": count})


# ---------------------------------------------------------------------------
# POST /puppet/master-of/kill-em-all
# ---------------------------------------------------------------------------

@bot_bp.route("/puppet/master-of/kill-em-all", methods=["POST"])
def kill_all():
    mop = current_app.extensions["mop"]
    count = len(mop.workers)
    for instance in store.bot_instances.values():
        instance["status"] = "KILLED"
        instance["next-exec-date"] = None
    mop.cancel_all()
    return jsonify({"affected": count})
