import os
import sys
import pandas as pd
import requests
sys.dont_write_bytecode = True
from flask import (
    Flask, render_template, request, redirect, url_for, session, flash, jsonify
)
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
from database import (
    verificar_usuario,
    insertar_cliente_completo,
    obtener_todos_clientes_con_detalles,
    obtener_cliente_completo_por_id,
    actualizar_cliente_completo,
    eliminar_cliente_db,
    obtener_ultimo_codigo_cliente,
    insertar_proveedor_completo,
    obtener_todos_proveedores,
    obtener_proveedor_por_id,
    actualizar_proveedor,
    eliminar_proveedor_db,
    obtener_ultimo_codigo_proveedor
)

from pdf_generator import pdf_generator

# ==================== IMPORTAR MODELOS PARA KÁRDEX ====================
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import base64

app = Flask(__name__)

# Registrar blueprints existentes
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

# ==================== CONFIGURACIÓN SUPABASE PARA KÁRDEX ====================
DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    _a = base64.b64decode('cG9zdGdyZXNxbDovLy9wb3N0Z3Jlcy50a2Ztd3ZzZW52Z3B5ZXh2ZGNhdDphZG1pbjM1NjE5NjdrY2ZAYXdzLTEtdXMtZWFzdC0xLnBvb2xlci5zdXBhYmFzZS5jb206NjU0My9wb3N0Z3Jlcw==').decode('utf-8')
    DATABASE_URL = _a

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}

db = SQLAlchemy()
db.init_app(app)

# ==================== MODELOS PARA KÁRDEX ====================
class Producto(db.Model):
    __tablename__ = 'productos'
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50))
    familia = db.Column(db.String(100))
    marca = db.Column(db.String(100))
    descripcion = db.Column(db.Text)
    modelo = db.Column(db.String(100))
    unidad = db.Column(db.String(20))
    costo_unitario = db.Column(db.Numeric(10,2))
    precio_unitario = db.Column(db.Numeric(10,2))
    stock = db.Column(db.Integer, default=0)

class MovimientoStock(db.Model):
    __tablename__ = 'movimientos_stock'
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'))
    tipo = db.Column(db.String(20))
    cantidad = db.Column(db.Integer)
    motivo = db.Column(db.String(200))
    referencia = db.Column(db.String(100))
    costo_unitario = db.Column(db.Numeric(10,2))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# =========================
# Helpers (tus funciones existentes)
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
# Auth (tus rutas existentes)
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
            flash(f'Bienvenido/a {usuario_data["nombre_completo"]}!', "success")
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
# ENDPOINTS CLIENTES API (tus rutas existentes)
# =========================

