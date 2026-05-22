from flask import Flask, jsonify, request
from database import db_query, db_execute, obtener_productos, obtener_producto_por_id
import base64
import os
from datetime import datetime

app = Flask(__name__)

# ==================== CONFIGURACIÓN SUPABASE ====================
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'sb_secret_k56lhPYVINqZMj_BZexRbw_JzeBx8Hx')

# ==================== FUNCIONES DE BASE DE DATOS ====================

def obtener_movimientos_stock(producto_id):
    """Obtener movimientos de stock para un producto"""
    try:
        query = """
            SELECT id, producto_id, tipo, cantidad, motivo, referencia, 
                   costo_unitario, created_at
            FROM movimientos_stock 
            WHERE producto_id = %s
            ORDER BY created_at ASC
        """
        return db_query(query, (producto_id,))
    except Exception as e:
        print(f"Error en obtener_movimientos_stock: {e}")
        return []

def crear_movimiento_stock(data):
    """Crear un nuevo movimiento de stock y actualizar stock del producto"""
    try:
        producto_id = data['producto_id']
        tipo = data['tipo']
        cantidad = data['cantidad']
        motivo = data.get('motivo')
        referencia = data.get('referencia')
        costo_unitario = data.get('costo_unitario')
        
        # Verificar stock actual para SALIDA
        if tipo == 'SALIDA':
            producto = obtener_producto_por_id(producto_id)
            stock_actual = producto.get('stock', 0) if producto else 0
            if stock_actual < cantidad:
                raise Exception(f'Stock insuficiente. Stock actual: {stock_actual}')
        
        # Insertar movimiento
        insert_query = """
            INSERT INTO movimientos_stock 
            (producto_id, tipo, cantidad, motivo, referencia, costo_unitario)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        db_execute(insert_query, (producto_id, tipo, cantidad, motivo, referencia, costo_unitario))
        
        # Actualizar stock del producto
        if tipo == 'ENTRADA':
            update_query = "UPDATE productos SET stock = stock + %s, updated_at = NOW() WHERE id = %s"
        elif tipo == 'SALIDA':
            update_query = "UPDATE productos SET stock = stock - %s, updated_at = NOW() WHERE id = %s"
        else:  # AJUSTE
            update_query = "UPDATE productos SET stock = %s, updated_at = NOW() WHERE id = %s"
        
        db_execute(update_query, (cantidad, producto_id))
        
        return True
    except Exception as e:
        print(f"Error en crear_movimiento_stock: {e}")
        raise e

# ==================== RUTAS API PARA KÁRDEX ====================

@app.route('/api/productos', methods=['GET'])
def get_productos():
    print("📦 Llamada a /api/productos")
    try:
        productos = obtener_productos()
        resultado = []
        for p in productos:
            resultado.append({
                'id': p.get('id'),
                'codigo': p.get('codigo', ''),
                'descripcion': p.get('descripcion', ''),
                'stock': p.get('stock', 0),
                'costo_unitario': float(p.get('costo_unitario', 0)) if p.get('costo_unitario') else 0,
                'familia': p.get('familia', ''),
                'marca': p.get('marca', ''),
                'modelo': p.get('modelo', ''),
                'unidad': p.get('unidad', ''),
                'precio_unitario': float(p.get('precio_unitario', 0)) if p.get('precio_unitario') else 0
            })
        print(f"✅ Se encontraron {len(resultado)} productos")
        return jsonify(resultado)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/productos/<int:id>', methods=['GET'])
def get_producto_by_id(id):
    print(f"🔍 Llamada a /api/productos/{id}")
    try:
        producto = obtener_producto_por_id(id)
        if not producto:
            return jsonify({'success': False, 'error': 'Producto no encontrado'}), 404
        
        return jsonify({
            'id': producto.get('id'),
            'codigo': producto.get('codigo', ''),
            'familia': producto.get('familia', ''),
            'descripcion': producto.get('descripcion', ''),
            'descripcion_larga': producto.get('descripcion_larga', ''),
            'modelo': producto.get('modelo', ''),
            'marca': producto.get('marca', ''),
            'unidad': producto.get('unidad', ''),
            'peso': producto.get('peso', ''),
            'volumen': producto.get('volumen', ''),
            'transporte': producto.get('transporte', ''),
            'costo_unitario': float(producto.get('costo_unitario', 0)) if producto.get('costo_unitario') else 0,
            'precio_unitario': float(producto.get('precio_unitario', 0)) if producto.get('precio_unitario') else 0,
            'stock': producto.get('stock', 0),
            'observaciones': producto.get('observaciones', '')
        })
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/productos/<int:id>', methods=['PUT'])
def update_producto(id):
    print(f"✏️ Llamada a PUT /api/productos/{id}")
    try:
        data = request.get_json()
        
        update_query = """
            UPDATE productos
            SET familia = %s,
                descripcion = %s,
                descripcion_larga = %s,
                modelo = %s,
                marca = %s,
                unidad = %s,
                peso = %s,
                volumen = %s,
                transporte = %s,
                costo_unitario = %s,
                precio_unitario = %s,
                stock = %s,
                observaciones = %s,
                updated_at = NOW()
            WHERE id = %s
        """
        
        db_execute(update_query, (
            data.get('familia'),
            data.get('descripcion'),
            data.get('descripcion_larga'),
            data.get('modelo'),
            data.get('marca'),
            data.get('unidad'),
            data.get('peso'),
            data.get('volumen'),
            data.get('transporte'),
            data.get('costo_unitario'),
            data.get('precio_unitario'),
            data.get('stock'),
            data.get('observaciones'),
            id
        ))
        
        print(f"✅ Producto {id} actualizado correctamente")
        return jsonify({'success': True, 'message': 'Producto actualizado correctamente'})
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/productos/<int:id>', methods=['DELETE'])
def delete_producto(id):
    print(f"🗑️ Llamada a DELETE /api/productos/{id}")
    try:
        # Verificar si tiene movimientos asociados
        movimientos = db_query("SELECT COUNT(*) as count FROM movimientos_stock WHERE producto_id = %s", (id,))
        count = movimientos[0]['count'] if movimientos else 0
        
        if count > 0:
            return jsonify({'success': False, 'error': f'No se puede eliminar el producto porque tiene {count} movimiento(s) de kárdex asociados'}), 400
        
        db_execute("DELETE FROM productos WHERE id = %s", (id,))
        print(f"✅ Producto {id} eliminado correctamente")
        return jsonify({'success': True, 'message': 'Producto eliminado correctamente'})
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/movimientos_stock', methods=['GET'])
def get_movimientos():
    print("📊 Llamada a /api/movimientos_stock")
    try:
        producto_id = request.args.get('producto_id', type=int)
        
        if producto_id:
            movimientos = obtener_movimientos_stock(producto_id)
        else:
            movimientos = []
        
        resultado = []
        for m in movimientos:
            resultado.append({
                'id': m.get('id'),
                'producto_id': m.get('producto_id'),
                'tipo': m.get('tipo'),
                'cantidad': m.get('cantidad'),
                'motivo': m.get('motivo'),
                'referencia': m.get('referencia'),
                'costo_unitario': float(m.get('costo_unitario')) if m.get('costo_unitario') else None,
                'created_at': m.get('created_at').isoformat() if m.get('created_at') else None
            })
        print(f"✅ Se encontraron {len(resultado)} movimientos")
        return jsonify(resultado)
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/movimientos_stock', methods=['POST'])
def crear_movimiento():
    print("📝 Llamada a POST /api/movimientos_stock")
    try:
        data = request.get_json()
        print(f"Datos recibidos: {data}")
        
        if not data.get('producto_id') or not data.get('tipo') or not data.get('cantidad'):
            return jsonify({'success': False, 'error': 'Faltan datos: producto_id, tipo y cantidad son requeridos'}), 400
        
        # Verificar que el producto existe
        producto = obtener_producto_por_id(data['producto_id'])
        if not producto:
            return jsonify({'success': False, 'error': 'Producto no encontrado'}), 404
        
        cantidad = int(data['cantidad'])
        
        # Verificar stock para SALIDA
        if data['tipo'] == 'SALIDA' and producto.get('stock', 0) < cantidad:
            return jsonify({'success': False, 'error': f'Stock insuficiente. Stock actual: {producto.get("stock", 0)}'}), 400
        
        # Crear movimiento y actualizar stock
        crear_movimiento_stock(data)
        
        print(f"✅ Movimiento creado exitosamente")
        return jsonify({'success': True, 'message': 'Movimiento registrado'}), 201
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/ultimo_codigo', methods=['GET'])
def ultimo_codigo():
    try:
        prefijo = request.args.get('prefijo', 'GEN')
        query = """
            SELECT codigo FROM productos 
            WHERE codigo LIKE %s 
            ORDER BY id DESC LIMIT 1
        """
        result = db_query(query, (f'{prefijo}%',))
        
        if result and result[0].get('codigo'):
            codigo = result[0]['codigo']
            import re
            numeros = re.findall(r'\d+', codigo)
            if numeros:
                return jsonify({'success': True, 'ultimo_numero': int(numeros[-1])})
        
        return jsonify({'success': True, 'ultimo_numero': 0})
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        db_query("SELECT 1 as test")
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    return jsonify({'status': 'ok', 'database': db_status})


@app.route('/')
def home():
    return jsonify({'message': 'Servidor funcionando', 'status': 'ok'})


# ==================== BLUEPRINTS ====================
from routes.usuarios import usuarios_bp
from routes.cotizaciones import cotizaciones_bp
from routes.mantenedor_productos import mantenedor_productos_bp

app.register_blueprint(usuarios_bp)
app.register_blueprint(cotizaciones_bp)
app.register_blueprint(mantenedor_productos_bp)

print("🔵 Blueprints registrados:", list(app.blueprints.keys()))
print("🚀 Servidor Flask iniciado")

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)