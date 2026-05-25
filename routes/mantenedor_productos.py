from flask import Blueprint, render_template, request, redirect, flash, jsonify
import pandas as pd
from database import db_query, db_execute, obtener_productos, crear_producto_con_stock, db_query_dict

mantenedor_productos_bp = Blueprint("mantenedor_productos", __name__)


@mantenedor_productos_bp.route("/mantenedor/productos/gestion")
def gestionar_productos():
    productos = obtener_productos()
    return render_template("mantenedor/gestion_productos.html", productos=productos)


@mantenedor_productos_bp.route("/mantenedor/productos")
def listar_productos():
    productos = obtener_productos()
    return render_template("mantenedor/productos.html", productos=productos)


@mantenedor_productos_bp.route("/mantenedor/productos/nuevo")
def insertar_producto():
    return render_template("mantenedor/nuevo_producto.html")


# ====================== GUARDAR PRODUCTO ======================
@mantenedor_productos_bp.route("/mantenedor/productos/guardar", methods=["POST"])
def guardar_producto():
    try:
        familia = request.form["familia"]
        descripcion = request.form["descripcion"]
        descripcion_larga = request.form.get("descripcion_larga", "")
        marca = request.form["marca"]
        modelo = request.form.get("modelo", "")
        unidad = request.form["unidad"]
        peso = request.form.get("peso", "")
        observaciones = request.form.get("observaciones", "")
        transporte = request.form.get("transporte", "")

        costo_unitario = float(request.form.get("costo_unitario", 0))
        precio_unitario = float(request.form.get("precio_unitario", 0))
        stock_inicial = int(request.form.get("stock", 0))

        # Generación automática del código
        prefijos = {
            "EQUIPOS DE PROTECCIÓN PERSONAL (EPP)": "EPP",
            "HERRAMIENTAS MANUALES": "HMA",
            "HERRAMIENTAS ELÉCTRICAS": "HEL",
            "MATERIALES ELÉCTRICOS": "MEL",
            "PRODUCTOS QUÍMICOS Y ADHESIVOS": "QUI",
            "MATERIALES DE SEGURIDAD Y SEÑALIZACIÓN": "SEG",
            "EQUIPOS DE SOLDADURA": "SOL",
            "MATERIALES DE EMBALAJE": "EMB",
            "EQUIPOS DE COMUNICACIÓN Y ELECTRÓNICA": "ELE",
            "MOBILIARIO Y EQUIPOS DE OFICINA": "OFI",
            "MATERIALES DE LIMPIEZA Y MANTENIMIENTO": "LIM",
            "REPUESTOS Y ACCESORIOS AUTOMOTRICES": "AUT"
        }

        prefijo = prefijos.get(familia, "GEN")

        result = db_query("SELECT COUNT(*) FROM productos WHERE familia = %s", (familia,))
        row = result[0]
        numero = (list(row.values())[0] if isinstance(row, dict) else row[0]) + 1
        codigo = f"{prefijo}{str(numero).zfill(3)}"

        # Preparar datos para la nueva función
        data = {
            'familia': familia,
            'codigo': codigo,
            'descripcion': descripcion,
            'descripcion_larga': descripcion_larga,
            'marca': marca,
            'modelo': modelo,
            'unidad': unidad,
            'peso': peso,
            'observaciones': observaciones,
            'transporte': transporte,
            'costo_unitario': costo_unitario,
            'precio_unitario': precio_unitario,
            'stock': stock_inicial
        }

        producto_id = crear_producto_con_stock(data)

        flash(f'✅ Producto creado correctamente (Código: {codigo})', 'success')

    except Exception as e:
        flash(f'❌ Error al guardar el producto: {str(e)}', 'danger')

    return redirect("/mantenedor/productos")


# ====================== IMPORTAR EXCEL ======================
@mantenedor_productos_bp.route("/mantenedor/productos/importar", methods=["POST"])
def importar_productos():
    flash("⚠️ La importación masiva aún no está actualizada con los nuevos campos (costo, precio, stock)", "warning")
    return redirect("/mantenedor/productos")


# ====================== EDITAR PRODUCTO ======================
@mantenedor_productos_bp.route('/mantenedor/productos/editar', methods=['POST'])
def editar_producto():
    try:
        id_producto = request.form['id']
        familia = request.form['familia']
        descripcion = request.form['descripcion']
        descripcion_larga = request.form.get('descripcion_larga', '')
        marca = request.form['marca']
        modelo = request.form.get('modelo', '')
        unidad = request.form['unidad']
        peso = request.form.get('peso', '')
        volumen = request.form.get('volumen', '')
        observaciones = request.form.get('observaciones', '')
        transporte = request.form.get('transporte', '')
        costo_unitario = float(request.form.get('costo_unitario', 0))
        precio_unitario = float(request.form.get('precio_unitario', 0))

        db_execute("""
            UPDATE productos
            SET familia = %s,
                descripcion = %s,
                descripcion_larga = %s,
                marca = %s,
                modelo = %s,
                unidad = %s,
                peso = %s,
                volumen = %s,
                observaciones = %s,
                transporte = %s,
                costo_unitario = %s,
                precio_unitario = %s
            WHERE id = %s
        """, (familia, descripcion, descripcion_larga, marca, modelo, unidad, peso,
              volumen, observaciones, transporte, costo_unitario, precio_unitario, id_producto))

        flash('Producto actualizado correctamente', 'success')

    except Exception as e:
        flash(f'Error al actualizar: {str(e)}', 'danger')

    return redirect('/mantenedor/productos')


