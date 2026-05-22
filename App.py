from flask import Flask, jsonify, request, render_template, session, redirect, url_for
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

# ==================== MODELOS ====================
class Producto(db.Model):
    __tablename__ = 'productos'
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True)
    familia = db.Column(db.String(100))
    marca = db.Column(db.String(100))
    descripcion = db.Column(db.Text)
    modelo = db.Column(db.String(100))
    unidad = db.Column(db.String(20), default='Unidad')
    costo_unitario = db.Column(db.Numeric(10,2), default=0)
    precio_unitario = db.Column(db.Numeric(10,2), default=0)
    stock = db.Column(db.Integer, default=0)
    activo = db.Column(db.Boolean, default=True)

class MovimientoStock(db.Model):
    __tablename__ = 'movimientos_stock'
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'))
    tipo = db.Column(db.String(20))  # ENTRADA, SALIDA, AJUSTE
    cantidad = db.Column(db.Integer)
    motivo = db.Column(db.String(200))
    referencia = db.Column(db.String(100))
    costo_unitario = db.Column(db.Numeric(10,2))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

# ==================== RUTAS DIRECTAS KÁRDEX ====================
@app.route('/api/productos', methods=['GET'])
def get_productos():
    print("📦 [API] /api/productos fue llamado")
    try:
        productos = Producto.query.filter_by(activo=True).order_by(Producto.descripcion).all()
        resultado = []
        for p in productos:
            resultado.append({
                'id': p.id,
                'codigo': p.codigo or f'P-{p.id}',
                'descripcion': p.descripcion,
                'stock': p.stock or 0,
                'costo_unitario': float(p.costo_unitario) if p.costo_unitario else 0
            })
        print(f"✅ Retornando {len(resultado)} productos")
        return jsonify(resultado)
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/movimientos_stock', methods=['GET'])
def get_movimientos():
    print("📊 [API] /api/movimientos_stock fue llamado")
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
                'motivo': m.motivo or '',
                'referencia': m.referencia or '',
                'costo_unitario': float(m.costo_unitario) if m.costo_unitario else None,
                'created_at': m.created_at.isoformat() if m.created_at else None
            })
        return jsonify(resultado)
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/movimientos_stock', methods=['POST'])
def crear_movimiento():
    print("📝 [API] POST /api/movimientos_stock fue llamado")
    try:
        data = request.get_json()
        print(f"Datos: {data}")
        
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
            motivo=data.get('motivo', ''),
            referencia=data.get('referencia', ''),
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
        print(f"✅ Movimiento creado. Nuevo stock: {producto.stock}")
        return jsonify({'success': True, 'message': 'Movimiento registrado'}), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/productos/<int:id>', methods=['GET'])
def obtener_producto(id):
    try:
        producto = Producto.query.get(id)
        if not producto:
            return jsonify({'error': 'Producto no encontrado'}), 404
        return jsonify({
            'id': producto.id,
            'codigo': producto.codigo,
            'descripcion': producto.descripcion,
            'stock': producto.stock,
            'costo_unitario': float(producto.costo_unitario) if producto.costo_unitario else 0
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== RUTAS DE PÁGINAS ====================
@app.route('/mantenedor/productos')
def gestion_productos():
    productos = Producto.query.filter_by(activo=True).all()
    return render_template('gestion_productos.html', productos=productos)

@app.route('/test')
def test():
    return jsonify({'status': 'ok', 'message': 'Servidor funcionando'})

# ==================== INICIALIZACIÓN ====================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("✅ Base de datos inicializada")
    app.run(debug=True, host='0.0.0.0', port=5000)