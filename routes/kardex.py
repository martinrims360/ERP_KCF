# routes/kardex.py
from flask import Blueprint, jsonify, request
from models import db
from models.producto import Producto
from models.movimiento_stock import MovimientoStock
from datetime import datetime  # ✅ 1. AGREGAR ESTA LÍNEA

kardex_bp = Blueprint('kardex', __name__)

# ====================== OBTENER PRODUCTOS ======================
@kardex_bp.route('/api/productos', methods=['GET'])
def get_productos():
    productos = Producto.query.order_by(Producto.descripcion).all()
    return jsonify([{
        'id': p.id,
        'codigo': getattr(p, 'codigo', ''),
        'descripcion': p.descripcion,
        'stock': p.stock,  # ✅ 2. AGREGAR STOCK
        'costo_unitario': float(p.costo_unitario) if p.costo_unitario else 0  # ✅ 3. AGREGAR COSTO
    } for p in productos])


# ====================== OBTENER PRODUCTO POR ID ======================
@kardex_bp.route('/api/productos/<int:id>', methods=['GET'])  # ✅ 4. NUEVO ENDPOINT
def get_producto(id):
    producto = Producto.query.get_or_404(id)
    return jsonify({
        'id': producto.id,
        'codigo': getattr(producto, 'codigo', ''),
        'descripcion': producto.descripcion,
        'stock': producto.stock,
        'costo_unitario': float(producto.costo_unitario) if producto.costo_unitario else 0
    })


# ====================== OBTENER MOVIMIENTOS ======================
@kardex_bp.route('/api/movimientos_stock', methods=['GET'])
def get_movimientos():
    producto_id = request.args.get('producto_id', type=int)
    fecha_desde = request.args.get('fecha_desde')  # ✅ 5. FILTRO POR FECHA
    fecha_hasta = request.args.get('fecha_hasta')

    # ✅ 6. CAMBIAR A orden ASCENDENTE para calcular saldo correctamente
    query = MovimientoStock.query.order_by(MovimientoStock.created_at.asc())

    if producto_id:
        query = query.filter_by(producto_id=producto_id)
    
    if fecha_desde:
        query = query.filter(MovimientoStock.created_at >= fecha_desde)
    
    if fecha_hasta:
        query = query.filter(MovimientoStock.created_at <= fecha_hasta + ' 23:59:59')

    movimientos = query.all()

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


# ====================== REGISTRAR MOVIMIENTO ======================
@kardex_bp.route('/api/movimientos_stock', methods=['POST'])
def crear_movimiento():
    data = request.get_json()
    
    # ✅ 7. VALIDAR DATOS
    if not data.get('producto_id') or not data.get('tipo') or not data.get('cantidad'):
        return jsonify({'success': False, 'error': 'Faltan datos requeridos'}), 400
    
    # ✅ 8. OBTENER PRODUCTO PARA VALIDAR STOCK
    producto = Producto.query.get(data['producto_id'])
    if not producto:
        return jsonify({'success': False, 'error': 'Producto no encontrado'}), 404
    
    cantidad = int(data['cantidad'])
    
    # ✅ 9. VALIDAR STOCK SUFICIENTE PARA SALIDAS
    if data['tipo'] == 'SALIDA' and producto.stock < cantidad:
        return jsonify({'success': False, 'error': f'Stock insuficiente. Stock actual: {producto.stock}'}), 400

    # ✅ 10. CREAR MOVIMIENTO
    nuevo = MovimientoStock(
        producto_id=data['producto_id'],
        tipo=data['tipo'],
        cantidad=cantidad,
        motivo=data.get('motivo'),
        referencia=data.get('referencia'),
        costo_unitario=data.get('costo_unitario')
    )
    
    # ✅ 11. FECHA PERSONALIZADA SI SE ENVÍA
    if data.get('fecha'):
        nuevo.created_at = datetime.fromisoformat(data['fecha'])
    
    db.session.add(nuevo)
    
    # ✅ 12. ACTUALIZAR STOCK DEL PRODUCTO
    if data['tipo'] == 'ENTRADA':
        producto.stock += cantidad
    elif data['tipo'] == 'SALIDA':
        producto.stock -= cantidad
    elif data['tipo'] == 'AJUSTE':
        producto.stock = cantidad
    
    try:
        db.session.commit()
        return jsonify({'success': True, 'message': 'Movimiento registrado correctamente'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500