# routes/kardex.py
from flask import Blueprint, jsonify, request
from models import db
from models.producto import Producto
from models.movimiento_stock import MovimientoStock  # Asumiendo que creaste el modelo

kardex_bp = Blueprint('kardex', __name__)

# ====================== API ======================

@kardex_bp.route('/api/productos', methods=['GET'])
def get_productos():
    """Devuelve todos los productos (para selects)"""
    productos = Producto.query.all()
    return jsonify([{
        'id': p.id,
        'codigo': p.codigo,
        'descripcion': p.descripcion,
        'costo_unitario': p.costo_unitario
    } for p in productos])


@kardex_bp.route('/api/movimientos_stock', methods=['GET'])
def get_movimientos():
    """Obtener movimientos del Kárdex"""
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
        'costo_unitario': m.costo_unitario,
        'created_at': m.created_at.isoformat()
    } for m in movimientos])


@kardex_bp.route('/api/movimientos_stock', methods=['POST'])
def crear_movimiento():
    """Registrar nuevo movimiento"""
    data = request.get_json()

    nuevo_mov = MovimientoStock(
        producto_id=data['producto_id'],
        tipo=data['tipo'],
        cantidad=data['cantidad'],
        motivo=data.get('motivo'),
        referencia=data.get('referencia'),
        costo_unitario=data.get('costo_unitario')
    )

    db.session.add(nuevo_mov)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Movimiento registrado correctamente'}), 201