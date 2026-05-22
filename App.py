from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
import base64
import traceback

app = Flask(__name__)

# ==================== CONFIGURACIÓN SUPABASE ====================
_a = base64.b64decode('cG9zdGdyZXNxbDovLy9wb3N0Z3Jlcy50a2Ztd3ZzZW52Z3B5ZXh2ZGNhdDphZG1pbjM1NjE5NjdrY2ZAYXdzLTEtdXMtZWFzdC0xLnBvb2xlci5zdXBhYmFzZS5jb206NjU0My9wb3N0Z3Jlcw==').decode('utf-8')
app.config['SQLALCHEMY_DATABASE_URI'] = _a
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'sb_secret_k56lhPYVINqZMj_BZexRbw_JzeBx8Hx'

db = SQLAlchemy()
db.init_app(app)

# ==================== MODELOS (SIN IMPORTAR DE OTROS LADOS) ====================
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
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

# ==================== RUTAS API PARA KÁRDEX ====================

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
        traceback.print_exc()
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
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/movimientos_stock', methods=['POST'])
def crear_movimiento():
    print("📝 POST a /api/movimientos_stock")
    try:
        data = request.get_json()
        print(f"Datos recibidos: {data}")
        
        # Validaciones
        if not data.get('producto_id'):
            return jsonify({'success': False, 'error': 'Producto ID requerido'}), 400
        
        if not data.get('tipo'):
            return jsonify({'success': False, 'error': 'Tipo de movimiento requerido'}), 400
        
        if not data.get('cantidad') or int(data.get('cantidad')) <= 0:
            return jsonify({'success': False, 'error': 'Cantidad válida requerida'}), 400
        
        producto = Producto.query.get(data['producto_id'])
        if not producto:
            return jsonify({'success': False, 'error': 'Producto no encontrado'}), 404
        
        cantidad = int(data['cantidad'])
        
        # Validar stock para salidas
        if data['tipo'] == 'SALIDA' and (producto.stock or 0) < cantidad:
            return jsonify({'success': False, 'error': f'Stock insuficiente. Stock actual: {producto.stock or 0}'}), 400
        
        # Crear movimiento
        nuevo = MovimientoStock(
            producto_id=data['producto_id'],
            tipo=data['tipo'],
            cantidad=cantidad,
            motivo=data.get('motivo', ''),
            referencia=data.get('referencia', ''),
            costo_unitario=data.get('costo_unitario') if data.get('costo_unitario') else None
        )
        db.session.add(nuevo)
        
        # Actualizar stock
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
        traceback.print_exc()
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
        print(f"❌ Error: {e}")
        return jsonify({'error': str(e)}), 500

# ==================== RUTAS DE PÁGINAS ====================
@app.route('/mantenedor/productos')
def gestion_productos():
    try:
        productos = Producto.query.all()
        return render_template('gestion_productos.html', productos=productos)
    except Exception as e:
        print(f"❌ Error: {e}")
        return f"Error: {e}"

@app.route('/test')
def test():
    return jsonify({'status': 'ok', 'message': 'Servidor funcionando'})

# ==================== INICIALIZACIÓN ====================
if __name__ == "__main__":
    with app.app_context():
        try:
            db.create_all()
            print("✅ Base de datos inicializada correctamente")
            
            # Verificar si hay productos
            count = Producto.query.count()
            print(f"📦 Productos en base de datos: {count}")
            
        except Exception as e:
            print(f"❌ Error al inicializar base de datos: {e}")
            traceback.print_exc()
    
    print("🚀 Servidor iniciando en http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)