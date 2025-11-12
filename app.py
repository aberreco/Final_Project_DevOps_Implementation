from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html", result=None, operation=None)

@app.route("/sumar", methods=["GET", "POST"])
def sumar():
    result = None
    if request.method == "POST":
        try:
            num1 = float(request.form["num1"])
            num2 = float(request.form["num2"])
            result = num1 + num2
        except ValueError:
            result = "Error: Ingresa números válidos"
    return render_template("index.html", result=result, operation="Suma")

@app.route("/restar", methods=["GET", "POST"])
def restar():
    result = None
    if request.method == "POST":
        try:
            num1 = float(request.form["num1"])
            num2 = float(request.form["num2"])
            result = num1 - num2
        except ValueError:
            result = "Error: Ingresa números válidos"
    return render_template("index.html", result=result, operation="Resta")

@app.route("/multiplicar", methods=["GET", "POST"])
def multiplicar():
    result = None
    if request.method == "POST":
        try:
            num1 = float(request.form["num1"])
            num2 = float(request.form["num2"])
            result = num1 * num2
        except ValueError:
            result = "Error: Ingresa números válidos"
    return render_template("index.html", result=result, operation="Multiplicación")

@app.route("/dividir", methods=["GET", "POST"])
def dividir():
    result = None
    if request.method == "POST":
        try:
            num1 = float(request.form["num1"])
            num2 = float(request.form["num2"])
            if num2 == 0:
                result = "Error: División por cero"
            else:
                result = num1 / num2
        except ValueError:
            result = "Error: Ingresa números válidos"
    return render_template("index.html", result=result, operation="División")

if __name__ == "__main__":
    app.run(debug=True)