@app.route("/api/clientes/guardar", methods=["POST"])
def api_guardar_cliente():
    try:
        data = request.get_json()
        if not data.get("razon_social"):
            return jsonify({"success": False, "error": "La razón social es obligatoria"})
        if not data.get("numero_documento"):
            return jsonify({"success": False, "error": "El número de documento es obligatorio"})
        if not data.get("contactos") or len(data.get("contactos")) == 0:
            return jsonify({"success": False, "error": "Agregue al menos un contacto"})
        if not data.get("puntos_entrega") or len(data.get("puntos_entrega")) == 0:
            return jsonify({"success": False, "error": "Agregue al menos un punto de entrega"})
        resultado = insertar_cliente_completo(data)
        return jsonify({
            "success": True,
            "data": resultado,
            "message": f'Cliente creado con código {resultado["codigo_cliente"]}'
        })
    except Exception as e:
        print(f"Error al guardar cliente: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route("/api/clientes/buscar", methods=["GET"])
def api_buscar_clientes():
    try:
        tipo_documento = request.args.get("tipo_documento", "")
        busqueda = request.args.get("busqueda", "")
        clientes = obtener_todos_clientes_con_detalles()
        if tipo_documento:
            clientes = [c for c in clientes if c.get("tipo_documento") == tipo_documento]
        if busqueda:
            busqueda_lower = busqueda.lower()
            clientes = [
                c for c in clientes 
                if busqueda_lower in c.get("razon_social", "").lower()
                or busqueda_lower in c.get("nombre_comercial", "").lower()
                or busqueda_lower in c.get("numero_documento", "")
                or busqueda_lower in c.get("codigo_cliente", "").lower()
            ]
        return jsonify({"success": True, "data": clientes})
    except Exception as e:
        print(f"Error al buscar clientes: {e}")
        return jsonify({"success": False, "data": [], "error": str(e)})

@app.route("/api/clientes/<int:cliente_id>", methods=["GET"])
def api_obtener_cliente(cliente_id):
    try:
        cliente = obtener_cliente_completo_por_id(cliente_id)
        if not cliente:
            return jsonify({"success": False, "error": "Cliente no encontrado"})
        return jsonify({"success": True, "data": cliente})
    except Exception as e:
        print(f"Error al obtener cliente: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route("/api/clientes/<int:cliente_id>", methods=["PUT"])
def api_actualizar_cliente(cliente_id):
    try:
        data = request.get_json()
        resultado = actualizar_cliente_completo(cliente_id, data)
        return jsonify({"success": True, "data": resultado, "message": "Cliente actualizado correctamente"})
    except Exception as e:
        print(f"Error al actualizar cliente: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route("/api/clientes/<int:cliente_id>", methods=["DELETE"])
def api_eliminar_cliente(cliente_id):
    try:
        resultado = eliminar_cliente_db(cliente_id)
        return jsonify({"success": True, "data": resultado, "message": "Cliente eliminado correctamente"})
    except Exception as e:
        print(f"Error al eliminar cliente: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route("/api/clientes/ultimo-codigo", methods=["GET"])
def api_ultimo_codigo():
    try:
        codigo = obtener_ultimo_codigo_cliente()
        return jsonify({"success": True, "ultimoCodigo": codigo})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# =========================
# ENDPOINTS PROVEEDORES API (tus rutas existentes)
# =========================

@app.route("/api/proveedores/guardar", methods=["POST"])
def api_guardar_proveedor():
    try:
        data = request.get_json()
        if not data.get("razon_social"):
            return jsonify({"success": False, "error": "La razón social es obligatoria"})
        if not data.get("ruc"):
            return jsonify({"success": False, "error": "El RUC es obligatorio"})
        if len(data.get("ruc", "")) != 11:
            return jsonify({"success": False, "error": "El RUC debe tener 11 dígitos"})
        if not data.get("direccion"):
            return jsonify({"success": False, "error": "La dirección es obligatoria"})
        resultado = insertar_proveedor_completo(data)
        return jsonify({
            "success": True,
            "data": resultado,
            "message": f'Proveedor creado con código {resultado["codigo_proveedor"]}'
        })
    except Exception as e:
        print(f"Error al guardar proveedor: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route("/api/proveedores/listar", methods=["GET"])
def api_listar_proveedores():
    try:
        proveedores = obtener_todos_proveedores()
        return jsonify({"success": True, "data": proveedores})
    except Exception as e:
        print(f"Error al listar proveedores: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route("/api/proveedores", methods=["GET"])
def api_buscar_proveedores():
    try:
        busqueda = request.args.get("busqueda", "")
        tipo = request.args.get("tipo_documento", "")
        proveedores = obtener_todos_proveedores()
        if busqueda:
            busqueda_lower = busqueda.lower()
            proveedores = [
                p for p in proveedores 
                if busqueda_lower in p.get("razon_social", "").lower()
                or busqueda_lower in p.get("ruc", "").lower()
                or busqueda_lower in p.get("codigo_proveedor", "").lower()
            ]
        return jsonify({"success": True, "data": proveedores})
    except Exception as e:
        print(f"Error al buscar proveedores: {e}")
        return jsonify({"success": False, "data": [], "error": str(e)})

@app.route("/api/proveedores/<int:id>", methods=["GET"])
def api_obtener_proveedor(id):
    try:
        proveedor = obtener_proveedor_por_id(id)
        if not proveedor:
            return jsonify({"success": False, "error": "Proveedor no encontrado"})
        return jsonify({"success": True, "data": proveedor})
    except Exception as e:
        print(f"Error al obtener proveedor: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route("/api/proveedores/<int:id>", methods=["PUT"])
def api_actualizar_proveedor(id):
    try:
        data = request.get_json()
        resultado = actualizar_proveedor(id, data)
        return jsonify({"success": True, "data": resultado, "message": "Proveedor actualizado correctamente"})
    except Exception as e:
        print(f"Error al actualizar proveedor: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route("/api/proveedores/<int:id>", methods=["DELETE"])
def api_eliminar_proveedor(id):
    try:
        resultado = eliminar_proveedor_db(id)
        return jsonify({"success": True, "data": resultado, "message": "Proveedor eliminado correctamente"})
    except Exception as e:
        print(f"Error al eliminar proveedor: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route("/api/proveedores/ultimo-codigo", methods=["GET"])
def api_ultimo_codigo_proveedor():
    try:
        codigo = obtener_ultimo_codigo_proveedor()
        return jsonify({"success": True, "ultimoCodigo": codigo})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# =========================
# ENDPOINT SUNAT
# =========================

@app.route("/api/sunat/consulta", methods=["GET"])
def api_consulta_sunat():
    ruc = request.args.get('ruc', '')
    print(f"🔍 Consultando RUC: {ruc}")
    if not ruc or len(ruc) != 11:
        return jsonify({'success': False, 'error': 'RUC inválido, debe tener 11 dígitos'})
    try:
        url = f'https://api.apis.net.pe/v1/ruc?numero={ruc}'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        }
        response = requests.get(url, timeout=15, headers=headers)
        print(f"📡 Status code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Datos recibidos: {data}")
            if data and data.get('nombre'):
                return jsonify({
                    'success': True,
                    'razon_social': data.get('nombre', ''),
                    'nombre_comercial': data.get('nombre', ''),
                    'direccion': data.get('direccion', ''),
                    'estado': data.get('estado', ''),
                    'condicion': data.get('condicion', ''),
                    'distrito': data.get('distrito', ''),
                    'provincia': data.get('provincia', ''),
                    'departamento': data.get('departamento', ''),
                    'ubigeo': data.get('ubigeo', '')
                })
            else:
                return jsonify({'success': False, 'error': 'No se encontraron datos para este RUC'})
        elif response.status_code == 404:
            return jsonify({'success': False, 'error': 'RUC no encontrado en SUNAT'})
        else:
            return jsonify({'success': False, 'error': f'Error en la consulta: Código {response.status_code}'})
    except requests.exceptions.Timeout:
        return jsonify({'success': False, 'error': 'Tiempo de espera agotado. Intente nuevamente.'})
    except requests.exceptions.ConnectionError:
        return jsonify({'success': False, 'error': 'Error de conexión. Verifique su internet.'})
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'success': False, 'error': str(e)})

# ==================== NUEVAS RUTAS PARA KÁRDEX ====================

@app.route('/api/productos', methods=['GET'])
def get_productos():
    print("📦 Llamada a /api/productos")
    try:
        productos = Producto.query.all()
        resultado = []
        for p in productos:
            resultado.append({
                'id': p.id,
                'codigo': p.codigo if p.codigo else f'P-{p.id}',
                'descripcion': p.descripcion if p.descripcion else '',
                'stock': p.stock if p.stock else 0,
                'costo_unitario': float(p.costo_unitario) if p.costo_unitario else 0
            })
        print(f"✅ {len(resultado)} productos encontrados")
        return jsonify(resultado)
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/movimientos_stock', methods=['GET'])
def get_movimientos():
    print("📊 Llamada a /api/movimientos_stock")
    try:
        producto_id = request.args.get('producto_id', type=int)
        print(f"Producto ID: {producto_id}")
        
        if producto_id:
            movimientos = MovimientoStock.query.filter_by(producto_id=producto_id).order_by(MovimientoStock.created_at.asc()).all()
        else:
            movimientos = []
        
        resultado = []
        for m in movimientos:
            resultado.append({
                'id': m.id,
                'producto_id': m.producto_id,
                'tipo': m.tipo,
                'cantidad': m.cantidad,
                'motivo': m.motivo if m.motivo else '',
                'referencia': m.referencia if m.referencia else '',
                'costo_unitario': float(m.costo_unitario) if m.costo_unitario else None,
                'created_at': m.created_at.isoformat() if m.created_at else None
            })
        print(f"✅ {len(resultado)} movimientos encontrados")
        return jsonify(resultado)
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/movimientos_stock', methods=['POST'])
def crear_movimiento():
    print("📝 POST a /api/movimientos_stock")
    try:
        data = request.get_json()
        print(f"Datos recibidos: {data}")
        
        if not data.get('producto_id'):
            return jsonify({'success': False, 'error': 'Producto ID requerido'}), 400
        
        if not data.get('tipo'):
            return jsonify({'success': False, 'error': 'Tipo requerido'}), 400
        
        if not data.get('cantidad') or int(data.get('cantidad')) <= 0:
            return jsonify({'success': False, 'error': 'Cantidad válida requerida'}), 400
        
        producto = Producto.query.get(data['producto_id'])
        if not producto:
            return jsonify({'success': False, 'error': 'Producto no encontrado'}), 404
        
        cantidad = int(data['cantidad'])
        
        if data['tipo'] == 'SALIDA' and (producto.stock or 0) < cantidad:
            return jsonify({'success': False, 'error': f'Stock insuficiente. Stock actual: {producto.stock or 0}'}), 400
        
        nuevo = MovimientoStock(
            producto_id=data['producto_id'],
            tipo=data['tipo'],
            cantidad=cantidad,
            motivo=data.get('motivo', ''),
            referencia=data.get('referencia', ''),
            costo_unitario=data.get('costo_unitario') if data.get('costo_unitario') else None
        )
        db.session.add(nuevo)
        
        if data['tipo'] == 'ENTRADA':
            producto.stock = (producto.stock or 0) + cantidad
        elif data['tipo'] == 'SALIDA':
            producto.stock = (producto.stock or 0) - cantidad
        elif data['tipo'] == 'AJUSTE':
            producto.stock = cantidad
        
        db.session.commit()
        print(f"✅ Movimiento registrado. Nuevo stock: {producto.stock}")
        
        return jsonify({'success': True, 'message': 'Movimiento registrado', 'nuevo_stock': producto.stock}), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/productos/<int:id>', methods=['GET'])
def get_producto(id):
    try:
        producto = Producto.query.get(id)
        if not producto:
            return jsonify({'error': 'Producto no encontrado'}), 404
        return jsonify({
            'id': producto.id,
            'codigo': producto.codigo,
            'descripcion': producto.descripcion,
            'stock': producto.stock or 0,
            'costo_unitario': float(producto.costo_unitario) if producto.costo_unitario else 0
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== RUTA PARA LA PÁGINA DE PRODUCTOS CON KÁRDEX ====================
@app.route('/mantenedor/productos')
def gestion_productos():
    try:
        productos = Producto.query.all()
        return render_template('gestion_productos.html', productos=productos)
    except Exception as e:
        return f"Error al cargar productos: {e}"

@app.route('/test')
def test():
    return jsonify({'status': 'ok', 'message': 'Kardex funcionando'})

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