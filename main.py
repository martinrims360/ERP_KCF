import os
import sys
sys.dont_write_bytecode = True

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, jsonify, send_from_directory
)
from functools import wraps

from database import (
    init_db,
    verificar_usuario,

    # mantenedor
    obtener_clientes_completos,
    obtener_proveedores,
    obtener_productos,
    insertar_cliente,
    insertar_contacto_cliente,
    insertar_punto_entrega,
    insertar_proveedor,
    insertar_producto,

    # api integración
    buscar_clientes,
    buscar_productos,
    obtener_cliente_completo_por_id,
    obtener_producto_completo_por_id,

    # cotizaciones
    obtener_cotizaciones_recientes,
    crear_cotizacion_transaccional,
    obtener_cotizacion_completa,
)

from pdf_generator import pdf_generator

app = Flask(__name__)
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

            if session.get("rol") == "administrador":
                return f(*args, **kwargs)

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
# Inicializar DB
# =========================
init_db()


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
        rol = request.form.get("rol", "")

        usuario_data = verificar_usuario(usuario, password)
        if usuario_data and usuario_data["rol"] == rol:
            session["usuario"] = usuario_data["usuario"]
            session["rol"] = usuario_data["rol"]
            session["nombre_completo"] = usuario_data["nombre_completo"]
            session["usuario_id"] = usuario_data["id"]

            flash(f'Bienvenido/a {usuario_data["nombre_completo"]}!', "success")
            return redirect(url_for("index"))

        flash("Usuario, contraseña o rol incorrectos", "error")

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
# Módulo Cotización
# =========================
@app.route("/cotizacion")
def cotizacion():
    cotizaciones = obtener_cotizaciones_recientes(limit=300)
    return render_template("listado_cotizaciones.html", cotizaciones=cotizaciones)


@app.route("/cotizacion/nueva")
def nueva_cotizacion():
    return render_template("cotizacion_oc/crear_cotizacion.html")


@app.route("/cotizacion/consultar/<int:cotizacion_id>")
def cotizacion_consultar(cotizacion_id: int):
    return render_template(
        "cotizacion_oc/crear_cotizacion.html",
        cotizacion_id=cotizacion_id,
        modo="consulta"
    )


@app.route("/cotizacion/comercial")
def cotizacion_comercial():
    return render_template("cotizacion_oc/cotizacion_comercial.html")


@app.route("/orden-compra/proveedor")
def orden_compra_proveedor():
    return render_template("cotizacion_oc/generar_orden_compra.html")


@app.route("/compras/directas")
def compras_directas():
    return render_template("cotizacion_oc/compras_directas.html")


# =========================
# Módulos (futuros)
# =========================
@app.route("/almacen")
def almacen():
    return "Aquí va el módulo de Almacén - Próximamente"


@app.route("/historial")
def historial():
    return "Aquí va el módulo de Historial - Próximamente"


@app.route("/kpis")
def kpis():
    return "Aquí va el módulo de KPIs - Próximamente"


# =========================
# Mantenedor (maestros)
# =========================
@app.route("/mantenedor")
def mantenedor():
    return render_template("mantenedor.html")


@app.route("/mantenedor/productos")
@requiere_permiso("productos", "ver")
def gestion_productos():
    productos = obtener_productos()
    return render_template("mantenedor/gestion_productos.html", productos=productos)


@app.route("/mantenedor/productos/nuevo", methods=["GET", "POST"])
@requiere_permiso("productos", "crear")
def nuevo_producto():
    if request.method == "POST":
        familia = request.form["familia"]
        descripcion = request.form["descripcion"]
        descripcion_larga = request.form.get("descripcion_larga", "")
        marca = request.form.get("marca", "")
        modelo = request.form.get("modelo", "")
        unidad = request.form["unidad"]

        codigo_generado = insertar_producto(
            familia, descripcion, descripcion_larga, marca, modelo, unidad
        )
        flash(f"Producto creado exitosamente con código: {codigo_generado}", "success")
        return redirect(url_for("gestion_productos"))

    return render_template("mantenedor/nuevo_producto.html")


@app.route("/mantenedor/proveedores")
@requiere_permiso("proveedores", "ver")
def gestion_proveedores():
    proveedores = obtener_proveedores()
    return render_template("mantenedor/gestion_proveedores.html", proveedores=proveedores)


@app.route("/mantenedor/proveedores/nuevo", methods=["GET", "POST"])
@requiere_permiso("proveedores", "crear")
def nuevo_proveedor():
    if request.method == "POST":
        razon_social = request.form["razon_social"]
        ruc = request.form["ruc"]
        direccion = request.form["direccion"]
        telefono = request.form.get("telefono", "")
        contacto = request.form.get("contacto", "")
        email = request.form.get("email", "")

        insertar_proveedor(razon_social, ruc, direccion, telefono, contacto, email)
        flash("Proveedor creado exitosamente", "success")
        return redirect(url_for("gestion_proveedores"))

    return render_template("mantenedor/nuevo_proveedor.html")


@app.route("/mantenedor/clientes")
@requiere_permiso("clientes", "ver")
def gestion_clientes():
    clientes = obtener_clientes_completos()
    return render_template("mantenedor/gestion_clientes.html", clientes=clientes)


