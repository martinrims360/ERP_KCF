import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


# =========================
# SUPABASE DATABASE URL
# =========================
DATABASE_URL = "postgresql://postgres.tkfmwvsenvgpyexvdcat:Kcf_10.2%40kcf.com@aws-1-us-east-1.pooler.supabase.com:5432/postgres"


# =========================
# CONEXIÓN
# =========================
def get_connection():

    return psycopg2.connect(
        DATABASE_URL,
        client_encoding="UTF8"
    )


# =========================
# TRANSACCIONES
# =========================
@contextmanager
def db_tx():

    conn = get_connection()

    try:

        yield conn

        conn.commit()

    except Exception:

        conn.rollback()

        raise

    finally:

        conn.close()


# =========================
# QUERY
# =========================
def db_query(sql, params=()):

    conn = get_connection()

    cur = conn.cursor(
        cursor_factory=RealDictCursor
    )

    cur.execute(sql, params)

    data = cur.fetchall()

    cur.close()

    conn.close()

    return data


# =========================
# EXECUTE
# =========================
def db_execute(sql, params=()):

    conn = get_connection()

    cur = conn.cursor()

    cur.execute(sql, params)

    conn.commit()

    cur.close()

    conn.close()

# =====================================
# GUARDAR
# =====================================
def guardar_usuario_db(data):

    conn = get_connection()

    cur = conn.cursor()

    password_hash = generate_password_hash(
        data['password']
    )

    cur.execute("""

        INSERT INTO usuarios (

            usuario,
            password,
            rol,
            nombre_completo,
            email,
            telefono,
            activo

        )

        VALUES (%s,%s,%s,%s,%s,%s,true)

    """, (

        data['usuario'],
        password_hash,
        data['rol'],
        data['nombre_completo'],
        data['email'],
        data['telefono']

    ))

    conn.commit()

    cur.close()
    conn.close()


# =====================================
# LISTAR
# =====================================
def listar_usuarios_db():

    conn = get_connection()

    cur = conn.cursor(
        cursor_factory=RealDictCursor
    )

    cur.execute("""

        SELECT
            id,
            usuario,
            rol,
            nombre_completo,
            email,
            telefono,
            activo,
            fecha_creacion
        FROM usuarios
        ORDER BY id DESC

    """)

    usuarios = cur.fetchall()

    cur.close()
    conn.close()

    return usuarios


# =====================================
# ELIMINAR
# =====================================
def eliminar_usuario_db(id):

    conn = get_connection()

    cur = conn.cursor()

    cur.execute("""

        DELETE FROM usuarios
        WHERE id = %s

    """, (id,))

    conn.commit()

    cur.close()
    conn.close()

# =========================
# Auth
# =========================
def verificar_usuario(usuario: str, password: str):

    rows = db_query("""
        SELECT id, usuario, password, rol, nombre_completo
        FROM usuarios
        WHERE usuario = %s AND activo = TRUE
        LIMIT 1
    """, (usuario,))

    if not rows:
        return None

    u = rows[0]

    if check_password_hash(u["password"], password):

        return {
            "id": u["id"],
            "usuario": u["usuario"],
            "rol": u["rol"],
            "nombre_completo": u["nombre_completo"]
        }

    return None


# =========================
# Productos
# =========================
def obtener_productos():
    return db_query("""
        SELECT id, familia, codigo, descripcion, descripcion_larga,
               marca, modelo, unidad,peso,observaciones,transporte,activo
        FROM productos
        WHERE activo = TRUE
        ORDER BY familia
    """)

