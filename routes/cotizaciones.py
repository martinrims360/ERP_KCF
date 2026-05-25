from flask import Blueprint, request, jsonify, render_template
from database import db_tx, db_query
from datetime import datetime
import base64
import os

cotizaciones_bp = Blueprint("cotizaciones", __name__)

# ========================= LISTAR COTIZACIONES =========================
@cotizaciones_bp.route('/api/cotizacion_comercial', methods=['GET'])
def listar_cotizaciones():
    try:
        buscar = request.args.get('buscar', '')
        
        query = """
            SELECT 
                c.id,
                c.codigo_cotizacion,
                c.numero_cotizacion,
                c.correlativo,
                c.estado,
                c.subtotal,
                c.igv,
                c.total,
                c.fecha_creacion,
                cl.razon_social as cliente,
                cl.numero_documento as cliente_ruc,
                u.nombre_completo as vendedor,
                c.es_borrador
            FROM cotizaciones c
            LEFT JOIN clientes cl ON c.cliente_id = cl.id
            LEFT JOIN usuarios u ON c.usuario_id = u.id
            WHERE 1=1
        """
        params = []
        
        if buscar:
            query += """ AND (
                c.codigo_cotizacion ILIKE %s OR 
                c.numero_cotizacion ILIKE %s OR 
                cl.razon_social ILIKE %s OR 
                u.nombre_completo ILIKE %s
            )"""
            busqueda = f"%{buscar}%"
            params = [busqueda, busqueda, busqueda, busqueda]
        
        query += " ORDER BY c.id DESC LIMIT 200"
        
        rows = db_query(query, params)
        
        return jsonify({
            "success": True,
            "data": rows
        })
    except Exception as e:
        print(f"❌ Error listando cotizaciones: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# ========================= OBTENER COTIZACIÓN POR ID =========================
@cotizaciones_bp.route('/api/cotizacion/<int:id>', methods=['GET'])
def obtener_cotizacion(id):
    try:
        query = """
            SELECT 
                c.*,
                cl.razon_social as cliente,
                cl.numero_documento,
                cl.direccion_fiscal,
                u.nombre_completo as vendedor,
                u.email,
                u.telefono
            FROM cotizaciones c
            LEFT JOIN clientes cl ON c.cliente_id = cl.id
            LEFT JOIN usuarios u ON c.usuario_id = u.id
            WHERE c.id = %s
        """
        rows = db_query(query, (id,))
        if not rows:
            return jsonify({"success": False, "error": "Cotización no encontrada"}), 404
        
        cotizacion = dict(rows[0])
        
        # Obtener detalles
        detalle_query = """
            SELECT 
                d.*,
                p.codigo,
                p.descripcion,
                p.marca,
                p.modelo,
                p.unidad
            FROM cotizacion_detalle d
            JOIN productos p ON d.producto_id = p.id
            WHERE d.cotizacion_id = %s
        """
        detalles = db_query(detalle_query, (id,))
        cotizacion['detalle'] = detalles
        
        return jsonify({
            "success": True,
            "data": cotizacion
        })
    except Exception as e:
        print(f"❌ Error obteniendo cotización: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# ========================= GUARDAR COTIZACIÓN =========================
@cotizaciones_bp.route('/api/cotizacion/guardar', methods=['POST'])
def guardar_cotizacion():
    try:
        data = request.get_json()
        
        cliente_id = data.get('cliente_id')
        usuario_id = data.get('usuario_id', 1)
        estado = data.get('estado', 'En Proceso')
        subtotal = float(data.get('subtotal', 0))
        igv = float(data.get('igv', 0))
        total = float(data.get('total', 0))
        forma_pago = data.get('forma_pago', '')
        tiempo_entrega = data.get('tiempo_entrega', '')
        almacen = data.get('almacen', '')
        validez_oferta = data.get('validez_oferta', '15 días')
        nota_cotizacion = data.get('nota_cotizacion', '')
        notas = data.get('notas', '')
        codigo_cotizacion = data.get('codigo_cotizacion', '')
        es_borrador = data.get('es_borrador', True)
        productos = data.get('productos', [])
        
        with db_tx() as conn:
            cur = conn.cursor()
            
            # Si es actualización
            cotizacion_id = data.get('id')
            if cotizacion_id:
                # Actualizar cabecera
                cur.execute("""
                    UPDATE cotizaciones 
                    SET cliente_id = %s,
                        usuario_id = %s,
                        estado = %s,
                        subtotal = %s,
                        igv = %s,
                        total = %s,
                        forma_pago = %s,
                        tiempo_entrega = %s,
                        almacen = %s,
                        validez_oferta = %s,
                        nota_cotizacion = %s,
                        notas = %s,
                        updated_at = NOW()
                    WHERE id = %s
                """, (cliente_id, usuario_id, estado, subtotal, igv, total, 
                      forma_pago, tiempo_entrega, almacen, validez_oferta, 
                      nota_cotizacion, notas, cotizacion_id))
                
                # Eliminar detalles antiguos
                cur.execute("DELETE FROM cotizacion_detalle WHERE cotizacion_id = %s", (cotizacion_id,))
            else:
                # Insertar nueva cotización
                cur.execute("""
                    INSERT INTO cotizaciones 
                    (cliente_id, usuario_id, estado, subtotal, igv, total, 
                     forma_pago, tiempo_entrega, almacen, validez_oferta, 
                     nota_cotizacion, notas, codigo_cotizacion, es_borrador, fecha_creacion)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                    RETURNING id
                """, (cliente_id, usuario_id, estado, subtotal, igv, total,
                      forma_pago, tiempo_entrega, almacen, validez_oferta,
                      nota_cotizacion, notas, codigo_cotizacion, es_borrador))
                
                cotizacion_id = cur.fetchone()[0]
            
            # Insertar detalles
            for idx, item in enumerate(productos):
                cur.execute("""
                    INSERT INTO cotizacion_detalle 
                    (cotizacion_id, producto_id, cantidad, costo_unitario, 
                     precio_venta_unitario, descuento_porcentaje, item)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (cotizacion_id, item.get('producto_id'), item.get('cantidad', 0),
                      item.get('costo_unitario', 0), item.get('precio_venta_unitario', 0),
                      item.get('descuento_porcentaje', 0), idx + 1))
        
        return jsonify({
            "success": True,
            "data": {
                "id": cotizacion_id,
                "codigo_cotizacion": codigo_cotizacion
            }
        })
    except Exception as e:
        print(f"❌ Error guardando cotización: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# ========================= ELIMINAR COTIZACIÓN =========================
@cotizaciones_bp.route('/api/cotizacion_comercial/<int:id>', methods=['DELETE'])
def eliminar_cotizacion(id):
    try:
        with db_tx() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM cotizacion_detalle WHERE cotizacion_id = %s", (id,))
            cur.execute("DELETE FROM cotizaciones WHERE id = %s", (id,))
        return jsonify({"success": True})
    except Exception as e:
        print(f"❌ Error eliminando cotización: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# ========================= GENERAR PDF =========================
@cotizaciones_bp.route('/api/cotizacion/pdf/<int:id>', methods=['GET'])
def generar_pdf_cotizacion(id):
    try:
        # Obtener datos de la cotización
        query = """
            SELECT 
                c.*,
                cl.razon_social as cliente_razon_social,
                cl.numero_documento as cliente_ruc,
                cl.direccion_fiscal as cliente_direccion,
                cl.telefono_contacto as cliente_telefono,
                u.nombre_completo as asesor_comercial,
                u.email as email_contacto,
                u.telefono as telefono_contacto
            FROM cotizaciones c
            LEFT JOIN clientes cl ON c.cliente_id = cl.id
            LEFT JOIN usuarios u ON c.usuario_id = u.id
            WHERE c.id = %s
        """
        rows = db_query(query, (id,))
        if not rows:
            return "Cotización no encontrada", 404
        
        cotizacion = dict(rows[0])
        
        # Obtener detalles
        detalle_query = """
            SELECT 
                d.*,
                p.codigo,
                p.descripcion,
                p.marca,
                p.modelo,
                p.unidad
            FROM cotizacion_detalle d
            JOIN productos p ON d.producto_id = p.id
            WHERE d.cotizacion_id = %s
            ORDER BY d.item
        """
        detalles = db_query(detalle_query, (id,))
        
        # Preparar datos para el template
        productos = []
        for idx, item in enumerate(detalles):
            subtotal_venta = float(item.get('precio_venta_unitario', 0)) * float(item.get('cantidad', 0))
            descuento = float(item.get('descuento_porcentaje', 0))
            subtotal_venta_desc = subtotal_venta * (1 - descuento / 100)
            productos.append({
                'item': idx + 1,
                'codigo': item.get('codigo', ''),
                'descripcion': item.get('descripcion', ''),
                'marca': item.get('marca', ''),
                'modelo': item.get('modelo', ''),
                'cantidad': float(item.get('cantidad', 0)),
                'unidad': item.get('unidad', 'Unid'),
                'precio_venta_unitario': float(item.get('precio_venta_unitario', 0)),
                'subtotal_venta': subtotal_venta,
                'porcentaje_descuento': descuento,
                'subtotal_venta_desc': subtotal_venta_desc
            })
        
        # Renderizar template PDF
        from flask import render_template_string
        
        pdf_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Cotización - KCF CORPORACION</title>
    <style>
        @page { size: A4; margin: 1.5cm; }
        body { font-family: Arial, sans-serif; font-size: 11px; line-height: 1.4; }
        .header { display: flex; justify-content: space-between; border-bottom: 3px solid #d90429; padding-bottom: 10px; margin-bottom: 20px; }
        .logo h1 { color: #d90429; margin: 0; font-size: 18px; }
        .numero-cotizacion { text-align: right; }
        .numero-cotizacion h2 { color: #d90429; margin: 0; font-size: 14px; }
        .info-cliente, .info-condiciones { border: 1px solid #ddd; padding: 10px; margin-bottom: 15px; border-radius: 5px; }
        .info-cliente h3, .info-condiciones h3 { margin: 0 0 10px 0; font-size: 12px; color: #d90429; }
        table { width: 100%; border-collapse: collapse; margin: 15px 0; }
        th { background: #d90429; color: white; padding: 8px; text-align: center; border: 1px solid #b71c1c; }
        td { padding: 6px; border: 1px solid #ddd; text-align: center; }
        .text-right { text-align: right; }
        .totales { width: 300px; margin-left: auto; border: 1px solid #ddd; padding: 10px; border-radius: 5px; }
        .total-final { font-size: 14px; font-weight: bold; color: #d90429; border-top: 2px solid #d90429; padding-top: 8px; margin-top: 8px; }
        .notas { margin-top: 20px; border: 1px solid #ddd; padding: 10px; border-radius: 5px; }
        .footer { margin-top: 30px; text-align: center; font-size: 9px; border-top: 1px solid #ddd; padding-top: 10px; }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">
            <h1>KCF CORPORACION</h1>
            <p>RUC: 20602095704<br>Lima - Perú</p>
        </div>
        <div class="numero-cotizacion">
            <h2>COTIZACIÓN N°: {{ codigo_cotizacion }}</h2>
            <p>Fecha: {{ fecha_actual }}</p>
        </div>
    </div>
    
    <div class="info-cliente">
        <h3>DATOS DEL CLIENTE</h3>
        <p><strong>Señor(es):</strong> {{ cliente_razon_social }}</p>
        <p><strong>RUC/DNI:</strong> {{ cliente_ruc }}</p>
        <p><strong>Dirección:</strong> {{ cliente_direccion }}</p>
    </div>
    
    <div class="info-condiciones">
        <h3>CONDICIONES COMERCIALES</h3>
        <p><strong>Asesor Comercial:</strong> {{ asesor_comercial }}</p>
        <p><strong>Tiempo de Entrega:</strong> {{ tiempo_entrega }}</p>
        <p><strong>Forma de Pago:</strong> {{ forma_pago }}</p>
        <p><strong>Validez de Oferta:</strong> {{ validez_oferta }}</p>
    </div>
    
    <table>
        <thead>
            <tr><th>Item</th><th>Código</th><th>Descripción</th><th>Cant</th><th>P.Unit S/.</th><th>Subtotal S/.</th><th>Total S/.</th></tr>
        </thead>
        <tbody>
            {% for p in productos %}
            <tr>
                <td>{{ p.item }}</td>
                <td>{{ p.codigo }}</td>
                <td>{{ p.descripcion }}</td>
                <td class="text-center">{{ p.cantidad }}</td>
                <td class="text-right">{{ "%.2f"|format(p.precio_venta_unitario) }}</td>
                <td class="text-right">{{ "%.2f"|format(p.subtotal_venta) }}</td>
                <td class="text-right">{{ "%.2f"|format(p.subtotal_venta_desc) }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    
    <div class="totales">
        <div class="text-right"><strong>Subtotal:</strong> S/ {{ "%.2f"|format(subtotal) }}</div>
        <div class="text-right"><strong>IGV 18%:</strong> S/ {{ "%.2f"|format(igv) }}</div>
        <div class="text-right total-final"><strong>TOTAL A PAGAR:</strong> S/ {{ "%.2f"|format(total) }}</div>
    </div>
    
    {% if nota_cotizacion %}
    <div class="notas">
        <h3>NOTAS COMERCIALES</h3>
        <p>{{ nota_cotizacion }}</p>
    </div>
    {% endif %}
    
    <div class="footer">
        <p>Atentamente,<br>Himer Castillo<br>Gerente Comercial<br>📞 Celular: (+51) 999932051<br>✉ Email: ventas@kcfcorporacion.com</p>
    </div>
</body>
</html>
        """
        
        from flask import render_template_string
        html_content = render_template_string(pdf_template,
            codigo_cotizacion=cotizacion.get('codigo_cotizacion', ''),
            fecha_actual=datetime.now().strftime('%d/%m/%Y'),
            cliente_razon_social=cotizacion.get('cliente_razon_social', ''),
            cliente_ruc=cotizacion.get('cliente_ruc', ''),
            cliente_direccion=cotizacion.get('cliente_direccion', ''),
            asesor_comercial=cotizacion.get('asesor_comercial', ''),
            tiempo_entrega=cotizacion.get('tiempo_entrega', ''),
            forma_pago=cotizacion.get('forma_pago', ''),
            validez_oferta=cotizacion.get('validez_oferta', ''),
            subtotal=float(cotizacion.get('subtotal', 0)),
            igv=float(cotizacion.get('igv', 0)),
            total=float(cotizacion.get('total', 0)),
            nota_cotizacion=cotizacion.get('nota_cotizacion', ''),
            productos=productos
        )
        
        from weasyprint import HTML
        import tempfile
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            HTML(string=html_content).write_pdf(tmp.name)
            tmp.seek(0)
            pdf_content = tmp.read()
        
        from flask import send_file
        import io
        return send_file(
            io.BytesIO(pdf_content),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'cotizacion_{cotizacion.get("codigo_cotizacion", "documento")}.pdf'
        )
        
    except Exception as e:
        print(f"❌ Error generando PDF: {e}")
        import traceback
        traceback.print_exc()
        return f"Error generando PDF: {str(e)}", 500