import os
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# =========================
# SUPABASE DATABASE URL
# =========================
# 1. Primero intenta leer la URL limpia que configuraste en Render
DATABASE_URL = os.environ.get('DATABASE_URL')

# 2. Si estás en local y no existe la variable de Render, usa esta por defecto (sin +psycopg2)
if not DATABASE_URL:
    DATABASE_URL = "postgresql://postgres.tkfmwvsenvgpyexvdcat:admin3561967kcf@aws-1-us-east-1.pooler.supabase.com:6543/postgres"

# 3. Por si acaso se te pasa un +psycopg2 en algún lado, esto lo limpia automáticamente:
if DATABASE_URL.startswith("postgresql+psycopg2://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql+psycopg2://", "postgresql://", 1)

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
# Productos - ACTUALIZADA
# =========================
def obtener_productos():
    return db_query("""
        SELECT 
            id, 
            familia, 
            codigo, 
            descripcion, 
            descripcion_larga,
            marca, 
            modelo, 
            unidad,
            peso,
            observaciones,
            transporte,
            costo_unitario,
            precio_unitario,
            stock,
            activo,
            fecha_creacion
        FROM productos
        WHERE activo = TRUE
        ORDER BY familia, codigo
    """)


# =========================
# Insertar proveedor (VERSIÓN ANTIGUA - mantener para compatibilidad)
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
# Obtener proveedores (VERSIÓN ANTIGUA)
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
        SELECT id, tipo_documento, numero_documento, razon_social, direccion_fiscal, codigo_cliente, nombre_comercial
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
        SELECT 
            id, familia, codigo, descripcion, descripcion_larga,
            marca, modelo, unidad, peso, observaciones, transporte,
            costo_unitario, precio_unitario, stock, activo, fecha_creacion
        FROM productos
        WHERE id = %s
        LIMIT 1
    """, (producto_id,))

    if not rows:
        return None

    return dict(rows[0])

# =========================
# Crear Producto con Stock Inicial (Kardex)
# =========================
def crear_producto_con_stock(data):
    """
    Inserta un nuevo producto y registra el stock inicial en el kardex
    """
    with db_tx() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Insertar el producto
        cur.execute("""
            INSERT INTO productos 
            (familia, codigo, descripcion, descripcion_larga, marca, modelo, 
             unidad, peso, observaciones, transporte, 
             costo_unitario, precio_unitario, stock, activo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE)
            RETURNING id
        """, (
            data['familia'],
            data['codigo'],
            data['descripcion'],
            data.get('descripcion_larga', ''),
            data.get('marca', ''),
            data.get('modelo', ''),
            data.get('unidad', 'Unidad'),
            data.get('peso', ''),
            data.get('observaciones', ''),
            data.get('transporte', ''),
            float(data.get('costo_unitario', 0)),
            float(data.get('precio_unitario', 0)),
            int(data.get('stock', 0))
        ))

        producto_id = cur.fetchone()['id']

        # Si hay stock inicial, registrar en kardex
        stock_inicial = int(data.get('stock', 0))
        if stock_inicial > 0:
            cur.execute("""
                INSERT INTO movimientos_stock 
                (producto_id, tipo, cantidad, motivo, referencia, created_at)
                VALUES (%s, 'ENTRADA', %s, 'Stock Inicial', 'Registro al crear producto', NOW())
            """, (producto_id, stock_inicial))

        return producto_id


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


# =========================================
# CLIENTES - NUEVAS FUNCIONES
# =========================================

def insertar_cliente_completo(data):
    """
    Insertar cliente completo con contactos y puntos de entrega
    El código de cliente se genera automáticamente por el trigger
    """
    with db_tx() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # 1. Insertar cliente (NO enviar codigo_cliente)
        cur.execute("""
            INSERT INTO clientes (
                tipo_documento, 
                numero_documento, 
                razon_social, 
                nombre_comercial,
                direccion_fiscal,
                activo
            )
            VALUES (%s, %s, %s, %s, %s, TRUE)
            RETURNING id, codigo_cliente
        """, (
            data.get('tipo_documento'),
            data.get('numero_documento'),
            data.get('razon_social'),
            data.get('nombre_comercial'),
            data.get('direccion_fiscal')
        ))
        
        resultado = cur.fetchone()
        cliente_id = resultado['id']
        codigo_generado = resultado['codigo_cliente']
        
        print(f"✅ Cliente insertado - ID: {cliente_id}, Código: {codigo_generado}")
        
        # 2. Insertar contactos
        contactos = data.get('contactos', [])
        for contacto in contactos:
            cur.execute("""
                INSERT INTO clientes_contactos 
                (cliente_id, nombre, email, telefono, cargo, principal)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                cliente_id,
                contacto.get('nombre_contacto'),
                contacto.get('email'),
                contacto.get('telefono'),
                contacto.get('cargo'),
                contacto.get('principal', False)
            ))
        
        # 3. Insertar puntos de entrega
        puntos = data.get('puntos_entrega', [])
        for punto in puntos:
            cur.execute("""
                INSERT INTO clientes_puntos_entrega 
                (cliente_id, nombre_punto, direccion, departamento, provincia, 
                 distrito, telefono_contacto, responsable, condicion_pago, 
                 tiempo_credito, principal)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                cliente_id,
                punto.get('nombre'),
                punto.get('direccion'),
                punto.get('departamento'),
                punto.get('provincia'),
                punto.get('distrito'),
                punto.get('telefono'),
                punto.get('responsable'),
                punto.get('condicion_pago'),
                punto.get('tiempo_credito'),
                punto.get('principal', False)
            ))
        
        return {
            'id': cliente_id,
            'codigo_cliente': codigo_generado,
            'success': True
        }


def obtener_ultimo_codigo_cliente():
    """Obtener el último código generado de cliente"""
    rows = db_query("""
        SELECT codigo_cliente 
        FROM clientes 
        WHERE codigo_cliente IS NOT NULL 
        ORDER BY id DESC 
        LIMIT 1
    """)
    
    if rows:
        return rows[0]['codigo_cliente']
    return 'CLI-000000'


def obtener_todos_clientes_con_detalles():
    """Obtener todos los clientes con sus contactos y puntos"""
    with db_tx() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Obtener clientes
        cur.execute("""
            SELECT 
                id,
                tipo_documento,
                numero_documento,
                razon_social,
                nombre_comercial,
                direccion_fiscal,
                codigo_cliente,
                activo,
                fecha_creacion
            FROM clientes
            WHERE activo = TRUE
            ORDER BY id DESC
        """)
        
        clientes = cur.fetchall()
        resultado = []
        
        for cliente in clientes:
            cliente_id = cliente['id']
            
            # Obtener contactos
            cur.execute("""
                SELECT id, nombre, email, telefono, cargo, principal
                FROM clientes_contactos
                WHERE cliente_id = %s
            """, (cliente_id,))
            contactos = cur.fetchall()
            
            # Obtener puntos de entrega
            cur.execute("""
                SELECT id, nombre_punto, direccion, departamento, provincia, 
                       distrito, telefono_contacto, responsable, condicion_pago, 
                       tiempo_credito, principal
                FROM clientes_puntos_entrega
                WHERE cliente_id = %s
            """, (cliente_id,))
            puntos = cur.fetchall()
            
            cliente['contactos'] = contactos
            cliente['puntos_entrega'] = puntos
            resultado.append(cliente)
        
        return resultado


def actualizar_cliente_completo(cliente_id, data):
    """Actualizar cliente completo"""
    with db_tx() as conn:
        cur = conn.cursor()
        
        # Actualizar datos básicos
        cur.execute("""
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
            cliente_id
        ))
        
        # Eliminar contactos antiguos y reinsertar
        cur.execute("DELETE FROM clientes_contactos WHERE cliente_id = %s", (cliente_id,))
        for contacto in data.get('contactos', []):
            cur.execute("""
                INSERT INTO clientes_contactos 
                (cliente_id, nombre, email, telefono, cargo, principal)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                cliente_id,
                contacto.get('nombre_contacto'),
                contacto.get('email'),
                contacto.get('telefono'),
                contacto.get('cargo'),
                contacto.get('principal', False)
            ))
        
        # Eliminar puntos antiguos y reinsertar
        cur.execute("DELETE FROM clientes_puntos_entrega WHERE cliente_id = %s", (cliente_id,))
        for punto in data.get('puntos_entrega', []):
            cur.execute("""
                INSERT INTO clientes_puntos_entrega 
                (cliente_id, nombre_punto, direccion, departamento, provincia, 
                 distrito, telefono_contacto, responsable, condicion_pago, 
                 tiempo_credito, principal)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                cliente_id,
                punto.get('nombre_punto'),
                punto.get('direccion'),
                punto.get('departamento'),
                punto.get('provincia'),
                punto.get('distrito'),
                punto.get('telefono'),
                punto.get('responsable'),
                punto.get('condicion_pago'),
                punto.get('tiempo_credito'),
                punto.get('principal', False)
            ))
        
        return {'success': True}


