import os
import sqlite3
import psycopg2
from datetime import datetime
from flask import Flask, render_template, request, Response

# App setup
app = Flask(__name__)

# Database configuration
# Use Postgres if POSTGRES_HOST is set (deployed in Kubernetes). Otherwise fallback to SQLite.
DB_PATH = os.environ.get("DATABASE_PATH", os.path.join(os.path.dirname(__file__), "operations.db"))
POSTGRES_HOST = os.environ.get("POSTGRES_HOST")
POSTGRES_PORT = os.environ.get("POSTGRES_PORT", "5432")
POSTGRES_DB = os.environ.get("POSTGRES_DB")
POSTGRES_USER = os.environ.get("POSTGRES_USER")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
USE_POSTGRES = bool(POSTGRES_HOST and POSTGRES_DB and POSTGRES_USER and POSTGRES_PASSWORD)


def pg_connect():
    return psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
    )


def init_postgres():
    conn = None
    cur = None
    try:
        conn = pg_connect()
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS operations (
                id SERIAL PRIMARY KEY,
                op_type VARCHAR(50) NOT NULL,
                num1 DOUBLE PRECISION,
                num2 DOUBLE PRECISION,
                result TEXT,
                success BOOLEAN,
                timestamp TIMESTAMPTZ DEFAULT NOW()
            )
            """
        )
        conn.commit()
    finally:
        try:
            if cur:
                cur.close()
        except Exception:
            pass
        try:
            if conn:
                conn.close()
        except Exception:
            pass



def init_db():
    """Create the operations table if it doesn't exist."""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS operations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                op_type TEXT NOT NULL,
                num1 REAL,
                num2 REAL,
                result TEXT,
                success INTEGER,
                timestamp TEXT
            )
            """
        )
        conn.commit()
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass


def save_operation(op_type: str, num1, num2, result, success: bool):
    """Persist a single operation into Postgres (if configured) or SQLite as fallback."""
    if USE_POSTGRES:
        conn = None
        cur = None
        try:
            conn = pg_connect()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO operations (op_type, num1, num2, result, success, timestamp) VALUES (%s, %s, %s, %s, %s, %s)",
                (op_type, num1, num2, str(result), bool(success), datetime.utcnow()),
            )
            conn.commit()
            return
        except Exception:
            try:
                if conn:
                    conn.rollback()
            except Exception:
                pass
        finally:
            try:
                if cur:
                    cur.close()
            except Exception:
                pass
            try:
                if conn:
                    conn.close()
            except Exception:
                pass

    # Fallback to SQLite
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO operations (op_type, num1, num2, result, success, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
            (op_type, num1, num2, str(result), int(bool(success)), datetime.utcnow().isoformat()),
        )
        conn.commit()
    except Exception:
        # Fail silently for persistence so the app remains responsive
        try:
            if conn:
                conn.rollback()
        except Exception:
            pass
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass


# Initialize DB at import time: prefer Postgres if configured, otherwise SQLite
try:
    if USE_POSTGRES:
        init_postgres()
    else:
        init_db()
except Exception:
    # If creation fails at build time (e.g., network or fs), the app will attempt again at runtime
    pass


@app.route("/")
def home():
    return render_template("index.html", result=None, operation=None)

@app.route("/sumar", methods=["GET", "POST"])
def sumar():
    result = None
    success = False
    if request.method == "POST":
        try:
            num1 = float(request.form["num1"])
            num2 = float(request.form["num2"])
            result = num1 + num2
            success = True
        except ValueError:
            result = "Error: Ingresa números válidos"
            num1 = None
            num2 = None
            success = False
        save_operation("suma", num1, num2, result, success)
    return render_template("index.html", result=result, operation="Suma")

@app.route("/restar", methods=["GET", "POST"])
def restar():
    result = None
    success = False
    if request.method == "POST":
        try:
            num1 = float(request.form["num1"])
            num2 = float(request.form["num2"])
            result = num1 - num2
            success = True
        except ValueError:
            result = "Error: Ingresa números válidos"
            num1 = None
            num2 = None
            success = False
        save_operation("resta", num1, num2, result, success)
    return render_template("index.html", result=result, operation="Resta")

@app.route("/multiplicar", methods=["GET", "POST"])
def multiplicar():
    result = None
    success = False
    if request.method == "POST":
        try:
            num1 = float(request.form["num1"])
            num2 = float(request.form["num2"])
            result = num1 * num2
            success = True
        except ValueError:
            result = "Error: Ingresa números válidos"
            num1 = None
            num2 = None
            success = False
        save_operation("multiplicacion", num1, num2, result, success)
    return render_template("index.html", result=result, operation="Multiplicación")

@app.route("/dividir", methods=["GET", "POST"])
def dividir():
    result = None
    success = False
    if request.method == "POST":
        try:
            num1 = float(request.form["num1"])
            num2 = float(request.form["num2"])
            if num2 == 0:
                result = "Error: División por cero"
                success = False
            else:
                result = num1 / num2
                success = True
        except ValueError:
            result = "Error: Ingresa números válidos"
            num1 = None
            num2 = None
            success = False
        save_operation("division", num1, num2, result, success)
    return render_template("index.html", result=result, operation="División")

@app.route('/custom-metrics', methods=["GET", "POST"])
def custom_metrics():
    # Custom metrics in Prometheus exposition format
    #retrieve some metric data from the database as an example
    sql_query = "SELECT COUNT(*) FROM operations;"
    database_counter = 0

    conn = None
    cur = None
    try:
        if USE_POSTGRES:
            conn = pg_connect()
            cur = conn.cursor()
            cur.execute(sql_query)
            database_counter = cur.fetchone()[0]
            cur.close()
            conn.close()
    finally:
        try:
            if cur:
                cur.close()
        except Exception:
            pass

    metrics_data = f"""
    # HELP database_usage Number of operations made in the app.
    # TYPE database_usage counter
    database_usage {database_counter}
    """
    return Response(metrics_data, mimetype='text/plain')


if __name__ == "__main__":
    # When running in a container with a Postgres DB we expect DATABASE_URL to be set
    # The app will create tables if possible and continue even if DB is temporarily unavailable
    app.run(debug=True, host="0.0.0.0", port=5000)
