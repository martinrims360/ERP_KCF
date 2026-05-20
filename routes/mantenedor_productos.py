from flask import Blueprint, render_template, request, redirect
from database import db_query, db_execute, obtener_productos
import pandas as pd
from flask import request, redirect, flash
from database import db_query, db_execute

mantenedor_productos_bp = Blueprint("mantenedor_productos", __name__)

@mantenedor_productos_bp.route("/mantenedor/productos/gestion")
def gestionar_productos():
    productos = obtener_productos()  
    return render_template("mantenedor/gestion_productos.html",productos=productos)

@mantenedor_productos_bp.route("/mantenedor/productos")
def listar_productos():
    productos = obtener_productos()
    return render_template("mantenedor/productos.html", productos=productos)
    

@mantenedor_productos_bp.route("/mantenedor/productos/nuevo")
def insertar_producto():
    return render_template("mantenedor/nuevo_producto.html")


@mantenedor_productos_bp.route("/mantenedor/productos/guardar", methods=["POST"])
def guardar_producto():

    familia = request.form["familia"]
    descripcion = request.form["descripcion"]
    descripcion_larga = request.form["descripcion_larga"]
    marca = request.form["marca"]
    modelo = request.form["modelo"]
    unidad = request.form["unidad"]
    peso = request.form["peso"]
    observaciones = request.form["observaciones"]
    transporte = request.form["transporte"]

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

    result = db_query("""
        SELECT COUNT(*) FROM productos WHERE familia = %s
    """, (familia,))

    row = result[0]
    numero = (list(row.values())[0] if isinstance(row, dict) else row[0]) + 1

    codigo = f"{prefijo}{str(numero).zfill(3)}"

    db_execute("""
        INSERT INTO productos 
        (familia, codigo, descripcion, descripcion_larga, marca, modelo, unidad, peso, observaciones, transporte, activo)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,TRUE)
    """, (familia, codigo, descripcion, descripcion_larga, marca, modelo, unidad,peso,observaciones,transporte))

    return redirect("/mantenedor/productos")

@mantenedor_productos_bp.route("/mantenedor/productos/importar", methods=["POST"])
def importar_productos():

    archivo = request.files.get("archivo")

    if not archivo:
        flash("No se seleccionó archivo", "error")
        return redirect("/mantenedor/productos")

    try:
        if archivo.filename.endswith('.csv'):
            df = pd.read_csv(archivo)
        else:
            df = pd.read_excel(archivo)

        insertados = 0
        ignorados = 0

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

        for _, row in df.iterrows():

            familia = row.get("familia")

            if pd.isna(familia):
                ignorados += 1
                continue

            # 🔥 generar código automático
            prefijo = prefijos.get(familia, "GEN")

            result = db_query("""
                SELECT COUNT(*) FROM productos WHERE familia = %s
            """, (familia,))

            row_count = result[0]
            numero = (list(row_count.values())[0] if isinstance(row_count, dict) else row_count[0]) + 1

            codigo = f"{prefijo}{str(numero).zfill(3)}"

            try:
                db_execute("""
                    INSERT INTO productos 
                    (familia, codigo, descripcion, descripcion_larga, marca, modelo, unidad, peso, observaciones, transporte, activo)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE)
                """, (
                    familia,
                    codigo,
                    row.get("descripcion"),
                    row.get("descripcion_larga"),
                    row.get("marca"),
                    row.get("modelo"),
                    row.get("unidad"),
                    row.get("peso"),
                    row.get("observaciones"),
                    row.get("transporte")
                ))

                insertados += 1

            except Exception:
                ignorados += 1

        flash(f"✅ Importados: {insertados} | ⚠️ Ignorados: {ignorados}", "success")

    except Exception as e:
        flash(f"❌ Error: {str(e)}", "error")

    return redirect("/mantenedor/productos")

@mantenedor_productos_bp.route('/mantenedor/productos/editar', methods=['POST'])
def editar_producto():

    id_producto = request.form['id']
    familia = request.form['familia']
    descripcion = request.form['descripcion']
    descripcion_larga = request.form['descripcion_larga']
    marca = request.form['marca']
    modelo = request.form['modelo']
    unidad = request.form['unidad']
    peso = request.form['peso']
    volumen = request.form['volumen']
    observaciones = request.form['observaciones']
    transporte = request.form['transporte']

    query = """
        UPDATE productos
        SET
            familia = %s,
            descripcion = %s,
            descripcion_larga = %s,
            marca = %s,
            modelo = %s,
            unidad = %s,
            peso = %s,
            volumen = %s,
            observaciones = %s,
            transporte = %s
        WHERE id = %s
    """

    valores = (
        familia,
        descripcion,
        descripcion_larga,
        marca,
        modelo,
        unidad,
        peso,
        volumen,
        observaciones,
        transporte,
        id_producto
    )

    db_execute(query, valores)

    flash('Producto actualizado correctamente', 'success')

    return redirect('/mantenedor/productos')

@mantenedor_productos_bp.route('/mantenedor/productos/eliminar', methods=['POST'])
def eliminar_producto():

    id_producto = request.form['id']

    query = """
        DELETE FROM productos
        WHERE id = %s
    """

    db_execute(query, (id_producto,))

    flash('Producto eliminado correctamente', 'danger')

    return redirect('/mantenedor/productos')