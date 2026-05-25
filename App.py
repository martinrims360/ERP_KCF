from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.pool import NullPool
import os
import requests  # 👈 IMPORTANTE: Agregar esta línea al inicio
from urllib.parse import quote_plus

app = Flask(__name__)

# ==================== CONFIGURACIÓN SUPABASE CORREGIDA ====================
DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    DATABASE_URL = "postgresql://postgres.tkfmwvsenvgpyexvdcat:admin3561967kcf@aws-1-us-east-1.pooler.supabase.com:6543/postgres"

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'sb_secret_k56lhPYVINqZMj_BZexRbw_JzeBx8Hx'

app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 5,
    'pool_recycle': 300,
    'pool_pre_ping': True,
    'pool_use_lifo': True,
    'connect_args': {
        'connect_timeout': 10,
        'keepalives': 1,
        'keepalives_idle': 30,
        'keepalives_interval': 10,
        'keepalives_count': 5
    }
}

db = SQLAlchemy()
db.init_app(app)

# ==================== IMPORTAR MODELOS ====================
from models.producto import Producto
from models.movimiento_stock import MovimientoStock
from datetime import datetime

# ==================== RUTAS DIRECTAS PARA KÁRDEX ====================

@app.route('/api/productos', methods=['GET'])
def get_productos():
    print("📦 Llamada a /api/productos")
    try:
        productos = Producto.query.all()
        resultado = []
        for p in productos:
            resultado.append({
                'id': p.id,
                'codigo': p.codigo if hasattr(p, 'codigo') else '',
                'descripcion': p.descripcion,
                'stock': p.stock if hasattr(p, 'stock') else 0,
                'costo_unitario': float(p.costo_unitario) if hasattr(p, 'costo_unitario') and p.costo_unitario else 0,
                'familia': p.familia if hasattr(p, 'familia') else '',
                'marca': p.marca if hasattr(p, 'marca') else '',
                'modelo': p.modelo if hasattr(p, 'modelo') else '',
                'unidad': p.unidad if hasattr(p, 'unidad') else '',
                'precio_unitario': float(p.precio_unitario) if hasattr(p, 'precio_unitario') and p.precio_unitario else 0
            })
        print(f"✅ Se encontraron {len(resultado)} productos")
        return jsonify(resultado)
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/productos/<int:id>', methods=['GET'])
def get_producto_by_id(id):
    print(f"🔍 Llamada a /api/productos/{id}")
    try:
        producto = Producto.query.get(id)
        if not producto:
            return jsonify({'success': False, 'error': 'Producto no encontrado'}), 404
        
        resultado = {
            'id': producto.id,
            'codigo': producto.codigo if hasattr(producto, 'codigo') else '',
            'familia': producto.familia if hasattr(producto, 'familia') else '',
            'descripcion': producto.descripcion if hasattr(producto, 'descripcion') else '',
            'descripcion_larga': producto.descripcion_larga if hasattr(producto, 'descripcion_larga') else '',
            'modelo': producto.modelo if hasattr(producto, 'modelo') else '',
            'marca': producto.marca if hasattr(producto, 'marca') else '',
            'unidad': producto.unidad if hasattr(producto, 'unidad') else '',
            'peso': producto.peso if hasattr(producto, 'peso') else '',
            'volumen': producto.volumen if hasattr(producto, 'volumen') else '',
            'transporte': producto.transporte if hasattr(producto, 'transporte') else '',
            'costo_unitario': float(producto.costo_unitario) if hasattr(producto, 'costo_unitario') and producto.costo_unitario else 0,
            'precio_unitario': float(producto.precio_unitario) if hasattr(producto, 'precio_unitario') and producto.precio_unitario else 0,
            'stock': producto.stock if hasattr(producto, 'stock') else 0,
            'observaciones': producto.observaciones if hasattr(producto, 'observaciones') else ''
        }
        print(f"✅ Producto encontrado: {resultado['codigo']}")
        return jsonify(resultado)
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/productos/<int:id>', methods=['PUT'])
def update_producto(id):
    print(f"✏️ Llamada a PUT /api/productos/{id}")
    try:
        producto = Producto.query.get(id)
        if not producto:
            return jsonify({'success': False, 'error': 'Producto no encontrado'}), 404
        
        data = request.get_json()
        
        if 'familia' in data:
            producto.familia = data['familia']
        if 'descripcion' in data:
            producto.descripcion = data['descripcion']
        if 'descripcion_larga' in data:
            producto.descripcion_larga = data['descripcion_larga']
        if 'modelo' in data:
            producto.modelo = data['modelo']
        if 'marca' in data:
            producto.marca = data['marca']
        if 'unidad' in data:
            producto.unidad = data['unidad']
        if 'peso' in data:
            producto.peso = data['peso']
        if 'volumen' in data:
            producto.volumen = data['volumen']
        if 'transporte' in data:
            producto.transporte = data['transporte']
        if 'costo_unitario' in data:
            producto.costo_unitario = data['costo_unitario']
        if 'precio_unitario' in data:
            producto.precio_unitario = data['precio_unitario']
        if 'stock' in data:
            producto.stock = data['stock']
        if 'observaciones' in data:
            producto.observaciones = data['observaciones']
        
        if hasattr(producto, 'updated_at'):
            producto.updated_at = datetime.now()
        
        db.session.commit()
        print(f"✅ Producto {id} actualizado correctamente")
        return jsonify({'success': True, 'message': 'Producto actualizado correctamente'})
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/productos/<int:id>', methods=['DELETE'])
def delete_producto(id):
    print(f"🗑️ Llamada a DELETE /api/productos/{id}")
    try:
        producto = Producto.query.get(id)
        if not producto:
            return jsonify({'success': False, 'error': 'Producto no encontrado'}), 404
        
        try:
            movimientos = MovimientoStock.query.filter_by(producto_id=id).count()
            if movimientos > 0:
                return jsonify({'success': False, 'error': f'No se puede eliminar el producto porque tiene {movimientos} movimiento(s) de kárdex asociados'}), 400
        except:
            pass
        
        codigo = producto.codigo if hasattr(producto, 'codigo') else 'sin código'
        
        db.session.delete(producto)
        db.session.commit()
        
        print(f"✅ Producto {id} ({codigo}) eliminado correctamente")
        return jsonify({'success': True, 'message': 'Producto eliminado correctamente'})
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/movimientos_stock', methods=['GET'])
def get_movimientos():
    print("📊 Llamada a /api/movimientos_stock")
    try:
        producto_id = request.args.get('producto_id', type=int)
        
        if producto_id:
            try:
                movimientos = MovimientoStock.query.filter_by(producto_id=producto_id).order_by(MovimientoStock.created_at.asc()).all()
            except:
                print("⚠️ Tabla movimientos_stock no existe aún")
                return jsonify([])
        else:
            movimientos = []
        
        resultado = []
        for m in movimientos:
            resultado.append({
                'id': m.id,
                'producto_id': m.producto_id,
                'tipo': m.tipo,
                'cantidad': m.cantidad,
                'motivo': m.motivo,
                'referencia': m.referencia,
                'costo_unitario': float(m.costo_unitario) if m.costo_unitario else None,
                'created_at': m.created_at.isoformat() if m.created_at else None
            })
        print(f"✅ Se encontraron {len(resultado)} movimientos")
        return jsonify(resultado)
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify([]), 200