# ====================== ELIMINAR ======================
@mantenedor_productos_bp.route('/mantenedor/productos/eliminar', methods=['POST'])
def eliminar_producto():
    id_producto = request.form['id']
    db_execute("DELETE FROM productos WHERE id = %s", (id_producto,))
    flash('Producto eliminado correctamente', 'danger')
    return redirect('/mantenedor/productos')


# ====================== API PARA KÁRDEX Y PRODUCTOS ======================

@mantenedor_productos_bp.route("/mantenedor/productos/api/productos", methods=["GET"])
def api_get_productos():
    """API: Obtener todos los productos"""
    try:
        productos = db_query_dict("SELECT id, codigo, descripcion, stock, costo_unitario, precio_unitario, familia, marca, modelo, unidad FROM productos")
        
        for p in productos:
            if p.get('costo_unitario'):
                p['costo_unitario'] = float(p['costo_unitario'])
            if p.get('precio_unitario'):
                p['precio_unitario'] = float(p['precio_unitario'])
            p['stock'] = p.get('stock') or 0
                
        return jsonify(productos)
    except Exception as e:
        print(f"❌ Error en api_get_productos: {e}")
        return jsonify({'error': str(e)}), 500


@mantenedor_productos_bp.route("/mantenedor/productos/api/productos/<int:id>", methods=["GET"])
def api_get_producto(id):
    """API: Obtener un producto por ID"""
    try:
        productos = db_query_dict("SELECT id, codigo, descripcion, descripcion_larga, stock, costo_unitario, precio_unitario, familia, marca, modelo, unidad, peso, volumen, transporte, observaciones FROM productos WHERE id = %s", (id,))
        
        if not productos:
            return jsonify({'error': 'Producto no encontrado'}), 404
        
        p = productos[0]
        
        if p.get('costo_unitario'):
            p['costo_unitario'] = float(p['costo_unitario'])
        if p.get('precio_unitario'):
            p['precio_unitario'] = float(p['precio_unitario'])
        p['stock'] = p.get('stock') or 0
            
        return jsonify(p)
    except Exception as e:
        print(f"❌ Error en api_get_producto: {e}")
        return jsonify({'error': str(e)}), 500


