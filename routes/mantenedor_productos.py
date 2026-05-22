from flask import Blueprint, render_template, request, redirect, flash
import pandas as pd
from app import db
from models.producto import Producto
from models.movimiento_stock import MovimientoStock
from datetime import datetime

mantenedor_productos_bp = Blueprint("mantenedor_productos", __name__)

@mantenedor_productos_bp.route("/mantenedor/productos/gestion")
def gestionar_productos():
    productos = Producto.query.all()
    return render_template("gestion_productos.html", productos=productos)

@mantenedor_productos_bp.route("/mantenedor/productos")
def listar_productos():
    productos = Producto.query.all()
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
        
        # Contar productos existentes para el código
        count = Producto.query.filter(Producto.codigo.like(f'{prefijo}%')).count()
        numero = count + 1
        codigo = f"{prefijo}{str(numero).zfill(3)}"

        # Crear nuevo producto
        nuevo_producto = Producto(
            codigo=codigo,
            familia=familia,
            descripcion=descripcion,
            descripcion_larga=descripcion_larga,
            marca=marca,
            modelo=modelo,
            unidad=unidad,
            peso=peso,
            observaciones=observaciones,
            transporte=transporte,
            costo_unitario=costo_unitario,
            precio_unitario=precio_unitario,
            stock=stock_inicial
        )
        
        db.session.add(nuevo_producto)
        db.session.commit()
        
        # Si hay stock inicial, crear movimiento de entrada
        if stock_inicial > 0:
            movimiento = MovimientoStock(
                producto_id=nuevo_producto.id,
                tipo='ENTRADA',
                cantidad=stock_inicial,
                motivo='Stock inicial',
                costo_unitario=costo_unitario
            )
            db.session.add(movimiento)
            db.session.commit()

        flash(f'✅ Producto creado correctamente (Código: {codigo})', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error al guardar el producto: {str(e)}', 'danger')

    return redirect("/mantenedor/productos")

# ====================== IMPORTAR EXCEL ======================
@mantenedor_productos_bp.route("/mantenedor/productos/importar", methods=["POST"])
def importar_productos():
    flash("⚠️ La importación masiva aún no está actualizada con los nuevos campos", "warning")
    return redirect("/mantenedor/productos")

# ====================== EDITAR PRODUCTO ======================
@mantenedor_productos_bp.route('/mantenedor/productos/editar', methods=['POST'])
def editar_producto():
    try:
        id_producto = request.form['id']
        producto = Producto.query.get(id_producto)
        
        if not producto:
            flash('Producto no encontrado', 'danger')
            return redirect('/mantenedor/productos')
        
        producto.familia = request.form['familia']
        producto.descripcion = request.form['descripcion']
        producto.descripcion_larga = request.form.get('descripcion_larga', '')
        producto.marca = request.form['marca']
        producto.modelo = request.form.get('modelo', '')
        producto.unidad = request.form['unidad']
        producto.peso = request.form.get('peso', '')
        producto.volumen = request.form.get('volumen', '')
        producto.observaciones = request.form.get('observaciones', '')
        producto.transporte = request.form.get('transporte', '')
        producto.costo_unitario = float(request.form.get('costo_unitario', 0))
        producto.precio_unitario = float(request.form.get('precio_unitario', 0))
        producto.updated_at = datetime.now()
        
        db.session.commit()
        flash('Producto actualizado correctamente', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar: {str(e)}', 'danger')

    return redirect('/mantenedor/productos')

# ====================== ELIMINAR ======================
@mantenedor_productos_bp.route('/mantenedor/productos/eliminar', methods=['POST'])
def eliminar_producto():
    try:
        id_producto = request.form['id']
        producto = Producto.query.get(id_producto)
        
        if producto:
            # Verificar si tiene movimientos
            movimientos = MovimientoStock.query.filter_by(producto_id=id_producto).count()
            if movimientos > 0:
                flash(f'No se puede eliminar el producto porque tiene {movimientos} movimiento(s) asociados', 'danger')
            else:
                db.session.delete(producto)
                db.session.commit()
                flash('Producto eliminado correctamente', 'success')
        else:
            flash('Producto no encontrado', 'danger')
            
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar: {str(e)}', 'danger')

    return redirect('/mantenedor/productos')