@app.route('/api/movimientos_stock', methods=['POST'])
def crear_movimiento():
    print("📝 Llamada a POST /api/movimientos_stock")
    try:
        data = request.get_json()
        
        if not data.get('producto_id') or not data.get('tipo') or not data.get('cantidad'):
            return jsonify({'success': False, 'error': 'Faltan datos: producto_id, tipo y cantidad son requeridos'}), 400
        
        producto = Producto.query.get(data['producto_id'])
        if not producto:
            return jsonify({'success': False, 'error': 'Producto no encontrado'}), 404
        
        cantidad = int(data['cantidad'])
        
        if data['tipo'] == 'SALIDA' and (producto.stock or 0) < cantidad:
            return jsonify({'success': False, 'error': f'Stock insuficiente. Stock actual: {producto.stock or 0}'}), 400
        
        try:
            nuevo = MovimientoStock(
                producto_id=data['producto_id'],
                tipo=data['tipo'],
                cantidad=cantidad,
                motivo=data.get('motivo'),
                referencia=data.get('referencia'),
                costo_unitario=data.get('costo_unitario')
            )
            db.session.add(nuevo)
        except:
            print("⚠️ Tabla movimientos_stock no existe, creándola...")
            db.create_all()
            
            nuevo = MovimientoStock(
                producto_id=data['producto_id'],
                tipo=data['tipo'],
                cantidad=cantidad,
                motivo=data.get('motivo'),
                referencia=data.get('referencia'),
                costo_unitario=data.get('costo_unitario')
            )
            db.session.add(nuevo)
        
        if data['tipo'] == 'ENTRADA':
            producto.stock = (producto.stock or 0) + cantidad
        elif data['tipo'] == 'SALIDA':
            producto.stock = (producto.stock or 0) - cantidad
        elif data['tipo'] == 'AJUSTE':
            producto.stock = cantidad
        
        if hasattr(producto, 'updated_at'):
            producto.updated_at = datetime.now()
        
        db.session.commit()
        print(f"✅ Movimiento creado exitosamente. Nuevo stock: {producto.stock}")
        return jsonify({'success': True, 'message': 'Movimiento registrado', 'nuevo_stock': producto.stock}), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ultimo_codigo', methods=['GET'])