# =========================
# Insertar proveedor
# =========================
def insertar_proveedor(
    razon_social,
    ruc,
    direccion,
    telefono="",
    contacto="",
    email="",
    razon_comercial="",
    codigo_proveedor="",
    lugar_recojo="",
    condicion_pago="",
    tiempo_credito="",
    banco="",
    numero_cuenta_cci=""
):

    with db_tx() as conn:

        cur = conn.cursor()

        cur.execute("""

            INSERT INTO proveedores (

                razon_social,
                ruc,
                direccion,
                telefono,
                contacto,
                email,
                razon_comercial,
                codigo_proveedor,
                lugar_recojo,
                condicion_pago,
                tiempo_credito,
                banco,
                numero_cuenta_cci

            )

            VALUES (
                %s,%s,%s,%s,%s,%s,%s,
                %s,%s,%s,%s,%s,%s
            )

        """, (

            razon_social,
            ruc,
            direccion,
            telefono,
            contacto,
            email,
            razon_comercial,
            codigo_proveedor,
            lugar_recojo,
            condicion_pago,
            tiempo_credito,
            banco,
            numero_cuenta_cci

        ))


# =========================
# Obtener proveedores
# =========================
def obtener_proveedores():

    return db_query("""

        SELECT

            id,
            razon_social,
            ruc,
            direccion,
            telefono,
            contacto,
            email,
            razon_comercial,
            codigo_proveedor,
            lugar_recojo,
            condicion_pago,
            tiempo_credito,
            banco,
            numero_cuenta_cci

        FROM proveedores

        WHERE activo = TRUE

        ORDER BY razon_social

    """)


# =========================
# Obtener Clientes
# =========================
def obtener_clientes():

    with db_tx() as conn:

        cur = conn.cursor()

        # =========================================
        # CLIENTES
        # =========================================
        cur.execute("""

            SELECT
                id,
                tipo_documento,
                numero_documento,
                razon_social,
                direccion_fiscal,
                codigo_cliente,
                nombre_comercial

            FROM clientes

            WHERE activo = TRUE

            ORDER BY razon_social

        """)

        clientes = cur.fetchall()

        resultado = []

        for c in clientes:

            cliente_id = c[0]

            # =========================================
            # CONTACTOS
            # =========================================
            cur.execute("""

                SELECT nombre_contacto

                FROM clientes_contactos

                WHERE cliente_id = %s

            """, (cliente_id,))

            contactos = [

                {
                    "nombre_contacto": row[0]
                }

                for row in cur.fetchall()

            ]

            # =========================================
            # PUNTOS ENTREGA
            # =========================================
            cur.execute("""

                SELECT
                    nombre_punto,
                    condicion_pago

                FROM clientes_puntos_entrega

                WHERE cliente_id = %s

            """, (cliente_id,))

            puntos = [

                {
                    "nombre_punto": row[0],
                    "condicion_pago": row[1]
                }

                for row in cur.fetchall()

            ]

            # =========================================
            # OBJETO
            # =========================================
            cliente = {

                "id": c[0],
                "tipo_documento": c[1],
                "numero_documento": c[2],
                "razon_social": c[3],
                "direccion_fiscal": c[4],
                "codigo_cliente": c[5],
                "nombre_comercial": c[6],
                "contactos": contactos,
                "puntos_entrega": puntos

            }

            resultado.append(cliente)

        return resultado

# =========================
# Insertar cliente
# =========================
def insertar_cliente(tipo_documento, numero_documento, razon_social, direccion_fiscal,nombre_comercial):

    rows = db_query("""
        INSERT INTO clientes
        (tipo_documento, numero_documento, razon_social, direccion_fiscal,nombre_comercial)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
    """, (
        tipo_documento,
        numero_documento,
        razon_social,
        direccion_fiscal,
        nombre_comercial
    ))

    return rows[0]["id"]

# =========================
# Insertar producto
# =========================
def insertar_producto(
    familia,
    codigo,
    descripcion,
    descripcion_larga="",
    marca="",
    modelo="",
    unidad="Unidad"):

    rows = db_query("""
        INSERT INTO productos
        (familia, codigo, descripcion, descripcion_larga, marca, modelo, unidad, activo)
        VALUES (%s, %s, %s, %s, %s, %s, %s, TRUE)
        RETURNING id
    """, (
        familia,
        codigo,
        descripcion,
        descripcion_larga,
        marca,
        modelo,
        unidad
    ))

    return rows[0]["id"]

