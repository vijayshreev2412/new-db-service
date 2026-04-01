from flask import Flask, jsonify, request
import logging
import ddtrace

app = Flask(__name__)
ddtrace.patch_all()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/health')
def health():
    return jsonify({"status": "ok"})

@app.route('/demo-error')
def demo_error():
    mode = request.args.get('mode')
    total = 100
    bucket = 1

    if mode == 'zero_division':
        bucket = 0

    if bucket == 0:
        logger.error("Division by zero attempt blocked")
        return jsonify({"error": "Division by zero attempt"}), 400

    try:
        result = total / bucket
        return jsonify({"result": result})
    except ZeroDivisionError:
        logger.error("ZeroDivisionError caught")
        return jsonify({"error": "Division by zero error"}), 400

@app.route('/checkout')
def checkout():
    return jsonify({"status": "checkout ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