@mantenedor_productos_bp.route("/mantenedor/productos/api/productos/<int:id>", methods=["PUT"])
def api_update_producto(id):
    """API: Actualizar un producto"""
    try:
        data = request.get_json()
        
        campos = []
        valores = []
        
        if 'familia' in data:
            campos.append("familia = %s")
            valores.append(data['familia'])
        if 'descripcion' in data:
            campos.append("descripcion = %s")
            valores.append(data['descripcion'])
        if 'descripcion_larga' in data:
            campos.append("descripcion_larga = %s")
            valores.append(data['descripcion_larga'])
        if 'marca' in data:
            campos.append("marca = %s")
            valores.append(data['marca'])
        if 'modelo' in data:
            campos.append("modelo = %s")
            valores.append(data['modelo'])
        if 'unidad' in data:
            campos.append("unidad = %s")
            valores.append(data['unidad'])
        if 'peso' in data:
            campos.append("peso = %s")
            valores.append(data['peso'])
        if 'volumen' in data:
            campos.append("volumen = %s")
            valores.append(data['volumen'])
        if 'transporte' in data:
            campos.append("transporte = %s")
            valores.append(data['transporte'])
        if 'costo_unitario' in data:
            campos.append("costo_unitario = %s")
            valores.append(data['costo_unitario'])
        if 'precio_unitario' in data:
            campos.append("precio_unitario = %s")
            valores.append(data['precio_unitario'])
        if 'stock' in data:
            campos.append("stock = %s")
            valores.append(data['stock'])
        if 'observaciones' in data:
            campos.append("observaciones = %s")
            valores.append(data['observaciones'])
        
        if not campos:
            return jsonify({'success': False, 'error': 'No hay datos para actualizar'}), 400
        
        valores.append(id)
        sql = f"UPDATE productos SET {', '.join(campos)} WHERE id = %s"
        
        db_execute(sql, valores)
        
        return jsonify({'success': True, 'message': 'Producto actualizado correctamente'})
        
    except Exception as e:
        print(f"❌ Error en api_update_producto: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@mantenedor_productos_bp.route("/mantenedor/productos/api/productos/<int:id>", methods=["DELETE"])
def api_delete_producto(id):
    """API: Eliminar un producto"""
    try:
        db_execute("DELETE FROM productos WHERE id = %s", (id,))
        return jsonify({'success': True, 'message': 'Producto eliminado correctamente'})
        
    except Exception as e:
        print(f"❌ Error en api_delete_producto: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@mantenedor_productos_bp.route("/mantenedor/productos/api/kardex/<int:producto_id>", methods=["GET"])
def api_get_kardex(producto_id):
    """API: Obtener movimientos de kárdex para un producto"""
    try:
        # Verificar si la tabla movimientos_stock existe
        try:
            movimientos = db_query_dict("""
                SELECT id, producto_id, tipo, cantidad, costo_unitario, referencia, motivo, created_at
                FROM movimientos_stock
                WHERE producto_id = %s
                ORDER BY created_at ASC
            """, (producto_id,))
        except:
            # Si la tabla no existe, devolver lista vacía
            return jsonify({
                'success': True,
                'movimientos': [],
                'stock_actual': 0,
                'costo_unitario': 0
            })
        
        # Obtener producto para stock actual
        producto = db_query_dict("SELECT stock, costo_unitario FROM productos WHERE id = %s", (producto_id,))
        stock_actual = producto[0]['stock'] if producto else 0
        costo_unitario = float(producto[0]['costo_unitario']) if producto and producto[0].get('costo_unitario') else 0
        
        # Procesar movimientos
        for m in movimientos:
            if m.get('costo_unitario'):
                m['costo_unitario'] = float(m['costo_unitario'])
            m['cantidad'] = m.get('cantidad') or 0
            if m.get('created_at'):
                m['fecha'] = str(m['created_at'])
        
        return jsonify({
            'success': True,
            'movimientos': movimientos,
            'stock_actual': stock_actual,
            'costo_unitario': costo_unitario
        })
        
    except Exception as e:
        print(f"❌ Error en api_get_kardex: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@mantenedor_productos_bp.route("/mantenedor/productos/api/movimientos", methods=["POST"])
def api_create_movimiento():
    """API: Crear un movimiento de stock"""
    try:
        data = request.get_json()
        
        producto_id = data.get('producto_id')
        tipo = data.get('tipo')
        cantidad = data.get('cantidad')
        costo_unitario = data.get('costo_unitario')
        referencia = data.get('referencia')
        motivo = data.get('motivo')
        
        if not producto_id or not tipo or not cantidad:
            return jsonify({'success': False, 'error': 'Faltan datos requeridos'}), 400
        
        # Crear tabla si no existe
        try:
            db_execute("""
                CREATE TABLE IF NOT EXISTS movimientos_stock (
                    id SERIAL PRIMARY KEY,
                    producto_id INTEGER NOT NULL,
                    tipo VARCHAR(20) NOT NULL,
                    cantidad INTEGER NOT NULL,
                    costo_unitario DECIMAL(10,2),
                    referencia VARCHAR(100),
                    motivo TEXT,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
        except:
            pass
        
        # Obtener stock actual
        producto = db_query_dict("SELECT stock FROM productos WHERE id = %s", (producto_id,))
        if not producto:
            return jsonify({'success': False, 'error': 'Producto no encontrado'}), 404
        
        stock_actual = producto[0]['stock'] or 0
        
        if tipo == 'SALIDA' and stock_actual < cantidad:
            return jsonify({'success': False, 'error': f'Stock insuficiente. Stock actual: {stock_actual}'}), 400
        
        # Calcular nuevo stock
        if tipo == 'ENTRADA':
            nuevo_stock = stock_actual + cantidad
        elif tipo == 'SALIDA':
            nuevo_stock = stock_actual - cantidad
        else:
            nuevo_stock = cantidad
        
        # Insertar movimiento
        db_execute("""
            INSERT INTO movimientos_stock (producto_id, tipo, cantidad, costo_unitario, referencia, motivo)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (producto_id, tipo, cantidad, costo_unitario, referencia, motivo))
        
        # Actualizar stock del producto
        db_execute("UPDATE productos SET stock = %s WHERE id = %s", (nuevo_stock, producto_id))
        
        return jsonify({
            'success': True,
            'message': 'Movimiento registrado correctamente',
            'nuevo_stock': nuevo_stock
        })
        
    except Exception as e:
        print(f"❌ Error en api_create_movimiento: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@mantenedor_productos_bp.route("/mantenedor/productos/api/ultimo_codigo", methods=["GET"])
def api_ultimo_codigo():
    """API: Obtener último código para un prefijo"""
    try:
        prefijo = request.args.get('prefijo', 'GEN')
        
        resultados = db_query_dict("""
            SELECT codigo FROM productos 
            WHERE codigo LIKE %s 
            ORDER BY id DESC LIMIT 1
        """, (f'{prefijo}-%',))
        
        if resultados and resultados[0].get('codigo'):
            try:
                numero = int(resultados[0]['codigo'].split('-')[1])
                return jsonify({'success': True, 'ultimo_numero': numero})
            except:
                return jsonify({'success': True, 'ultimo_numero': 0})
        else:
            return jsonify({'success': True, 'ultimo_numero': 0})
                
    except Exception as e:
        print(f"❌ Error en api_ultimo_codigo: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500