# =========================
# Insertar contacto cliente
# =========================
def insertar_contacto_cliente(cliente_id, nombre_contacto, email, telefono, cargo, principal):

    db_execute("""
        INSERT INTO clientes_contactos
        (cliente_id, nombre, email, telefono, cargo, principal)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        cliente_id,
        nombre_contacto,
        email,
        telefono,
        cargo,
        principal
    ))

# =========================
# Insertar punto entrega
# =========================

def insertar_punto_entrega(
    cliente_id,
    nombre_punto,
    direccion,
    departamento="",
    provincia="",
    distrito="",
    telefono_contacto="",
    responsable="",
    condicion_pago="",
    tiempo_credito="",
    principal=False
):

    db_execute("""
        INSERT INTO clientes_puntos_entrega
        (cliente_id, nombre_punto, direccion, departamento, provincia, distrito,
         telefono_contacto, responsable,condicion_pago,tiempo_credito, principal)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        cliente_id,
        nombre_punto,
        direccion,
        departamento,
        provincia,
        distrito,
        telefono_contacto,
        responsable,
        condicion_pago,
        tiempo_credito,
        principal
    ))

# =========================
# Buscar clientes
# =========================
def buscar_clientes(q: str, limit: int = 10):

    q = (q or "").strip()

    if len(q) < 2:
        return []

    return db_query("""
        SELECT id, tipo_documento, numero_documento, razon_social, direccion_fiscal,codigo_cliente,nombre_comercial
        FROM clientes
        WHERE activo = TRUE
        AND (numero_documento ILIKE %s OR razon_social ILIKE %s)
        ORDER BY razon_social
        LIMIT %s
    """, (f"%{q}%", f"%{q}%", limit))


# =========================
# Buscar productos
# =========================
def buscar_productos(q: str, limit: int = 15):

    q = (q or "").strip()

    if len(q) < 2:
        return []

    return db_query("""
        SELECT id, codigo, descripcion, marca, modelo, unidad, familia
        FROM productos
        WHERE activo = TRUE
        AND (codigo ILIKE %s OR descripcion ILIKE %s)
        ORDER BY descripcion
        LIMIT %s
    """, (f"%{q}%", f"%{q}%", limit))
# ===============================
# obtener_cliente_completo_por_id
# ===============================
def obtener_cliente_completo_por_id(cliente_id):

    rows = db_query("""
        SELECT *
        FROM clientes
        WHERE id = %s
        LIMIT 1
    """, (cliente_id,))

    if not rows:
        return None

    cliente = dict(rows[0])

    # contactos del cliente
    contactos = db_query("""
        SELECT *
        FROM clientes_contactos
        WHERE cliente_id = %s
    """, (cliente_id,))

    # puntos de entrega
    puntos = db_query("""
        SELECT *
        FROM clientes_puntos_entrega
        WHERE cliente_id = %s
    """, (cliente_id,))

    cliente["contactos"] = [dict(c) for c in contactos]
    cliente["puntos_entrega"] = [dict(p) for p in puntos]

    return cliente
# ================================
# obtener_producto_completo_por_id
# ================================
def obtener_producto_completo_por_id(producto_id):

    rows = db_query("""
        SELECT id, familia, codigo, descripcion, descripcion_larga,
               marca, modelo, unidad, activo, fecha_creacion
        FROM productos
        WHERE id = %s
        LIMIT 1
    """, (producto_id,))

    if not rows:
        return None

    return dict(rows[0])

# =========================
# Cotizaciones recientes
# =========================
def obtener_cotizaciones_recientes(limit: int = 200):

    return db_query("""
        SELECT
            c.id,
            c.numero_cotizacion,
            c.fecha_creacion,
            c.estado,
            c.total,
            cl.razon_social AS cliente_razon_social,
            cl.numero_documento AS cliente_ruc
        FROM cotizaciones c
        JOIN clientes cl ON c.cliente_id = cl.id 
        ORDER BY c.id DESC
        LIMIT %s
    """, (limit,))


