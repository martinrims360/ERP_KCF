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

# ==================== IMPORTAR MODELOS ====================
from models.producto import Producto
from models.movimiento_stock import MovimientoStock

# ==================== IMPORTAR BLUEPRINTS ====================
from routes.usuarios import usuarios_bp
from routes.cotizaciones import cotizaciones_bp
from routes.mantenedor_productos import productos_bp
from routes.kardex import kardex_bp  # ← IMPORTANTE: Debe estar importado

# ==================== REGISTRAR BLUEPRINTS ====================
app.register_blueprint(usuarios_bp)
app.register_blueprint(cotizaciones_bp)
app.register_blueprint(productos_bp)
app.register_blueprint(kardex_bp)  # ← IMPORTANTE: Debe estar registrado

# ==================== RUTA DE PRUEBA ====================
@app.route('/')
def home():
    return jsonify({'message': 'Servidor funcionando', 'status': 'ok'})

# ==================== RUTA DE PRUEBA PARA KÁRDEX ====================
@app.route('/test-kardex')
def test_kardex():
    return jsonify({'message': 'Kardex route test', 'status': 'ok'})

# ==================== RUTAS PARA PLANTILLAS PRINCIPALES ====================
@app.route('/mantenedor')
def mantenedor():
    """Página principal del mantenedor"""
    return render_template('mantenedor.html')

@app.route('/mantenedor/productos')
def gestion_productos():
    """Página de gestión de productos"""
    productos = Producto.query.all()
    return render_template('gestion_productos.html', productos=productos)

@app.route('/mantenedor/productos/guardar', methods=['POST'])
def guardar_producto():
    """Guardar nuevo producto"""
    try:
        # Obtener datos del formulario
        familia = request.form.get('familia')
        marca = request.form.get('marca')
        descripcion = request.form.get('descripcion')
        descripcion_larga = request.form.get('descripcion_larga', '')
        modelo = request.form.get('modelo')
        unidad = request.form.get('unidad')
        volumen = request.form.get('volumen')
        transporte = request.form.get('transporte')
        observaciones = request.form.get('observaciones', '')
        costo_unitario = float(request.form.get('costo_unitario', 0))
        precio_unitario = float(request.form.get('precio_unitario', 0))
        stock = int(request.form.get('stock', 0))
        
        # Procesar peso
        tipo_peso = request.form.get('tipo_peso')
        if tipo_peso == 'exacto':
            peso = request.form.get('peso_exacto')
        else:
            peso = request.form.get('peso_rango')
        
        # Generar código automático (necesitas tener esta función en models/producto.py)
        from models.producto import generar_codigo_producto
        codigo = generar_codigo_producto(familia)
        
        # Crear producto
        nuevo_producto = Producto(
            codigo=codigo,
            familia=familia,
            marca=marca,
            descripcion=descripcion,
            descripcion_larga=descripcion_larga,
            modelo=modelo,
            unidad=unidad,
            peso=peso,
            volumen=volumen,
            transporte=transporte,
            observaciones=observaciones,
            costo_unitario=costo_unitario,
            precio_unitario=precio_unitario,
            stock=stock
        )
        
        db.session.add(nuevo_producto)
        db.session.commit()
        
        # Si hay stock inicial, crear movimiento de entrada
        if stock > 0:
            movimiento = MovimientoStock(
                producto_id=nuevo_producto.id,
                tipo='ENTRADA',
                cantidad=stock,
                motivo='Stock inicial',
                referencia='Registro inicial',
                costo_unitario=costo_unitario
            )
            db.session.add(movimiento)
            db.session.commit()
        
        return redirect('/mantenedor/productos?success=producto_creado')
        
    except Exception as e:
        db.session.rollback()
        print(f"Error al guardar producto: {e}")
        return redirect('/mantenedor/productos?error=' + str(e))

