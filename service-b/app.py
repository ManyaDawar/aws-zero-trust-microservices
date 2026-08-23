from flask import Flask, jsonify
import os
import pymysql

app = Flask(__name__)

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


@app.route("/")
def home():
    return jsonify({
        "service": "Service B",
        "status": "running",
        "message": "Service B is reachable"
    })


@app.route("/health")
def health():
    return jsonify({
        "service": "Service B",
        "status": "healthy"
    })


@app.route("/db-health")
def db_health():
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            connect_timeout=5
        )

        connection.close()

        return jsonify({
            "service": "Service B",
            "database": "connected",
            "status": "healthy"
        })

    except Exception as e:
        return jsonify({
            "service": "Service B",
            "database": "connection failed",
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)