# ==============================
# Crear o guardar cotización transaccional
# ==============================
def crear_cotizacion_transaccional(payload: dict, usuario_id: int):

    cliente_id = payload.get("cliente_id")
    productos = payload.get("productos", [])

    if not cliente_id:                          
        raise ValueError("cliente_id es requerido")

    if not productos:
        raise ValueError("Debe enviar productos")

    with db_tx() as conn:

        cur = conn.cursor(cursor_factory=RealDictCursor)

        prefix = f"COT-{datetime.now().strftime('%y%m')}"

        cur.execute("""
            SELECT numero_cotizacion
            FROM cotizaciones
            WHERE numero_cotizacion LIKE %s
            ORDER BY id DESC
            LIMIT 1
        """, (f"{prefix}%",))

        row = cur.fetchone()
        nuevo = 1

        if row:
            try:
                nuevo = int(row["numero_cotizacion"][-4:]) + 1
            except:
                pass

        numero = f"{prefix}{nuevo:04d}"

        cur.execute("""
            INSERT INTO cotizaciones
            (numero_cotizacion, cliente_id, estado, subtotal, igv, total, usuario_id, notas)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            RETURNING id
        """, (
            numero,
            int(cliente_id),
            payload.get("estado", "En Proceso"),
            float(payload.get("subtotal", 0)),
            float(payload.get("igv", 0)),
            float(payload.get("total", 0)),
            int(usuario_id),
            payload.get("notas", "")
        ))

        cotizacion_id = cur.fetchone()["id"]

        for item in productos:
            cur.execute("""
                INSERT INTO cotizacion_detalle
                (cotizacion_id, producto_id, cantidad)
                VALUES (%s,%s,%s)
            """, (
                cotizacion_id,
                int(item["producto_id"]),
                float(item["cantidad"])
            ))

        return {
            "cotizacion_id": cotizacion_id,
            "numero_cotizacion": numero
        }
# ==========================
# Obtener cotización completa
# ==========================
def obtener_cotizacion_completa(cotizacion_id):

    # cabecera de la cotización
    rows = db_query("""
    SELECT 
        c.*,
                    
        cl.razon_social,
        cl.numero_documento AS cliente_ruc,
        cl.direccion_fiscal,
                    
        co.nombre_contacto,
        
        de.descuento_porcentaje,
                    
        pe.nombre_punto,
        pe.direccion,
        pe.telefono_contacto,
                    
        u.nombre_completo,
        u.email,
        u.telefono,
                    
        c.forma_pago,
        c.tiempo_entrega,
        c.almacen,
        c.validez_oferta
                    
        

    FROM cotizaciones c
                    
    JOIN clientes cl 
        ON c.cliente_id = cl.id
                    
    LEFT JOIN clientes_puntos_entrega pe 
        ON pe.cliente_id = cl.id
        
    JOIN usuarios u 
        ON u.id = c.usuario_id
    
   LEFT JOIN clientes_contactos co
        ON co.cliente_id = cl.id
                    
   LEFT JOIN cotizacion_detalle de
        ON de.cotizacion_id = de.producto_id
                    
    WHERE c.id = %s
    LIMIT 1
""", (cotizacion_id,))
    
    if not rows:
        return None

    cotizacion = dict(rows[0])

    # detalle de productos
    detalle = db_query("""
        SELECT 
            d.*,
            p.descripcion,
            p.codigo,
            p.marca,
            p.modelo
        FROM cotizacion_detalle d
        JOIN productos p ON p.id = d.producto_id
        WHERE d.cotizacion_id = %s
    """, (cotizacion_id,))

    cotizacion["detalle"] = [dict(d) for d in detalle]

    return {
    "cabecera": cotizacion,
    "detalle": cotizacion["detalle"]
}

# =========================
# Crear usuario
# =========================
def crear_usuario(usuario: str, password: str, rol: str, nombre_completo: str, email: str = ""):

    pwd_hash = generate_password_hash(password)

    with db_tx() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO usuarios (usuario, password, rol, nombre_completo, email)
            VALUES (%s,%s,%s,%s,%s)
        """, (usuario, pwd_hash, rol, nombre_completo, email))