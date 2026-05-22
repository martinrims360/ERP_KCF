from flask import Blueprint, render_template, request, redirect, flash
import pandas as pd
from database import db_query, db_execute, obtener_productos, crear_producto_con_stock

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


# ====================== IMPORTAR EXCEL (Pendiente de actualizar) ======================
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