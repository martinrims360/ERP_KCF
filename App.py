from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import base64

app = Flask(__name__)

# ==================== CONFIGURACIÓN SUPABASE ====================
_a = base64.b64decode('cG9zdGdyZXNxbDovLy9wb3N0Z3Jlcy50a2Ztd3ZzZW52Z3B5ZXh2ZGNhdDphZG1pbjM1NjE5NjdrY2ZAYXdzLTEtdXMtZWFzdC0xLnBvb2xlci5zdXBhYmFzZS5jb206NjU0My9wb3N0Z3Jlcw==').decode('utf-8')
app.config['SQLALCHEMY_DATABASE_URI'] = _a
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'sb_secret_k56lhPYVINqZMj_BZexRbw_JzeBx8Hx'

db = SQLAlchemy()
db.init_app(app)

# ==================== IMPORTAR MODELOS ====================
from models.producto import Producto
from models.movimiento_stock import MovimientoStock
from datetime import datetime

# ==================== RUTAS DIRECTAS PARA KÁRDEX (SIN BLUEPRINT) ====================

# Ruta para obtener todos los productos
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
                'costo_unitario': float(p.costo_unitario) if hasattr(p, 'costo_unitario') and p.costo_unitario else 0
            })
        print(f"✅ Se encontraron {len(resultado)} productos")
        return jsonify(resultado)
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'error': str(e)}), 500

# Ruta para obtener movimientos de stock
@app.route('/api/movimientos_stock', methods=['GET'])
def get_movimientos():
    print("📊 Llamada a /api/movimientos_stock")
    try:
        producto_id = request.args.get('producto_id', type=int)
        
        if producto_id:
            movimientos = MovimientoStock.query.filter_by(producto_id=producto_id).order_by(MovimientoStock.created_at.desc()).all()
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
        print(f"✅ Se encontraron {len(resultado)} movimientos")
        return jsonify(resultado)
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'error': str(e)}), 500

# Ruta para crear movimientos
@app.route('/api/movimientos_stock', methods=['POST'])
def crear_movimiento():
    print("📝 Llamada a POST /api/movimientos_stock")
    try:
        data = request.get_json()
        print(f"Datos recibidos: {data}")
        
        if not data.get('producto_id') or not data.get('tipo') or not data.get('cantidad'):
            return jsonify({'success': False, 'error': 'Faltan datos'}), 400
        
        producto = Producto.query.get(data['producto_id'])
        if not producto:
            return jsonify({'success': False, 'error': 'Producto no encontrado'}), 404
        
        cantidad = int(data['cantidad'])
        
        if data['tipo'] == 'SALIDA' and producto.stock < cantidad:
            return jsonify({'success': False, 'error': f'Stock insuficiente. Stock actual: {producto.stock}'}), 400
        
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
            producto.stock += cantidad
        elif data['tipo'] == 'SALIDA':
            producto.stock -= cantidad
        elif data['tipo'] == 'AJUSTE':
            producto.stock = cantidad
        
        db.session.commit()
        print("✅ Movimiento creado exitosamente")
        return jsonify({'success': True, 'message': 'Movimiento registrado'}), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Ruta de prueba
@app.route('/')
def home():
    return jsonify({'message': 'Servidor funcionando', 'status': 'ok'})

# ==================== BLUEPRINTS ORIGINALES ====================
from routes.usuarios import usuarios_bp
from routes.cotizaciones import cotizaciones_bp
from routes.mantenedor_productos import productos_bp

app.register_blueprint(usuarios_bp)
app.register_blueprint(cotizaciones_bp)
app.register_blueprint(productos_bp)

print("🔵 Blueprints registrados:", list(app.blueprints.keys()))
print("🚀 Servidor Flask iniciado")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("✅ Base de datos inicializada")
    app.run(debug=True, host='0.0.0.0', port=5000)