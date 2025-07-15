from flask import Blueprint, jsonify

ai_bp = Blueprint('ai_bp', __name__)

@ai_bp.route('/hello', methods=['GET'])
def hello():
    return jsonify({"message": "Hello from AI Plugin!"})
