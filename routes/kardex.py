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
# 🔥 AGREGAR url_prefix='' para asegurar que las rutas sean correctas
kardex_bp = Blueprint('kardex', __name__, url_prefix='')
print("🟢 [8] Blueprint kardex_bp creado exitosamente")

# ====================== OBTENER PRODUCTOS ======================
@kardex_bp.route('/api/productos', methods=['GET'])
def get_productos():
    print("📦 [API] Endpoint /api/productos fue llamado")
    try:
        productos = Producto.query.order_by(Producto.descripcion).all()
        print(f"📦 [API] Se encontraron {len(productos)} productos")
        
        # 🔥 MEJORA: Verificar que los productos tengan los atributos necesarios
        resultado = []
        for p in productos:
            resultado.append({
                'id': p.id,
                'codigo': getattr(p, 'codigo', f'PROD-{p.id}'),  # Si no tiene código, genera uno
                'descripcion': p.descripcion,
                'stock': getattr(p, 'stock', 0),
                'costo_unitario': float(p.costo_unitario) if hasattr(p, 'costo_unitario') and p.costo_unitario else 0
            })
        
        print(f"📦 [API] Retornando {len(resultado)} productos")
        return jsonify(resultado)
    except Exception as e:
        print(f"❌ [API] Error en get_productos: {e}")
        import traceback
        traceback.print_exc()
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
            'stock': getattr(producto, 'stock', 0),
            'costo_unitario': float(producto.costo_unitario) if hasattr(producto, 'costo_unitario') and producto.costo_unitario else 0
        })
    except Exception as e:
        print(f"❌ [API] Error en get_producto: {e}")
        import traceback
        traceback.print_exc()
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
                'created_at': m.created_at.isoformat() if m.created_at else datetime.now().isoformat()
            })
        
        return jsonify(resultado)
    except Exception as e:
        print(f"❌ [API] Error en get_movimientos: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# ====================== REGISTRAR MOVIMIENTO ======================
@kardex_bp.route('/api/movimientos_stock', methods=['POST'])
def crear_movimiento():
    print("📝 [API] Endpoint POST /api/movimientos_stock fue llamado")
    try:
        data = request.get_json()
        print(f"📝 [API] Datos recibidos: {data}")
        
        # 🔥 MEJORA: Validaciones más claras
        if not data.get('producto_id'):
            return jsonify({'success': False, 'error': 'Producto no especificado'}), 400
        
        if not data.get('tipo'):
            return jsonify({'success': False, 'error': 'Tipo de movimiento no especificado'}), 400
        
        if not data.get('cantidad') or int(data.get('cantidad', 0)) <= 0:
            return jsonify({'success': False, 'error': 'Cantidad inválida'}), 400
        
        producto = Producto.query.get(data['producto_id'])
        if not producto:
            return jsonify({'success': False, 'error': 'Producto no encontrado'}), 404
        
        cantidad = int(data['cantidad'])
        stock_actual = getattr(producto, 'stock', 0)
        
        # Validar stock para salidas
        if data['tipo'] == 'SALIDA' and stock_actual < cantidad:
            return jsonify({'success': False, 'error': f'Stock insuficiente. Stock actual: {stock_actual}'}), 400

        nuevo = MovimientoStock(
            producto_id=data['producto_id'],
            tipo=data['tipo'],
            cantidad=cantidad,
            motivo=data.get('motivo', ''),
            referencia=data.get('referencia', ''),
            costo_unitario=data.get('costo_unitario') if data.get('costo_unitario') else None
        )
        
        if data.get('fecha'):
            try:
                nuevo.created_at = datetime.strptime(data['fecha'], '%Y-%m-%d')
            except:
                print(f"⚠️ No se pudo parsear la fecha: {data.get('fecha')}")
        
        db.session.add(nuevo)
        
        # Actualizar stock según tipo
        if data['tipo'] == 'ENTRADA':
            producto.stock = stock_actual + cantidad
        elif data['tipo'] == 'SALIDA':
            producto.stock = stock_actual - cantidad
        elif data['tipo'] == 'AJUSTE':
            producto.stock = cantidad
        
        db.session.commit()
        print(f"✅ [API] Movimiento registrado. Nuevo stock: {producto.stock}")
        return jsonify({
            'success': True, 
            'message': 'Movimiento registrado correctamente',
            'nuevo_stock': producto.stock
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ [API] Error en crear_movimiento: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


# ====================== RUTA DE PRUEBA ======================
@kardex_bp.route('/test', methods=['GET'])
def test_kardex():
    return jsonify({'message': 'Kardex funciona correctamente', 'status': 'ok'})

print("🟢 [9] ¡kardex.py se ha cargado COMPLETAMENTE sin errores!")