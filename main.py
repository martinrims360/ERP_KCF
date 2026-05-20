import os
import sys
import pandas as pd
sys.dont_write_bytecode = True
from flask import (
    Flask, render_template, request, redirect, url_for,session, flash)
from functools import wraps
from routes.clientes import clientes_bp
from routes.productos import productos_bp
from routes.cotizaciones import cotizaciones_bp
from routes.proveedores import proveedores_bp
from routes.mantenedor_productos import mantenedor_productos_bp
from routes.usuarios import usuarios_bp
from routes.mantenedor_principal import mantenedor_principal_bp
from routes.mantenedor_clientes import mantenedor_clientes_bp
from routes.mantenedor_proveedores import mantenedor_proveedores_bp
from routes.mantenedor_usuarios import mantenedor_usuarios_bp
from database import (
    verificar_usuario,
)

from pdf_generator import pdf_generator

app = Flask(__name__)
app.register_blueprint(clientes_bp)
app.register_blueprint(proveedores_bp)
app.register_blueprint(productos_bp)
app.register_blueprint(cotizaciones_bp)
app.register_blueprint(mantenedor_productos_bp)
app.register_blueprint(usuarios_bp)
app.register_blueprint(mantenedor_principal_bp)
app.register_blueprint(mantenedor_clientes_bp)
app.register_blueprint(mantenedor_usuarios_bp)
app.register_blueprint(mantenedor_proveedores_bp)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-only-change-me")


# =========================
# Helpers
# =========================
def formato_moneda_soles(valor):
    try:
        if valor is None:
            return "0.00"
        if isinstance(valor, str):
            v = valor.replace(",", "").strip()
            if not v:
                return "0.00"
            numero = float(v)
        else:
            numero = float(valor)
        return "{:,.2f}".format(numero)
    except (ValueError, TypeError):
        return "0.00"


app.jinja_env.filters["formato_soles"] = formato_moneda_soles


def requiere_permiso(modulo, accion="ver"):

    def decorator(f):

        @wraps(f)
        def decorated_function(*args, **kwargs):

            if "usuario" not in session:
                return redirect(url_for("login"))

            # =========================
            # ADMINISTRADOR
            # =========================
            if session.get("rol") == "administrador":
                return f(*args, **kwargs)

            # =========================
            # USUARIO NORMAL
            # =========================
            if session.get("rol") == "usuario":

                permisos_usuario = {
                    "productos": ["crear", "ver"],
                    "proveedores": ["crear", "ver"],
                    "clientes": ["crear", "ver"],
                    "precios": ["crear", "ver"],
                    "usuarios": []
                }

                if modulo in permisos_usuario and accion in permisos_usuario[modulo]:
                    return f(*args, **kwargs)

            flash("No tiene permisos para realizar esta acción", "error")
            return redirect(url_for("mantenedor"))

        return decorated_function

    return decorator


@app.before_request
def require_login():

    allowed_routes = {"login", "static", "logout"}

    if request.endpoint and request.endpoint not in allowed_routes:
        if "usuario" not in session:
            return redirect(url_for("login"))


# =========================
# Auth
# =========================
@app.route("/")
def root():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():

    if "usuario" in session:
        return redirect(url_for("index"))

    if request.method == "POST":

        usuario = request.form.get("usuario", "").strip()
        password = request.form.get("password", "")

        usuario_data = verificar_usuario(usuario, password)

        if usuario_data:

            session["usuario"] = usuario_data["usuario"]
            session["rol"] = usuario_data["rol"]
            session["nombre_completo"] = usuario_data["nombre_completo"]
            session["usuario_id"] = usuario_data["id"]

            flash(
                f'Bienvenido/a {usuario_data["nombre_completo"]}!',
                "success"
            )

            return redirect(url_for("index"))

        flash("Usuario o contraseña incorrectos", "error")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Has cerrado sesión correctamente", "info")
    return redirect(url_for("login"))


@app.route("/index")
def index():
    return render_template("index.html")

# =========================
# Ejecutar
# =========================
if __name__ == "__main__":

    host = "0.0.0.0"
    port = 5000

    print(f"🚀 Servidor corriendo en:")
    print(f"👉 http://localhost:{port}")
    print(f"👉 http://127.0.0.1:{port}")

    app.run(
        debug=True,
        host=host,
        port=port
    )
    
