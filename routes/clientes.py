from flask import Blueprint, request, jsonify
from database import buscar_clientes, obtener_cliente_completo_por_id,db_tx,obtener_clientes,db_execute

clientes_bp = Blueprint("clientes", __name__)

@clientes_bp.route("/api/clientes/buscar")
def api_buscar_clientes():
    try:
        # Obtener parámetros de búsqueda
        busqueda = request.args.get('busqueda', '').strip()
        tipo_documento = request.args.get('tipo_documento', '')

        # Obtener todos los clientes primero
        data = obtener_clientes()

        # Aplicar filtros si hay búsqueda
        if busqueda:
            busqueda = busqueda.lower()
            data = [
                c for c in data if (
                    (c.get('numero_documento') and busqueda in str(c.get('numero_documento', '')).lower()) or
                    (c.get('razon_social') and busqueda in str(c.get('razon_social', '')).lower()) or
                    (c.get('nombre_comercial') and busqueda in str(c.get('nombre_comercial', '')).lower()) or
                    (c.get('codigo_cliente') and busqueda in str(c.get('codigo_cliente', '')).lower())
                )
            ]

        # Filtrar por tipo de documento si se envía
        if tipo_documento:
            data = [c for c in data if c.get('tipo_documento') == tipo_documento]

        return jsonify({
            "success": True,
            "data": data
        })

    except Exception as e:
        print("🔥 ERROR en búsqueda de clientes:", e)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@clientes_bp.route("/api/clientes/<int:cliente_id>")
def api_cliente_por_id(cliente_id):
    data = obtener_cliente_completo_por_id(cliente_id)

    if not data:
        return jsonify({"success": False, "error": "Cliente no encontrado"}), 404

    return jsonify({
        "success": True,
        "data": data
    })
@clientes_bp.route("/api/clientes/guardar", methods=["POST"])
def guardar_cliente():
    data = request.get_json()

    try:
        tipo_documento = data.get("tipo_documento")
        numero_documento = data.get("numero_documento")
        razon_social = data.get("razon_social")
        direccion = data.get("direccion_fiscal")
        nombre_comercial = data.get("nombre_comercial")

        if not tipo_documento or not numero_documento or not razon_social:
            return jsonify({
                "success": False,
                "error": "Campos obligatorios faltantes"
            }), 400
        # =========================================
        # VALIDAR PRINCIPALES
        # =========================================

        def limpiar_principales(lista):
            encontrado = False
            for item in lista:
                if item.get("principal") and not encontrado:
                    encontrado = True
                else:
                    item["principal"] = False
            return lista

        contactos = limpiar_principales(data.get("contactos", []))
        puntos = limpiar_principales(data.get("puntos_entrega", []))

        with db_tx() as conn:
            cur = conn.cursor()

            # 🔍 validar duplicado
            cur.execute("""
                SELECT id FROM clientes WHERE numero_documento = %s
            """, (numero_documento,))

            if cur.fetchone():
                return jsonify({
                    "success": False,
                    "error": "El cliente ya existe"
                }), 400

            # =========================================
            # INSERTAR CLIENTE
            # =========================================
            cur.execute("""
                INSERT INTO clientes (
                    tipo_documento,
                    numero_documento,
                    razon_social,
                    nombre_comercial,
                    direccion_fiscal
                )
                VALUES (%s,%s,%s,%s,%s)
                RETURNING id
            """, (
                tipo_documento,
                numero_documento,
                razon_social,
                nombre_comercial,
                direccion
            ))

            cliente_id = cur.fetchone()[0]


            # =========================================
            # INSERTAR CONTACTOS
            # =========================================
            for c in contactos:

                cur.execute("""
                    INSERT INTO clientes_contactos (
                        cliente_id,
                        nombre_contacto,
                        cargo,
                        email,
                        telefono,
                        principal
                    )
                    VALUES (%s,%s,%s,%s,%s,%s)
                """, (
                    cliente_id,
                    c.get("nombre_contacto"),
                    c.get("cargo"),
                    c.get("email"),
                    c.get("telefono"),
                    c.get("principal", False)
                ))

            # =========================================
            # INSERTAR PUNTOS ENTREGA
            # =========================================
            for p in puntos:

                cur.execute("""
                    INSERT INTO clientes_puntos_entrega (
                        cliente_id,
                        nombre_punto,
                        direccion,
                        departamento,
                        provincia,
                        distrito,
                        responsable,
                        telefono_contacto,
                        principal,
                        condicion_pago,
                        tiempo_credito
                    )
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, (
                    cliente_id,
                    p.get("nombre"),
                    p.get("direccion"),
                    p.get("departamento"),
                    p.get("provincia"),
                    p.get("distrito"),
                    p.get("responsable"),
                    p.get("telefono_contacto"),
                    p.get("principal", False),
                    p.get("condicion_pago"),
                    p.get("tiempo_credito")
                ))
    

        return jsonify({
            "success": True,
            "message": "Cliente guardado correctamente"
        })
    except Exception as e:

        import traceback

        print("🔥 ERROR ELIMINAR:")
        print(str(e))

        traceback.print_exc()

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    

# =========================================
# EDITAR CLIENTE
# =========================================
@clientes_bp.route('/api/clientes/<int:id>', methods=['PUT'])
def editar_cliente(id):

    data = request.get_json()

    try:
        db_execute("""
            UPDATE clientes
            SET tipo_documento = %s,
                numero_documento = %s,
                razon_social = %s,
                nombre_comercial = %s,
                direccion_fiscal = %s
            WHERE id = %s
        """, (
            data.get('tipo_documento'),
            data.get('numero_documento'),
            data.get('razon_social'),
            data.get('nombre_comercial'),
            data.get('direccion_fiscal'),
            id
        ))

        return jsonify({
            "success": True,
            "message": "Cliente actualizado"
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        })
    
@clientes_bp.route("/api/clientes/<int:cliente_id>", methods=["DELETE"])
def eliminar_cliente(cliente_id):

    try:

        with db_tx() as conn:

            cur = conn.cursor()

            # eliminar contactos
            cur.execute("""
                DELETE FROM clientes_contactos
                WHERE cliente_id = %s
            """, (cliente_id,))

            # eliminar puntos
            cur.execute("""
                DELETE FROM clientes_puntos_entrega
                WHERE cliente_id = %s
            """, (cliente_id,))

            # eliminar cliente
            cur.execute("""
                DELETE FROM clientes
                WHERE id = %s
            """, (cliente_id,))

        return jsonify({
            "success": True
        })
    except Exception as e:

        import traceback

        print("🔥 ERROR ELIMINAR:")
        print(str(e))

        traceback.print_exc()

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

   