@app.route('/api/productos/<int:id>', methods=['PUT'])
def actualizar_producto(id):
    """Actualizar producto por API"""
    try:
        producto = Producto.query.get(id)
        if not producto:
            return jsonify({'success': False, 'error': 'Producto no encontrado'}), 404
        
        data = request.get_json()
        
        # Actualizar campos
        producto.familia = data.get('familia', producto.familia)
        producto.marca = data.get('marca', producto.marca)
        producto.descripcion = data.get('descripcion', producto.descripcion)
        producto.descripcion_larga = data.get('descripcion_larga', producto.descripcion_larga)
        producto.modelo = data.get('modelo', producto.modelo)
        producto.unidad = data.get('unidad', producto.unidad)
        producto.volumen = data.get('volumen', producto.volumen)
        producto.transporte = data.get('transporte', producto.transporte)
        producto.observaciones = data.get('observaciones', producto.observaciones)
        producto.costo_unitario = data.get('costo_unitario', producto.costo_unitario)
        producto.precio_unitario = data.get('precio_unitario', producto.precio_unitario)
        producto.stock = data.get('stock', producto.stock)
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Producto actualizado'})
        
    except Exception as e:
        db.session.rollback()
        print(f"Error al actualizar producto: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/productos/<int:id>', methods=['DELETE'])
def eliminar_producto(id):
    """Eliminar producto por API"""
    try:
        producto = Producto.query.get(id)
        if not producto:
            return jsonify({'success': False, 'error': 'Producto no encontrado'}), 404
        
        # Eliminar movimientos relacionados primero
        MovimientoStock.query.filter_by(producto_id=id).delete()
        
        # Eliminar producto
        db.session.delete(producto)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Producto eliminado'})
        
    except Exception as e:
        db.session.rollback()
        print(f"Error al eliminar producto: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/productos/<int:id>', methods=['GET'])
def obtener_producto(id):
    """Obtener producto por ID para la API"""
    try:
        producto = Producto.query.get(id)
        if not producto:
            return jsonify({'error': 'Producto no encontrado'}), 404
        
        return jsonify({
            'id': producto.id,
            'codigo': getattr(producto, 'codigo', ''),
            'descripcion': producto.descripcion,
            'stock': getattr(producto, 'stock', 0),
            'costo_unitario': float(producto.costo_unitario) if producto.costo_unitario else 0,
            'precio_unitario': float(producto.precio_unitario) if producto.precio_unitario else 0
        })
    except Exception as e:
        print(f"Error al obtener producto: {e}")
        return jsonify({'error': str(e)}), 500

# ==================== RUTA PARA IMPORTAR EXCEL ====================
@app.route('/mantenedor/productos/importar', methods=['POST'])
def importar_productos_excel():
    """Importar productos desde archivo Excel"""
    try:
        import pandas as pd
        from io import BytesIO
        
        if 'archivo' not in request.files:
            return redirect('/mantenedor/productos?error=No se seleccionó archivo')
        
        archivo = request.files['archivo']
        if archivo.filename == '':
            return redirect('/mantenedor/productos?error=Archivo vacío')
        
        # Leer Excel
        df = pd.read_excel(BytesIO(archivo.read()))
        
        productos_importados = 0
        for _, row in df.iterrows():
            # Generar código automático
            from models.producto import generar_codigo_producto
            familia = row.get('familia', '')
            codigo = generar_codigo_producto(familia)
            
            producto = Producto(
                codigo=codigo,
                familia=familia,
                marca=row.get('marca', ''),
                descripcion=row.get('descripcion', ''),
                modelo=row.get('modelo', ''),
                unidad=row.get('unidad', 'Unidad'),
                costo_unitario=float(row.get('costo_unitario', 0)),
                precio_unitario=float(row.get('precio_unitario', 0)),
                stock=int(row.get('stock', 0))
            )
            db.session.add(producto)
            productos_importados += 1
        
        db.session.commit()
        
        return redirect(f'/mantenedor/productos?success=importados_{productos_importados}')
        
    except Exception as e:
        db.session.rollback()
        print(f"Error al importar Excel: {e}")
        return redirect(f'/mantenedor/productos?error={str(e)}')

print("🔵 Blueprints registrados:", list(app.blueprints.keys()))
print("🚀 Servidor Flask iniciado")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("✅ Base de datos inicializada")
    app.run(debug=True, host='0.0.0.0', port=5000)