def eliminar_cliente_db(cliente_id):
    """Eliminar cliente (borrado lógico)"""
    db_execute("""
        UPDATE clientes SET activo = FALSE WHERE id = %s
    """, (cliente_id,))
    return {'success': True}


# =========================================
# PROVEEDORES - NUEVAS FUNCIONES
# =========================================

def insertar_proveedor_completo(data):
    """Insertar proveedor completo - El código se genera automáticamente por el trigger"""
    with db_tx() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            INSERT INTO proveedores (
                razon_social,
                razon_comercial,
                ruc,
                direccion,
                telefono,
                contacto,
                email,
                condicion_pago,
                tiempo_credito,
                banco,
                numero_cuenta_cci,
                lugar_recojo,
                activo
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE)
            RETURNING id, codigo_proveedor
        """, (
            data.get('razon_social'),
            data.get('razon_comercial'),
            data.get('ruc'),
            data.get('direccion'),
            data.get('telefono'),
            data.get('contacto'),
            data.get('email'),
            data.get('condicion_pago'),
            data.get('tiempo_credito'),
            data.get('banco'),
            data.get('numero_cuenta_cci'),
            data.get('lugar_recojo')
        ))
        
        resultado = cur.fetchone()
        print(f"✅ Proveedor insertado - ID: {resultado['id']}, Código: {resultado['codigo_proveedor']}")
        
        return {
            'id': resultado['id'],
            'codigo_proveedor': resultado['codigo_proveedor'],
            'success': True
        }


def obtener_todos_proveedores():
    """Obtener todos los proveedores activos"""
    return db_query("""
        SELECT 
            id,
            codigo_proveedor,
            razon_social,
            razon_comercial,
            ruc,
            direccion,
            telefono,
            contacto,
            email,
            condicion_pago,
            tiempo_credito,
            banco,
            numero_cuenta_cci,
            lugar_recojo,
            activo,
            fecha_creacion
        FROM proveedores
        WHERE activo = TRUE
        ORDER BY id DESC
    """)


def obtener_proveedor_por_id(proveedor_id):
    """Obtener proveedor por ID"""
    rows = db_query("""
        SELECT 
            id,
            codigo_proveedor,
            razon_social,
            razon_comercial,
            ruc,
            direccion,
            telefono,
            contacto,
            email,
            condicion_pago,
            tiempo_credito,
            banco,
            numero_cuenta_cci,
            lugar_recojo
        FROM proveedores
        WHERE id = %s AND activo = TRUE
    """, (proveedor_id,))
    
    return rows[0] if rows else None


def actualizar_proveedor(proveedor_id, data):
    """Actualizar proveedor"""
    db_execute("""
        UPDATE proveedores 
        SET razon_social = %s,
            razon_comercial = %s,
            ruc = %s,
            direccion = %s,
            telefono = %s,
            contacto = %s,
            email = %s,
            condicion_pago = %s,
            tiempo_credito = %s,
            banco = %s,
            numero_cuenta_cci = %s,
            lugar_recojo = %s
        WHERE id = %s
    """, (
        data.get('razon_social'),
        data.get('razon_comercial'),
        data.get('ruc'),
        data.get('direccion'),
        data.get('telefono'),
        data.get('contacto'),
        data.get('email'),
        data.get('condicion_pago'),
        data.get('tiempo_credito'),
        data.get('banco'),
        data.get('numero_cuenta_cci'),
        data.get('lugar_recojo'),
        proveedor_id
    ))
    return {'success': True}


def eliminar_proveedor_db(proveedor_id):
    """Eliminar proveedor (borrado lógico)"""
    db_execute("""
        UPDATE proveedores SET activo = FALSE WHERE id = %s
    """, (proveedor_id,))
    return {'success': True}


def obtener_ultimo_codigo_proveedor():
    """Obtener el último código generado de proveedor"""
    rows = db_query("""
        SELECT codigo_proveedor 
        FROM proveedores 
        WHERE codigo_proveedor IS NOT NULL 
        ORDER BY id DESC 
        LIMIT 1
    """)
    
    if rows:
        return rows[0]['codigo_proveedor']
    return 'PROV-000000'


# =========================================
# BUSCAR CLIENTE POR RUC EXACTO (CORREGIDO)
# =========================================
def buscar_cliente_por_ruc(ruc: str):
    """Buscar cliente exactamente por número de RUC"""
    if not ruc or len(ruc) < 3:
        return None
    
    rows = db_query("""
        SELECT 
            id,
            tipo_documento,
            numero_documento,
            razon_social,
            nombre_comercial,
            direccion_fiscal,
            codigo_cliente
        FROM clientes
        WHERE activo = TRUE
        AND numero_documento = %s
        LIMIT 1
    """, (ruc,))
    
    return rows[0] if rows else None

    # =========================================
# FUNCIONES PARA KÁRDEX (MOVIMIENTOS DE STOCK)
# =========================================

def obtener_movimientos_stock_por_producto(producto_id):
    """Obtener todos los movimientos de stock para un producto"""
    try:
        query = """
            SELECT 
                id, 
                producto_id, 
                tipo, 
                cantidad, 
                motivo, 
                referencia, 
                costo_unitario, 
                created_at
            FROM movimientos_stock 
            WHERE producto_id = %s
            ORDER BY created_at ASC
        """
        return db_query(query, (producto_id,))
    except Exception as e:
        print(f"Error en obtener_movimientos_stock_por_producto: {e}")
        return []


def crear_movimiento_stock_completo(data):
    """
    Crear un nuevo movimiento de stock y actualizar el stock del producto
    """
    try:
        producto_id = data.get('producto_id')
        tipo = data.get('tipo')
        cantidad = int(data.get('cantidad', 0))
        motivo = data.get('motivo')
        referencia = data.get('referencia')
        costo_unitario = data.get('costo_unitario')
        
        if not producto_id or not tipo or not cantidad:
            raise ValueError("Faltan datos requeridos")
        
        with db_tx() as conn:
            cur = conn.cursor()
            
            # Verificar stock actual para SALIDA
            if tipo == 'SALIDA':
                cur.execute("SELECT stock FROM productos WHERE id = %s", (producto_id,))
                row = cur.fetchone()
                stock_actual = row[0] if row else 0
                if stock_actual < cantidad:
                    raise Exception(f'Stock insuficiente. Stock actual: {stock_actual}')
            
            # Insertar movimiento
            cur.execute("""
                INSERT INTO movimientos_stock 
                (producto_id, tipo, cantidad, motivo, referencia, costo_unitario, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """, (producto_id, tipo, cantidad, motivo, referencia, costo_unitario))
            
            # Actualizar stock del producto
            if tipo == 'ENTRADA':
                cur.execute("UPDATE productos SET stock = stock + %s, updated_at = NOW() WHERE id = %s", (cantidad, producto_id))
            elif tipo == 'SALIDA':
                cur.execute("UPDATE productos SET stock = stock - %s, updated_at = NOW() WHERE id = %s", (cantidad, producto_id))
            else:  # AJUSTE
                cur.execute("UPDATE productos SET stock = %s, updated_at = NOW() WHERE id = %s", (cantidad, producto_id))
            
            return True
    except Exception as e:
        print(f"Error en crear_movimiento_stock_completo: {e}")
        raise e


def obtener_producto_por_id(producto_id):
    """Obtener un producto por su ID (incluyendo todos los campos)"""
    try:
        query = """
            SELECT 
                id, 
                codigo, 
                familia, 
                descripcion, 
                descripcion_larga,
                modelo, 
                marca, 
                unidad,
                peso,
                volumen,
                transporte,
                costo_unitario,
                precio_unitario,
                stock,
                observaciones,
                activo,
                fecha_creacion
            FROM productos
            WHERE id = %s
        """
        results = db_query(query, (producto_id,))
        return results[0] if results else None
    except Exception as e:
        print(f"Error en obtener_producto_por_id: {e}")
        return None


def actualizar_producto_completo(producto_id, data):
    """Actualizar un producto completo"""
    try:
        query = """
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
        db_execute(query, (
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
            producto_id
        ))
        return True
    except Exception as e:
        print(f"Error en actualizar_producto_completo: {e}")
        raise e


def eliminar_producto_completo(producto_id):
    """Eliminar un producto (borrado lógico o verificar movimientos)"""
    try:
        # Verificar si tiene movimientos asociados
        movimientos = db_query("SELECT COUNT(*) as total FROM movimientos_stock WHERE producto_id = %s", (producto_id,))
        count = movimientos[0]['total'] if movimientos else 0
        
        if count > 0:
            raise Exception(f"No se puede eliminar el producto porque tiene {count} movimiento(s) de kárdex asociados")
        
        db_execute("DELETE FROM productos WHERE id = %s", (producto_id,))
        return True
    except Exception as e:
        print(f"Error en eliminar_producto_completo: {e}")
        raise e


def obtener_ultimo_codigo_por_prefijo(prefijo):
    """Obtener el último número de código para un prefijo"""
    try:
        query = """
            SELECT codigo FROM productos 
            WHERE codigo LIKE %s 
            ORDER BY id DESC LIMIT 1
        """
        results = db_query(query, (f'{prefijo}%',))
        
        if results and results[0].get('codigo'):
            codigo = results[0]['codigo']
            import re
            numeros = re.findall(r'\d+', codigo)
            if numeros:
                return int(numeros[-1])
        return 0
    except Exception as e:
        print(f"Error en obtener_ultimo_codigo_por_prefijo: {e}")
        return 0