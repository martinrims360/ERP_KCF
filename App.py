from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# ==================== CONFIGURACIÓN SUPABASE CORREGIDA ====================
DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    DATABASE_URL = "postgresql://postgres.tkfmwvsenvgpyexvdcat:admin3561967kcf@aws-1-us-east-1.pooler.supabase.com:6543/postgres"

# Limpiar URL si tiene prefijo incorrecto
if DATABASE_URL and DATABASE_URL.startswith("postgresql+psycopg2://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql+psycopg2://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'sb_secret_k56lhPYVINqZMj_BZexRbw_JzeBx8Hx'

app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 5,
    'pool_recycle': 300,
    'pool_pre_ping': True,
    'pool_use_lifo': True,
    'connect_args': {
        'connect_timeout': 10,
        'keepalives': 1,
        'keepalives_idle': 30,
        'keepalives_interval': 10,
        'keepalives_count': 5
    }
}

db = SQLAlchemy()
db.init_app(app)

# ==================== IMPORTAR MODELOS ====================
from models.producto import Producto
from models.movimiento_stock import MovimientoStock
from datetime import datetime

# ==================== RUTAS DE PÁGINAS HTML ====================

@app.route('/')
def home():
    return jsonify({'message': 'Servidor funcionando', 'status': 'ok'})

@app.route('/crear_cotizacion')
def crear_cotizacion():
    """Página para crear/editar cotizaciones"""
    return render_template('crear_cotizacion.html')

@app.route('/listado_cotizaciones')
def listado_cotizaciones():
    """Página de listado de cotizaciones"""
    return render_template('listado_cotizaciones.html')

# ==================== RUTAS PARA PRODUCTOS ====================

@app.route('/api/productos', methods=['GET'])
def get_productos():
    print("📦 Llamada a /api/productos")
    try:
        productos = Producto.query.all()
        resultado = []
        for p in productos:
            resultado.append({
                'id': p.id,
                'codigo': p.codigo if hasattr(p, 'codigo') else '',
                'descripcion': p.descripcion,
                'stock': p.stock if hasattr(p, 'stock') else 0,
                'costo_unitario': float(p.costo_unitario) if hasattr(p, 'costo_unitario') and p.costo_unitario else 0,
                'familia': p.familia if hasattr(p, 'familia') else '',
                'marca': p.marca if hasattr(p, 'marca') else '',
                'modelo': p.modelo if hasattr(p, 'modelo') else '',
                'unidad': p.unidad if hasattr(p, 'unidad') else '',
                'precio_unitario': float(p.precio_unitario) if hasattr(p, 'precio_unitario') and p.precio_unitario else 0
            })
        return jsonify(resultado)
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/productos/buscar', methods=['GET'])
def buscar_productos_cotizacion():
    """Buscar productos por código o descripción para autocomplete"""
    try:
        q = request.args.get('q', '').strip()
        if len(q) < 2:
            return jsonify({'success': True, 'data': []})
        
        from database import buscar_productos
        productos = buscar_productos(q, limit=20)
        
        resultado = []
        for p in productos:
            resultado.append({
                'id': p.get('id'),
                'codigo': p.get('codigo', ''),
                'descripcion': p.get('descripcion', ''),
                'marca': p.get('marca', ''),
                'modelo': p.get('modelo', ''),
                'ultimo_costo': float(p.get('costo_unitario', 0)) if p.get('costo_unitario') else 0,
                'precio_venta': float(p.get('precio_unitario', 0)) if p.get('precio_unitario') else 0
            })
        
        return jsonify({'success': True, 'data': resultado})
    except Exception as e:
        print(f"❌ Error en buscar_productos: {e}")
        return jsonify({'success': False, 'data': [], 'error': str(e)}), 500

