# routes/kardex.py
from flask import Blueprint, jsonify, request
from models import db
from models.producto import Producto
from models.movimiento_stock import MovimientoStock

kardex_bp = Blueprint('kardex', __name__)

# ====================== OBTENER PRODUCTOS ======================
@kardex_bp.route('/api/productos', methods=['GET'])
def get_productos():
    productos = Producto.query.order_by(Producto.descripcion).all()
    return jsonify([{
        'id': p.id,
        'codigo': getattr(p, 'codigo', ''),
        'descripcion': p.descripcion
    } for p in productos])


# ====================== OBTENER MOVIMIENTOS ======================
@kardex_bp.route('/api/movimientos_stock', methods=['GET'])
def get_movimientos():
    producto_id = request.args.get('producto_id', type=int)

    query = MovimientoStock.query.order_by(MovimientoStock.created_at.desc())

    if producto_id:
        query = query.filter_by(producto_id=producto_id)

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

    nuevo = MovimientoStock(
        producto_id=data['producto_id'],
        tipo=data['tipo'],
        cantidad=int(data['cantidad']),
        motivo=data.get('motivo'),
        referencia=data.get('referencia'),
        costo_unitario=data.get('costo_unitario')
    )

    db.session.add(nuevo)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Movimiento registrado correctamente'}), 201