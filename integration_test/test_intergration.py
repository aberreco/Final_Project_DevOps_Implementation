import psycopg2
import os
import requests

# Configuración de la base de datos desde variables de entorno
DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "calculadora_db"),
    "port": os.getenv("POSTGRES_PORT", "5432"),
    "dbname": os.getenv("POSTGRES_DB", "calculadora"),
    "user": os.getenv("POSTGRES_USER", "calc"),
    "password": os.getenv("POSTGRES_PASSWORD", "calc"),
}

BASE_URL = "http://localhost:5000"

def get_last_operation():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT op_type, num1, num2, result, success FROM operations ORDER BY id DESC LIMIT 1;")
    row = cur.fetchone()
    conn.close()
    return row

def test_sumar():
    r = requests.post(f"{BASE_URL}/sumar", data={"num1": "10", "num2": "5"})
    assert r.status_code == 200
    assert "15.0" in r.text
    op = get_last_operation()
    assert op[0] == "suma"
    assert op[4] is True

def test_restar():
    r = requests.post(f"{BASE_URL}/restar", data={"num1": "10", "num2": "5"})
    assert r.status_code == 200
    assert "5.0" in r.text
    op = get_last_operation()
    assert op[0] == "resta"

def test_multiplicar():
    r = requests.post(f"{BASE_URL}/multiplicar", data={"num1": "3", "num2": "4"})
    assert r.status_code == 200
    assert "12.0" in r.text
    op = get_last_operation()
    assert op[0] == "multiplicacion"

def test_dividir():
    r = requests.post(f"{BASE_URL}/dividir", data={"num1": "10", "num2": "2"})
    assert r.status_code == 200
    assert "5.0" in r.text
    op = get_last_operation()
    assert op[0] == "division"

def test_dividir_por_cero():
    r = requests.post(f"{BASE_URL}/dividir", data={"num1": "10", "num2": "0"})
    assert "División por cero" in r.text
    op = get_last_operation()
    assert op[4] is False