@app.route("/mantenedor/clientes/nuevo", methods=["GET", "POST"])
@requiere_permiso("clientes", "crear")
def nuevo_cliente():
    if request.method == "POST":
        tipo_documento = request.form["tipo_documento"]
        numero_documento = request.form["numero_documento"]
        razon_social = request.form["razon_social"]
        direccion_fiscal = request.form["direccion_fiscal"]

        cliente_id = insertar_cliente(tipo_documento, numero_documento, razon_social, direccion_fiscal)

        # contactos
        contactos = {}
        for key, value in request.form.items():
            if key.startswith("contactos["):
                parts = key.split("[")
                if len(parts) >= 3:
                    index = parts[1].rstrip("]")
                    field = parts[2].rstrip("]")
                    contactos.setdefault(index, {})[field] = value

        for contacto_data in contactos.values():
            if contacto_data.get("nombre"):
                principal = "principal" in contacto_data
                insertar_contacto_cliente(
                    cliente_id,
                    contacto_data["nombre"],
                    contacto_data.get("email", ""),
                    contacto_data.get("telefono", ""),
                    contacto_data.get("cargo", ""),
                    principal
                )

        # puntos de entrega
        puntos = {}
        for key, value in request.form.items():
            if key.startswith("puntos_entrega["):
                parts = key.split("[")
                if len(parts) >= 3:
                    index = parts[1].rstrip("]")
                    field = parts[2].rstrip("]")
                    puntos.setdefault(index, {})[field] = value

        for punto_data in puntos.values():
            if punto_data.get("nombre"):
                principal = "principal" in punto_data
                insertar_punto_entrega(
                    cliente_id,
                    punto_data["nombre"],
                    punto_data["direccion"],
                    punto_data.get("departamento", ""),
                    punto_data.get("provincia", ""),
                    punto_data.get("distrito", ""),
                    punto_data.get("telefono", ""),
                    punto_data.get("responsable", ""),
                    principal
                )

        flash("Cliente creado exitosamente", "success")
        return redirect(url_for("gestion_clientes"))

    return render_template("mantenedor/nuevo_cliente.html")


# =========================
# API - Integración Cotización ↔ Mantenedor
# =========================
@app.route("/api/clientes/buscar")
def api_buscar_clientes():
    q = request.args.get("q", "")
    return jsonify({"success": True, "data": buscar_clientes(q)})


@app.route("/api/productos/buscar")
def api_buscar_productos():
    q = request.args.get("q", "")
    return jsonify({"success": True, "data": buscar_productos(q)})


@app.route("/api/clientes/<int:cliente_id>")
def api_cliente_por_id(cliente_id: int):
    data = obtener_cliente_completo_por_id(cliente_id)
    if not data:
        return jsonify({"success": False, "error": "Cliente no encontrado"}), 404
    return jsonify({"success": True, "data": data})


@app.route("/api/productos/<int:producto_id>")
def api_producto_por_id(producto_id: int):
    data = obtener_producto_completo_por_id(producto_id)
    if not data:
        return jsonify({"success": False, "error": "Producto no encontrado"}), 404
    return jsonify({"success": True, "data": data})


# =========================
# API - Cotizaciones
# =========================
@app.route("/api/cotizacion/guardar", methods=["POST"])
def api_guardar_cotizacion():
    if "usuario" not in session:
        return jsonify({"success": False, "error": "No autorizado"}), 401

    try:
        payload = request.get_json() or {}
        result = crear_cotizacion_transaccional(payload, usuario_id=session["usuario_id"])
        return jsonify({"success": True, "data": result})
    except ValueError as ve:
        return jsonify({"success": False, "error": str(ve)}), 400
    except Exception as e:
        return jsonify({"success": False, "error": f"Error del servidor: {str(e)}"}), 500


@app.route("/api/cotizaciones/<int:cotizacion_id>")
def api_get_cotizacion(cotizacion_id: int):
    try:
        data = obtener_cotizacion_completa(cotizacion_id)
        if not data:
            return jsonify({"success": False, "error": "Cotización no encontrada"}), 404
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# =========================
# PDF
# =========================
@app.route("/generar-pdf", methods=["POST"])
def generar_pdf():
    try:
        datos_documento = request.get_json() or {}
        pdf_path = pdf_generator.generar_pdf_universal(datos_documento)
        if pdf_path:
            return jsonify({
                "success": True,
                "pdf_path": pdf_path,
                "message": "PDF generado exitosamente"
            })
        return jsonify({"success": False, "message": "Error al generar PDF"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"})


@app.route("/pdf/<int:cotizacion_id>", methods=["GET"])
def generar_pdf_cotizacion(cotizacion_id):
    try:
        print(f"Generando PDF para cotización ID: {cotizacion_id}")
        # Obtener datos completos de la cotización
        datos_cotizacion = obtener_cotizacion_completa(cotizacion_id)
        if not datos_cotizacion:
            print("Cotización no encontrada")
            return "Cotización no encontrada", 404
        
        print(f"Datos obtenidos: {datos_cotizacion.keys()}")
        # Agregar tipo_documento para el generador
        datos_cotizacion['tipo_documento'] = 'cotizacion'
        
        # Generar PDF
        pdf_path = pdf_generator.generar_pdf_universal(datos_cotizacion)
        if pdf_path:
            print(f"PDF generado: {pdf_path}")
            return send_from_directory(".", pdf_path, as_attachment=True, download_name=pdf_path)
        else:
            print("Error al generar PDF")
            return "Error al generar PDF", 500
    except Exception as e:
        print(f"Error en generar_pdf_cotizacion: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Error: {str(e)}", 500


@app.route("/pdfs/<path:filename>")
def serve_pdf(filename):
    return send_from_directory(".", filename)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)