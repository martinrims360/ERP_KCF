# routes/kardex.py
print("=" * 50)
print("🟢 INICIANDO CARGA DE KARDEX.PY")
print("=" * 50)

from flask import Blueprint, jsonify, request
print("🟢 Flask importado")

from models import db
print("🟢 db importado")

from models.producto import Producto
print("🟢 Producto importado")

from models.movimiento_stock import MovimientoStock
print("🟢 MovimientoStock importado")

from datetime import datetime
print("🟢 datetime importado")

# Crear blueprint
print("🟢 Creando blueprint...")
kardex_bp = Blueprint('kardex', __name__, url_prefix='')
print("🟢 Blueprint creado exitosamente")

# ====================== RUTA DE PRUEBA ======================
@kardex_bp.route('/test', methods=['GET'])
def test_kardex():
    print("🧪 Ruta /test llamada")
    return jsonify({'message': 'Kardex funciona correctamente', 'status': 'ok'})

# ====================== OBTENER PRODUCTOS ======================
@kardex_bp.route('/api/productos', methods=['GET'])
def get_productos():
    print("📦 [API] /api/productos fue llamado")
    try:
        productos = Producto.query.all()
        print(f"📦 [API] Se encontraron {len(productos)} productos")
        
        resultado = []
        for p in productos:
            resultado.append({
                'id': p.id,
                'codigo': getattr(p, 'codigo', f'P-{p.id}'),
                'descripcion': p.descripcion,
                'stock': getattr(p, 'stock', 0),
                'costo_unitario': float(p.costo_unitario) if hasattr(p, 'costo_unitario') and p.costo_unitario else 0
            })
        
        print(f"📦 [API] Retornando {len(resultado)} productos")
        return jsonify(resultado)
    except Exception as e:
        print(f"❌ Error en get_productos: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# ====================== OBTENER MOVIMIENTOS ======================
@kardex_bp.route('/api/movimientos_stock', methods=['GET'])
def get_movimientos():
    print("📊 [API] /api/movimientos_stock fue llamado")
    try:
        producto_id = request.args.get('producto_id', type=int)
        print(f"📊 producto_id: {producto_id}")
        
        if producto_id:
            movimientos = MovimientoStock.query.filter_by(producto_id=producto_id).order_by(MovimientoStock.created_at.asc()).all()
        else:
            movimientos = []
        
        print(f"📊 Se encontraron {len(movimientos)} movimientos")
        
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
        print(f"❌ Error en get_movimientos: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# ====================== REGISTRAR MOVIMIENTO ======================
@kardex_bp.route('/api/movimientos_stock', methods=['POST'])
def crear_movimiento():
    print("📝 [API] POST /api/movimientos_stock fue llamado")
    try:
        data = request.get_json()
        print(f"📝 Datos recibidos: {data}")
        
        if not data.get('producto_id'):
            return jsonify({'success': False, 'error': 'Producto no especificado'}), 400
        
        if not data.get('tipo'):
            return jsonify({'success': False, 'error': 'Tipo no especificado'}), 400
        
        if not data.get('cantidad') or int(data.get('cantidad', 0)) <= 0:
            return jsonify({'success': False, 'error': 'Cantidad inválida'}), 400
        
        producto = Producto.query.get(data['producto_id'])
        if not producto:
            return jsonify({'success': False, 'error': 'Producto no encontrado'}), 404
        
        cantidad = int(data['cantidad'])
        stock_actual = getattr(producto, 'stock', 0)
        
        if data['tipo'] == 'SALIDA' and stock_actual < cantidad:
            return jsonify({'success': False, 'error': f'Stock insuficiente. Actual: {stock_actual}'}), 400
        
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
            producto.stock = stock_actual + cantidad
        elif data['tipo'] == 'SALIDA':
            producto.stock = stock_actual - cantidad
        elif data['tipo'] == 'AJUSTE':
            producto.stock = cantidad
        
        db.session.commit()
        print(f"✅ Movimiento registrado. Nuevo stock: {producto.stock}")
        
        return jsonify({'success': True, 'message': 'Movimiento registrado'}), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error en crear_movimiento: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

print("=" * 50)
print("🟢 ¡KARDEX.PY CARGADO COMPLETAMENTE!")
print("=" * 50)