def ultimo_codigo():
    try:
        prefijo = request.args.get('prefijo', 'GEN')
        print(f"🔢 Buscando último código para prefijo: {prefijo}")
        
        from sqlalchemy import text
        
        with db.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT codigo FROM productos 
                WHERE codigo LIKE :prefijo 
                ORDER BY id DESC LIMIT 1
            """), {"prefijo": f'{prefijo}-%'})
            
            row = result.fetchone()
            
            if row and row[0]:
                try:
                    numero = int(row[0].split('-')[1])
                    return jsonify({'success': True, 'ultimo_numero': numero})
                except (IndexError, ValueError):
                    return jsonify({'success': True, 'ultimo_numero': 0})
            else:
                return jsonify({'success': True, 'ultimo_numero': 0})
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== ENDPOINT PROXY PARA SUNAT (NUEVO) ====================
@app.route('/api/sunat/consulta', methods=['GET'])
def consultar_sunat_proxy():
    """
    Endpoint proxy para consultar SUNAT evitando problemas de CORS
    """
    ruc = request.args.get('ruc')
    
    if not ruc:
        return jsonify({'success': False, 'error': 'RUC no proporcionado'}), 400
    
    if len(ruc) != 11:
        return jsonify({'success': False, 'error': 'RUC debe tener 11 dígitos'}), 400
    
    try:
        # API principal
        url = f'https://api.apis.net.pe/v2/sunat/ruc?numero={ruc}'
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'es-ES,es;q=0.9'
        }
        
        print(f"🔍 Consultando SUNAT para RUC: {ruc}")
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data and data.get('razonSocial'):
                return jsonify({
                    'success': True,
                    'razon_social': data.get('razonSocial', ''),
                    'nombre_comercial': data.get('nombreComercial', ''),
                    'direccion': data.get('direccion', ''),
                    'estado': data.get('estado', '')
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'No se encontraron datos para este RUC'
                })
        else:
            return jsonify({
                'success': False,
                'error': f'Error en API: {response.status_code}'
            })
            
    except requests.exceptions.Timeout:
        return jsonify({
            'success': False,
            'error': 'Tiempo de espera agotado. Intente nuevamente.'
        })
    except requests.exceptions.RequestException as e:
        print(f"Error en proxy SUNAT: {e}")
        return jsonify({
            'success': False,
            'error': 'Error de conexión con SUNAT'
        })
    except Exception as e:
        print(f"Error inesperado: {e}")
        return jsonify({
            'success': False,
            'error': 'Error al consultar SUNAT'
        }), 500

# ==================== CLIENTES API ROUTES ====================

@app.route('/api/clientes/buscar', methods=['GET'])
def api_buscar_clientes():
    try:
        from database import buscar_clientes_paginado
        
        tipo_documento = request.args.get('tipo_documento', '')
        busqueda = request.args.get('busqueda', '').strip()
        pagina = request.args.get('pagina', 1, type=int)
        por_pagina = request.args.get('por_pagina', 100, type=int)
        
        resultado = buscar_clientes_paginado(
            tipo_documento=tipo_documento,
            busqueda=busqueda,
            pagina=pagina,
            por_pagina=por_pagina
        )
        
        for cliente in resultado['data']:
            if 'contactos' in cliente:
                cliente['contactos'] = [
                    {
                        'id': c.get('id'),
                        'nombre_contacto': c.get('nombre'),
                        'email': c.get('email'),
                        'telefono': c.get('telefono'),
                        'cargo': c.get('cargo'),
                        'principal': c.get('principal', False)
                    }
                    for c in cliente.get('contactos', [])
                ]
            
            if 'puntos_entrega' in cliente:
                cliente['puntos_entrega'] = [
                    {
                        'id': p.get('id'),
                        'nombre_punto': p.get('nombre_punto'),
                        'direccion': p.get('direccion'),
                        'departamento': p.get('departamento'),
                        'provincia': p.get('provincia'),
                        'distrito': p.get('distrito'),
                        'telefono': p.get('telefono_contacto'),
                        'responsable': p.get('responsable'),
                        'condicion_pago': p.get('condicion_pago'),
                        'tiempo_credito': p.get('tiempo_credito'),
                        'principal': p.get('principal', False)
                    }
                    for p in cliente.get('puntos_entrega', [])
                ]
        
        return jsonify({
            'success': True,
            'data': resultado['data'],
            'total': resultado['total'],
            'pagina': resultado['pagina'],
            'por_pagina': resultado['por_pagina'],
            'total_paginas': resultado['total_paginas']
        })
        
    except Exception as e:
        print(f"❌ Error en api_buscar_clientes: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'data': []
        }), 500

@app.route('/api/clientes/<int:id>', methods=['GET'])
def api_obtener_cliente(id):
    try:
        from database import obtener_cliente_completo_por_id
        
        cliente = obtener_cliente_completo_por_id(id)
        
        if not cliente:
            return jsonify({
                'success': False,
                'error': 'Cliente no encontrado'
            }), 404
        
        resultado = {
            'id': cliente.get('id'),
            'tipo_documento': cliente.get('tipo_documento'),
            'numero_documento': cliente.get('numero_documento'),
            'razon_social': cliente.get('razon_social'),
            'nombre_comercial': cliente.get('nombre_comercial'),
            'direccion_fiscal': cliente.get('direccion_fiscal'),
            'codigo_cliente': cliente.get('codigo_cliente'),
            'contactos': [
                {
                    'id': c.get('id'),
                    'nombre_contacto': c.get('nombre'),
                    'email': c.get('email'),
                    'telefono': c.get('telefono'),
                    'cargo': c.get('cargo'),
                    'principal': c.get('principal', False)
                }
                for c in cliente.get('contactos', [])
            ],
            'puntos_entrega': [
                {
                    'id': p.get('id'),
                    'nombre_punto': p.get('nombre_punto'),
                    'direccion': p.get('direccion'),
                    'departamento': p.get('departamento'),
                    'provincia': p.get('provincia'),
                    'distrito': p.get('distrito'),
                    'telefono': p.get('telefono_contacto'),
                    'responsable': p.get('responsable'),
                    'condicion_pago': p.get('condicion_pago'),
                    'tiempo_credito': p.get('tiempo_credito'),
                    'principal': p.get('principal', False)
                }
                for p in cliente.get('puntos_entrega', [])
            ]
        }
        
        return jsonify({
            'success': True,
            'data': resultado
        })
        
    except Exception as e:
        print(f"❌ Error en api_obtener_cliente: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/clientes/guardar', methods=['POST'])
def api_guardar_cliente():
    try:
        data = request.get_json()
        from database import insertar_cliente_completo
        
        resultado = insertar_cliente_completo(data)
        
        if resultado and resultado.get('success'):
            return jsonify({
                'success': True,
                'data': {
                    'id': resultado.get('id'),
                    'codigo_cliente': resultado.get('codigo_cliente')
                },
                'message': 'Cliente guardado exitosamente'
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': resultado.get('error', 'Error al guardar cliente')
            }), 400
        
    except Exception as e:
        print(f"❌ Error en api_guardar_cliente: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/clientes/<int:id>', methods=['PUT'])
def api_actualizar_cliente(id):
    try:
        data = request.get_json()
        from database import actualizar_cliente_completo
        
        resultado = actualizar_cliente_completo(id, data)
        
        if resultado and resultado.get('success'):
            return jsonify({
                'success': True,
                'message': 'Cliente actualizado exitosamente'
            })
        else:
            return jsonify({
                'success': False,
                'error': resultado.get('error', 'Error al actualizar cliente')
            }), 400
        
    except Exception as e:
        print(f"❌ Error en api_actualizar_cliente: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/clientes/<int:id>', methods=['DELETE'])
def api_eliminar_cliente(id):
    try:
        from database import eliminar_cliente_db
        
        resultado = eliminar_cliente_db(id)
        
        if resultado and resultado.get('success'):
            return jsonify({
                'success': True,
                'message': 'Cliente eliminado exitosamente'
            })
        else:
            return jsonify({
                'success': False,
                'error': resultado.get('error', 'Error al eliminar cliente')
            }), 400
        
    except Exception as e:
        print(f"❌ Error en api_eliminar_cliente: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== RUTA DE PRUEBA ====================
@app.route('/')
def home():
    return jsonify({'message': 'Servidor funcionando', 'status': 'ok'})

# ==================== BLUEPRINTS ORIGINALES ====================
from routes.usuarios import usuarios_bp
from routes.cotizaciones import cotizaciones_bp
from routes.mantenedor_productos import productos_bp
from routes.mantenedor_clientes import mantenedor_clientes_bp

app.register_blueprint(usuarios_bp)
app.register_blueprint(cotizaciones_bp)
app.register_blueprint(productos_bp)
app.register_blueprint(mantenedor_clientes_bp)

print("🔵 Blueprints registrados:", list(app.blueprints.keys()))
print("🚀 Servidor Flask iniciado")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("✅ Base de datos inicializada")
    app.run(debug=True, host='0.0.0.0', port=5000)