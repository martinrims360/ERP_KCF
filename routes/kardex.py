# routes/kardex.py
print("🟢 [1] Iniciando carga de kardex.py...")

from flask import Blueprint, jsonify, request
print("🟢 [2] Flask importado")

from models import db
print("🟢 [3] db importado")

from models.producto import Producto
print("🟢 [4] Producto importado")

from models.movimiento_stock import MovimientoStock
print("🟢 [5] MovimientoStock importado")

from datetime import datetime
print("🟢 [6] datetime importado")

print("🟢 [7] Creando blueprint kardex_bp...")
kardex_bp = Blueprint('kardex', __name__)
print("🟢 [8] Blueprint kardex_bp creado exitosamente")

# ====================== OBTENER PRODUCTOS ======================
@kardex_bp.route('/api/productos', methods=['GET'])
def get_productos():
    print("📦 [API] Endpoint /api/productos fue llamado")
    try:
        productos = Producto.query.order_by(Producto.descripcion).all()
        print(f"📦 [API] Se encontraron {len(productos)} productos")
        return jsonify([{
            'id': p.id,
            'codigo': getattr(p, 'codigo', ''),
            'descripcion': p.descripcion,
            'stock': p.stock,
            'costo_unitario': float(p.costo_unitario) if p.costo_unitario else 0
        } for p in productos])
    except Exception as e:
        print(f"❌ [API] Error en get_productos: {e}")
        return jsonify({'error': str(e)}), 500


# ====================== OBTENER PRODUCTO POR ID ======================
@kardex_bp.route('/api/productos/<int:id>', methods=['GET'])
def get_producto(id):
    print(f"📦 [API] Endpoint /api/productos/{id} fue llamado")
    try:
        producto = Producto.query.get_or_404(id)
        return jsonify({
            'id': producto.id,
            'codigo': getattr(producto, 'codigo', ''),
            'descripcion': producto.descripcion,
            'stock': producto.stock,
            'costo_unitario': float(producto.costo_unitario) if producto.costo_unitario else 0
        })
    except Exception as e:
        print(f"❌ [API] Error en get_producto: {e}")
        return jsonify({'error': str(e)}), 500


# ====================== OBTENER MOVIMIENTOS ======================
@kardex_bp.route('/api/movimientos_stock', methods=['GET'])
def get_movimientos():
    print("📊 [API] Endpoint /api/movimientos_stock fue llamado")
    try:
        producto_id = request.args.get('producto_id', type=int)
        fecha_desde = request.args.get('fecha_desde')
        fecha_hasta = request.args.get('fecha_hasta')
        
        print(f"📊 [API] Parámetros - producto_id: {producto_id}, desde: {fecha_desde}, hasta: {fecha_hasta}")

        query = MovimientoStock.query.order_by(MovimientoStock.created_at.asc())

        if producto_id:
            query = query.filter_by(producto_id=producto_id)
        
        if fecha_desde:
            query = query.filter(MovimientoStock.created_at >= fecha_desde)
        
        if fecha_hasta:
            query = query.filter(MovimientoStock.created_at <= fecha_hasta + ' 23:59:59')

        movimientos = query.all()
        print(f"📊 [API] Se encontraron {len(movimientos)} movimientos")

        return jsonify([{
            'id': m.id,
            'producto_id': m.producto_id,
            'tipo': m.tipo,
            'cantidad': m.cantidad,
            'motivo': m.motivo,
            'referencia': m.referencia,
            'costo_unitario': float(m.costo_unitario) if m.costo_unitario else None,
            'created_at': m.created_at.isoformat()
        } for m in movimientos])
    except Exception as e:
        print(f"❌ [API] Error en get_movimientos: {e}")
        return jsonify({'error': str(e)}), 500


# ====================== REGISTRAR MOVIMIENTO ======================
@kardex_bp.route('/api/movimientos_stock', methods=['POST'])
def crear_movimiento():
    print("📝 [API] Endpoint POST /api/movimientos_stock fue llamado")
    try:
        data = request.get_json()
        print(f"📝 [API] Datos recibidos: {data}")
        
        if not data.get('producto_id') or not data.get('tipo') or not data.get('cantidad'):
            return jsonify({'success': False, 'error': 'Faltan datos requeridos'}), 400
        
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
        
        if data.get('fecha'):
            nuevo.created_at = datetime.fromisoformat(data['fecha'])
        
        db.session.add(nuevo)
        
        if data['tipo'] == 'ENTRADA':
            producto.stock += cantidad
        elif data['tipo'] == 'SALIDA':
            producto.stock -= cantidad
        elif data['tipo'] == 'AJUSTE':
            producto.stock = cantidad
        
        db.session.commit()
        print("✅ [API] Movimiento registrado y stock actualizado")
        return jsonify({'success': True, 'message': 'Movimiento registrado correctamente'}), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ [API] Error en crear_movimiento: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

print("🟢 [9] ¡kardex.py se ha cargado COMPLETAMENTE sin errores!")