@app.route('/api/productos/<int:id>', methods=['GET'])
def get_producto_by_id(id):
    try:
        producto = Producto.query.get(id)
        if not producto:
            return jsonify({'success': False, 'error': 'Producto no encontrado'}), 404
        
        resultado = {
            'id': producto.id,
            'codigo': producto.codigo if hasattr(producto, 'codigo') else '',
            'familia': producto.familia if hasattr(producto, 'familia') else '',
            'descripcion': producto.descripcion if hasattr(producto, 'descripcion') else '',
            'descripcion_larga': producto.descripcion_larga if hasattr(producto, 'descripcion_larga') else '',
            'modelo': producto.modelo if hasattr(producto, 'modelo') else '',
            'marca': producto.marca if hasattr(producto, 'marca') else '',
            'unidad': producto.unidad if hasattr(producto, 'unidad') else '',
            'peso': producto.peso if hasattr(producto, 'peso') else '',
            'volumen': producto.volumen if hasattr(producto, 'volumen') else '',
            'transporte': producto.transporte if hasattr(producto, 'transporte') else '',
            'costo_unitario': float(producto.costo_unitario) if hasattr(producto, 'costo_unitario') and producto.costo_unitario else 0,
            'precio_unitario': float(producto.precio_unitario) if hasattr(producto, 'precio_unitario') and producto.precio_unitario else 0,
            'stock': producto.stock if hasattr(producto, 'stock') else 0,
            'observaciones': producto.observaciones if hasattr(producto, 'observaciones') else ''
        }
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/productos/<int:id>', methods=['PUT'])
def update_producto(id):
    try:
        producto = Producto.query.get(id)
        if not producto:
            return jsonify({'success': False, 'error': 'Producto no encontrado'}), 404
        
        data = request.get_json()
        
        if 'familia' in data:
            producto.familia = data['familia']
        if 'descripcion' in data:
            producto.descripcion = data['descripcion']
        if 'descripcion_larga' in data:
            producto.descripcion_larga = data['descripcion_larga']
        if 'modelo' in data:
            producto.modelo = data['modelo']
        if 'marca' in data:
            producto.marca = data['marca']
        if 'unidad' in data:
            producto.unidad = data['unidad']
        if 'peso' in data:
            producto.peso = data['peso']
        if 'volumen' in data:
            producto.volumen = data['volumen']
        if 'transporte' in data:
            producto.transporte = data['transporte']
        if 'costo_unitario' in data:
            producto.costo_unitario = data['costo_unitario']
        if 'precio_unitario' in data:
            producto.precio_unitario = data['precio_unitario']
        if 'stock' in data:
            producto.stock = data['stock']
        if 'observaciones' in data:
            producto.observaciones = data['observaciones']
        
        if hasattr(producto, 'updated_at'):
            producto.updated_at = datetime.now()
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Producto actualizado correctamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/productos/<int:id>', methods=['DELETE'])
def delete_producto(id):
    try:
        producto = Producto.query.get(id)
        if not producto:
            return jsonify({'success': False, 'error': 'Producto no encontrado'}), 404
        
        db.session.delete(producto)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Producto eliminado correctamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== RUTAS PARA CLIENTES ====================

@app.route('/api/clientes/buscar', methods=['GET'])
def api_buscar_clientes():
    try:
        busqueda = request.args.get('q', '').strip()
        
        if len(busqueda) < 2:
            return jsonify({'success': True, 'data': []})
        
        from database import buscar_clientes
        clientes = buscar_clientes(busqueda, limit=20)
        
        resultado = []
        for c in clientes:
            resultado.append({
                'id': c.get('id'),
                'tipo_documento': c.get('tipo_documento'),
                'numero_documento': c.get('numero_documento'),
                'razon_social': c.get('razon_social'),
                'nombre_comercial': c.get('nombre_comercial'),
                'direccion_fiscal': c.get('direccion_fiscal'),
                'codigo_cliente': c.get('codigo_cliente'),
                'telefono_contacto': c.get('telefono_contacto', '')
            })
        
        return jsonify({'success': True, 'data': resultado})
    except Exception as e:
        print(f"❌ Error en api_buscar_clientes: {e}")
        return jsonify({'success': False, 'data': [], 'error': str(e)}), 500

@app.route('/api/clientes/crear', methods=['POST'])
def api_crear_cliente():
    """Crear un nuevo cliente desde la cotización"""
    try:
        data = request.get_json()
        
        from database import insertar_cliente_completo
        
        cliente_data = {
            'tipo_documento': data.get('tipo_documento'),
            'numero_documento': data.get('numero_documento'),
            'razon_social': data.get('razon_social'),
            'nombre_comercial': data.get('nombre_comercial'),
            'direccion_fiscal': data.get('direccion_fiscal'),
            'telefono_contacto': data.get('telefono_contacto'),
            'email_contacto': data.get('email_contacto'),
            'contactos': [],
            'puntos_entrega': []
        }
        
        if data.get('nombre_contacto'):
            cliente_data['contactos'].append({
                'nombre_contacto': data.get('nombre_contacto'),
                'email': data.get('email_contacto'),
                'telefono': data.get('telefono_contacto'),
                'principal': True
            })
        
        resultado = insertar_cliente_completo(cliente_data)
        
        if resultado and resultado.get('success'):
            return jsonify({
                'success': True,
                'data': {
                    'id': resultado.get('id'),
                    'codigo_cliente': resultado.get('codigo_cliente')
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': resultado.get('error', 'Error al guardar cliente')
            }), 400
            
    except Exception as e:
        print(f"❌ Error en api_crear_cliente: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/clientes/<int:id>', methods=['GET'])
def api_obtener_cliente(id):
    try:
        from database import obtener_cliente_completo_por_id
        cliente = obtener_cliente_completo_por_id(id)
        
        if not cliente:
            return jsonify({'success': False, 'error': 'Cliente no encontrado'}), 404
        
        return jsonify({'success': True, 'data': cliente})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== RUTAS PARA USUARIO ====================

@app.route('/api/usuarios/actual', methods=['GET'])
def usuario_actual():
    """Obtener el usuario actual"""
    try:
        return jsonify({
            'success': True,
            'data': {
                'id': 1,
                'nombre_completo': 'Hellen Blas Principe',
                'email': 'ventas@kcfcorporacion.com',
                'telefono': '999932051',
                'codigo_vendedor': 'HELLEN',
                'rol': 'VENDEDOR'
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== RUTAS PARA MOVIMIENTOS STOCK ====================

@app.route('/api/movimientos_stock', methods=['GET'])
def get_movimientos():
    try:
        producto_id = request.args.get('producto_id', type=int)
        
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
                'motivo': m.motivo,
                'referencia': m.referencia,
                'costo_unitario': float(m.costo_unitario) if m.costo_unitario else None,
                'created_at': m.created_at.isoformat() if m.created_at else None
            })
        return jsonify(resultado)
    except Exception as e:
        return jsonify([]), 200

@app.route('/api/movimientos_stock', methods=['POST'])
def crear_movimiento():
    try:
        data = request.get_json()
        
        if not data.get('producto_id') or not data.get('tipo') or not data.get('cantidad'):
            return jsonify({'success': False, 'error': 'Faltan datos'}), 400
        
        producto = Producto.query.get(data['producto_id'])
        if not producto:
            return jsonify({'success': False, 'error': 'Producto no encontrado'}), 404
        
        cantidad = int(data['cantidad'])
        
        nuevo = MovimientoStock(
            producto_id=data['producto_id'],
            tipo=data['tipo'],
            cantidad=cantidad,
            motivo=data.get('motivo'),
            referencia=data.get('referencia'),
            costo_unitario=data.get('costo_unitario')
        )
        db.session.add(nuevo)
        
        if data['tipo'] == 'ENTRADA':
            producto.stock = (producto.stock or 0) + cantidad
        elif data['tipo'] == 'SALIDA':
            producto.stock = (producto.stock or 0) - cantidad
        elif data['tipo'] == 'AJUSTE':
            producto.stock = cantidad
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Movimiento registrado', 'nuevo_stock': producto.stock}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ultimo_codigo', methods=['GET'])
def ultimo_codigo():
    try:
        prefijo = request.args.get('prefijo', 'GEN')
        from sqlalchemy import text
        
        with db.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT codigo FROM productos 
                WHERE codigo LIKE :prefijo 
                ORDER BY id DESC LIMIT 1
            """), {"prefijo": f'{prefijo}-%'})
            
            row = result.fetchone()
            
            if row and row[0]:
                try:
                    numero = int(row[0].split('-')[1])
                    return jsonify({'success': True, 'ultimo_numero': numero})
                except:
                    return jsonify({'success': True, 'ultimo_numero': 0})
            else:
                return jsonify({'success': True, 'ultimo_numero': 0})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== BLUEPRINTS ====================
from routes.usuarios import usuarios_bp
from routes.cotizaciones import cotizaciones_bp
from routes.mantenedor_productos import productos_bp
from routes.mantenedor_clientes import mantenedor_clientes_bp

app.register_blueprint(usuarios_bp)
app.register_blueprint(cotizaciones_bp)
app.register_blueprint(productos_bp)
app.register_blueprint(mantenedor_clientes_bp)

print("🔵 Blueprints registrados:", list(app.blueprints.keys()))
print("🚀 Servidor Flask iniciado")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("✅ Base de datos inicializada")
    app.run(debug=True, host='0.0.0.0', port=5000)