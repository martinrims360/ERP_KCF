# database.py
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = os.environ.get("ERP_DB_PATH", "sistema_gestion.db")


# =========================
# Conexión y transacciones
# =========================
def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    return conn


def _connect():
    return get_connection()


@contextmanager
def db_tx():
    conn = _connect()
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def db_query(sql: str, params: tuple = ()):
    conn = _connect()
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        cur = conn.execute(sql, params)
        rows = cur.fetchall()
        return rows
    finally:
        conn.close()


# =========================
# Inicialización
# =========================
def init_db():
    with db_tx() as conn:
        # Usuarios
        conn.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            rol TEXT NOT NULL CHECK(rol IN ('administrador', 'usuario')),
            nombre_completo TEXT NOT NULL,
            email TEXT,
            activo BOOLEAN DEFAULT 1,
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Clientes
        conn.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo_documento TEXT NOT NULL CHECK(tipo_documento IN ('RUC', 'DNI')),
            numero_documento TEXT UNIQUE NOT NULL,
            razon_social TEXT NOT NULL,
            direccion_fiscal TEXT NOT NULL,
            activo BOOLEAN DEFAULT 1,
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS clientes_contactos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            nombre_contacto TEXT NOT NULL,
            email TEXT,
            telefono TEXT,
            cargo TEXT,
            principal BOOLEAN DEFAULT 0,
            activo BOOLEAN DEFAULT 1,
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cliente_id) REFERENCES clientes (id)
        )
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS clientes_puntos_entrega (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            nombre_punto TEXT NOT NULL,
            direccion TEXT NOT NULL,
            departamento TEXT,
            provincia TEXT,
            distrito TEXT,
            telefono_contacto TEXT,
            responsable TEXT,
            principal BOOLEAN DEFAULT 0,
            activo BOOLEAN DEFAULT 1,
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cliente_id) REFERENCES clientes (id)
        )
        """)

        # Proveedores
        conn.execute("""
        CREATE TABLE IF NOT EXISTS proveedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            razon_social TEXT NOT NULL,
            ruc TEXT UNIQUE NOT NULL,
            direccion TEXT NOT NULL,
            telefono TEXT,
            contacto TEXT,
            email TEXT,
            activo BOOLEAN DEFAULT 1,
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Productos
        conn.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            familia TEXT NOT NULL,
            codigo TEXT UNIQUE NOT NULL,
            descripcion TEXT NOT NULL,
            descripcion_larga TEXT,
            marca TEXT,
            modelo TEXT,
            unidad TEXT NOT NULL,
            activo BOOLEAN DEFAULT 1,
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Listas de precios
        conn.execute("""
        CREATE TABLE IF NOT EXISTS listas_precios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producto_id INTEGER NOT NULL,
            precio_venta DECIMAL(10,2) NOT NULL,
            margen DECIMAL(5,2) NOT NULL,
            vigente_desde DATE NOT NULL,
            vigente_hasta DATE,
            activo BOOLEAN DEFAULT 1,
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (producto_id) REFERENCES productos (id)
        )
        """)

        # Cotizaciones
        conn.execute("""
        CREATE TABLE IF NOT EXISTS cotizaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_cotizacion TEXT UNIQUE NOT NULL,
            cliente_id INTEGER NOT NULL,
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
            estado TEXT NOT NULL CHECK(estado IN ('En Proceso', 'Generada', 'Aceptada por Cliente', 'Rechazada')),
            subtotal DECIMAL(12,2) DEFAULT 0,
            igv DECIMAL(12,2) DEFAULT 0,
            total DECIMAL(12,2) DEFAULT 0,
            usuario_id INTEGER NOT NULL,
            notas TEXT,
            FOREIGN KEY (cliente_id) REFERENCES clientes (id),
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS cotizacion_detalle (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cotizacion_id INTEGER NOT NULL,
            producto_id INTEGER NOT NULL,
            cantidad DECIMAL(12,3) NOT NULL,

            costo_unitario DECIMAL(12,4) DEFAULT 0,
            subtotal_costo DECIMAL(12,2) DEFAULT 0,

            margen_porcentaje DECIMAL(6,2) DEFAULT 0,
            precio_venta_unitario DECIMAL(12,4) DEFAULT 0,
            subtotal_venta DECIMAL(12,2) DEFAULT 0,

            descuento_porcentaje DECIMAL(6,2) DEFAULT 0,
            precio_venta_con_descuento DECIMAL(12,4) DEFAULT 0,
            subtotal_venta_con_descuento DECIMAL(12,2) DEFAULT 0,

            descuento_total DECIMAL(12,2) DEFAULT 0,
            margen_final DECIMAL(12,2) DEFAULT 0,

            FOREIGN KEY (cotizacion_id) REFERENCES cotizaciones (id),
            FOREIGN KEY (producto_id) REFERENCES productos (id)
        )
        """)

        # Índices
        conn.execute("CREATE INDEX IF NOT EXISTS idx_clientes_doc ON clientes(numero_documento)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_productos_codigo ON productos(codigo)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_cotizaciones_numero ON cotizaciones(numero_cotizacion)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_detalle_cotizacion ON cotizacion_detalle(cotizacion_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_detalle_producto ON cotizacion_detalle(producto_id)")


# =========================
# Auth
# =========================
def verificar_usuario(usuario: str, password: str):
    row = db_query("""
        SELECT id, usuario, password, rol, nombre_completo
        FROM usuarios
        WHERE usuario = ? AND activo = 1
        LIMIT 1
    """, (usuario,))
    if not row:
        return None

    u = row[0]
    if check_password_hash(u["password"], password):
        return {
            "id": u["id"],
            "usuario": u["usuario"],
            "rol": u["rol"],
            "nombre_completo": u["nombre_completo"]
        }
    return None


# =========================
# Lecturas mantenedor
# =========================
def obtener_productos():
    rows = db_query("SELECT * FROM productos WHERE activo = 1 ORDER BY descripcion")
    return [dict(r) for r in rows]


def obtener_proveedores():
    rows = db_query("SELECT * FROM proveedores WHERE activo = 1 ORDER BY razon_social")
    return [dict(r) for r in rows]


def obtener_clientes_completos():
    clientes = db_query("SELECT * FROM clientes WHERE activo = 1 ORDER BY razon_social")
    out = []

    conn = _connect()
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")

        for c in clientes:
            cliente_id = c["id"]

            contactos = conn.execute("""
                SELECT * FROM clientes_contactos
                WHERE cliente_id = ? AND activo = 1
                ORDER BY principal DESC, nombre_contacto
            """, (cliente_id,)).fetchall()

            puntos = conn.execute("""
                SELECT * FROM clientes_puntos_entrega
                WHERE cliente_id = ? AND activo = 1
                ORDER BY principal DESC, nombre_punto
            """, (cliente_id,)).fetchall()

            out.append({
                "id": c["id"],
                "tipo_documento": c["tipo_documento"],
                "numero_documento": c["numero_documento"],
                "razon_social": c["razon_social"],
                "direccion_fiscal": c["direccion_fiscal"],
                "contactos": [dict(x) for x in contactos],
                "puntos_entrega": [dict(x) for x in puntos],
            })
    finally:
        conn.close()

    return out


def obtener_cliente_completo_por_id(cliente_id: int):
    conn = _connect()
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")

        c = conn.execute("""
            SELECT * FROM clientes WHERE id = ? AND activo = 1
        """, (cliente_id,)).fetchone()

        if not c:
            return None

        contactos = conn.execute("""
            SELECT * FROM clientes_contactos
            WHERE cliente_id = ? AND activo = 1
            ORDER BY principal DESC, nombre_contacto
        """, (cliente_id,)).fetchall()

        puntos = conn.execute("""
            SELECT * FROM clientes_puntos_entrega
            WHERE cliente_id = ? AND activo = 1
            ORDER BY principal DESC, nombre_punto
        """, (cliente_id,)).fetchall()

        return {
            "id": c["id"],
            "tipo_documento": c["tipo_documento"],
            "numero_documento": c["numero_documento"],
            "razon_social": c["razon_social"],
            "direccion_fiscal": c["direccion_fiscal"],
            "contactos": [dict(x) for x in contactos],
            "puntos_entrega": [dict(x) for x in puntos],
        }
    finally:
        conn.close()


def obtener_producto_completo_por_id(producto_id: int):
    rows = db_query("SELECT * FROM productos WHERE id = ? AND activo = 1", (producto_id,))
    return dict(rows[0]) if rows else None


# =========================
# Inserciones mantenedor
# =========================
def insertar_cliente(tipo_documento, numero_documento, razon_social, direccion_fiscal):
    with db_tx() as conn:
        cur = conn.execute("""
            INSERT INTO clientes (tipo_documento, numero_documento, razon_social, direccion_fiscal)
            VALUES (?, ?, ?, ?)
        """, (tipo_documento, numero_documento, razon_social, direccion_fiscal))
        return cur.lastrowid


def insertar_contacto_cliente(cliente_id, nombre_contacto, email="", telefono="", cargo="", principal=False):
    with db_tx() as conn:
        conn.execute("""
            INSERT INTO clientes_contactos (cliente_id, nombre_contacto, email, telefono, cargo, principal)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (cliente_id, nombre_contacto, email, telefono, cargo, int(bool(principal))))


def insertar_punto_entrega(cliente_id, nombre_punto, direccion, departamento="", provincia="", distrito="",
                          telefono_contacto="", responsable="", principal=False):
    with db_tx() as conn:
        conn.execute("""
            INSERT INTO clientes_puntos_entrega
            (cliente_id, nombre_punto, direccion, departamento, provincia, distrito,
             telefono_contacto, responsable, principal)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (cliente_id, nombre_punto, direccion, departamento, provincia, distrito,
              telefono_contacto, responsable, int(bool(principal))))


def insertar_proveedor(razon_social, ruc, direccion, telefono="", contacto="", email=""):
    with db_tx() as conn:
        conn.execute("""
            INSERT INTO proveedores (razon_social, ruc, direccion, telefono, contacto, email)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (razon_social, ruc, direccion, telefono, contacto, email))


PREFIJOS_FAMILIA = {
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


def generar_codigo_producto(familia: str) -> str:
    prefijo = PREFIJOS_FAMILIA.get(familia, "GEN")
    rows = db_query("""
        SELECT codigo FROM productos
        WHERE codigo LIKE ?
        ORDER BY codigo DESC
        LIMIT 1
    """, (f"{prefijo}%",))
    if rows:
        ultimo = rows[0]["codigo"]
        try:
            ultimo_num = int(ultimo[3:])
            nuevo = ultimo_num + 1
        except ValueError:
            nuevo = 1
    else:
        nuevo = 1
    return f"{prefijo}{nuevo:03d}"


def insertar_producto(familia, descripcion, descripcion_larga="", marca="", modelo="", unidad="Unidad"):
    codigo = generar_codigo_producto(familia)
    with db_tx() as conn:
        conn.execute("""
            INSERT INTO productos (familia, codigo, descripcion, descripcion_larga, marca, modelo, unidad)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (familia, codigo, descripcion, descripcion_larga, marca, modelo, unidad))
    return codigo


# =========================
# Búsquedas
# =========================
def buscar_clientes(q: str, limit: int = 10):
    q = (q or "").strip()
    if len(q) < 2:
        return []

    rows = db_query("""
        SELECT id, tipo_documento, numero_documento, razon_social, direccion_fiscal
        FROM clientes
        WHERE activo = 1
          AND (numero_documento LIKE ? OR razon_social LIKE ?)
        ORDER BY razon_social
        LIMIT ?
    """, (f"%{q}%", f"%{q}%", limit))

    return [dict(r) for r in rows]


def buscar_productos(q: str, limit: int = 15):
    q = (q or "").strip()
    if len(q) < 2:
        return []

    rows = db_query("""
        SELECT id, codigo, descripcion, marca, modelo, unidad, familia
        FROM productos
        WHERE activo = 1
          AND (codigo LIKE ? OR descripcion LIKE ?)
        ORDER BY descripcion
        LIMIT ?
    """, (f"%{q}%", f"%{q}%", limit))

    return [dict(r) for r in rows]


def obtener_producto_id_por_codigo(codigo: str):
    codigo = (codigo or "").strip()
    rows = db_query("SELECT id FROM productos WHERE codigo = ? AND activo = 1 LIMIT 1", (codigo,))
    return rows[0]["id"] if rows else None


# =========================
# Cotizaciones
# =========================
def obtener_cotizaciones_recientes(limit: int = 200):
    rows = db_query("""
        SELECT
            c.id,
            c.numero_cotizacion,
            c.fecha_creacion,
            c.estado,
            c.total,
            cl.razon_social AS cliente_razon_social
        FROM cotizaciones c
        JOIN clientes cl ON cl.id = c.cliente_id
        ORDER BY c.id DESC
        LIMIT ?
    """, (limit,))
    return [dict(r) for r in rows]


def _generar_numero_cotizacion(conn) -> str:
    prefix = f"COT-{datetime.now().strftime('%y%m')}"
    row = conn.execute("""
        SELECT numero_cotizacion
        FROM cotizaciones
        WHERE numero_cotizacion LIKE ?
        ORDER BY id DESC
        LIMIT 1
    """, (f"{prefix}%",)).fetchone()

    nuevo = 1
    if row:
        try:
            nuevo = int(row["numero_cotizacion"][-4:]) + 1
        except ValueError:
            nuevo = 1
    return f"{prefix}{nuevo:04d}"


def crear_cotizacion_transaccional(payload: dict, usuario_id: int) -> dict:
    if not payload or not isinstance(payload, dict):
        raise ValueError("Payload inválido")

    cliente_id = payload.get("cliente_id")
    productos = payload.get("productos", [])

    if not cliente_id:
        raise ValueError("cliente_id es requerido")
    if not productos or not isinstance(productos, list):
        raise ValueError("Debe enviar productos")

    with db_tx() as conn:
        numero = _generar_numero_cotizacion(conn)

        cur = conn.execute("""
            INSERT INTO cotizaciones
            (numero_cotizacion, cliente_id, estado, subtotal, igv, total, usuario_id, notas)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            numero,
            int(cliente_id),
            payload.get("estado", "En Proceso"),
            float(payload.get("subtotal", 0) or 0),
            float(payload.get("igv", 0) or 0),
            float(payload.get("total", 0) or 0),
            int(usuario_id),
            payload.get("notas", "")
        ))

        cotizacion_id = cur.lastrowid

        for item in productos:
            if not isinstance(item, dict):
                raise ValueError("Item inválido")

            producto_id = item.get("producto_id")
            cantidad = item.get("cantidad")

            if not producto_id:
                raise ValueError("producto_id es requerido en cada item")
            if cantidad is None:
                raise ValueError("cantidad es requerida en cada item")

            conn.execute("""
                INSERT INTO cotizacion_detalle
                (cotizacion_id, producto_id, cantidad,
                 costo_unitario, subtotal_costo,
                 margen_porcentaje, precio_venta_unitario, subtotal_venta,
                 descuento_porcentaje, precio_venta_con_descuento,
                 subtotal_venta_con_descuento, descuento_total, margen_final)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cotizacion_id,
                int(producto_id),
                float(cantidad),

                float(item.get("costo_unitario", 0) or 0),
                float(item.get("subtotal_costo", 0) or 0),

                float(item.get("margen_porcentaje", 0) or 0),
                float(item.get("precio_venta_unitario", 0) or 0),
                float(item.get("subtotal_venta", 0) or 0),

                float(item.get("descuento_porcentaje", 0) or 0),
                float(item.get("precio_venta_con_descuento", 0) or 0),
                float(item.get("subtotal_venta_con_descuento", 0) or 0),

                float(item.get("descuento_total", 0) or 0),
                float(item.get("margen_final", 0) or 0),
            ))

        return {"cotizacion_id": cotizacion_id, "numero_cotizacion": numero}



def obtener_cotizacion_completa(cotizacion_id: int):
    conn = get_connection()

    # =========================
    # Cabecera
    # =========================
    cab = conn.execute("""
        SELECT
            c.id,
            c.numero_cotizacion,
            c.fecha_creacion,
            c.estado,
            c.subtotal,
            c.igv,
            c.total,
            c.notas,
            c.cliente_id,

            cl.razon_social AS cliente_razon_social,
            cl.tipo_documento AS cliente_tipo_documento,
            cl.numero_documento AS cliente_numero_documento,
            cl.direccion_fiscal AS cliente_direccion_fiscal
        FROM cotizaciones c
        JOIN clientes cl ON cl.id = c.cliente_id
        WHERE c.id = ?
    """, (cotizacion_id,)).fetchone()

    if not cab:
        conn.close()
        return None

    # =========================
    # Detectar tabla real de detalle
    # =========================
    tablas = conn.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table'
          AND name IN ('cotizacion_detalle', 'cotizaciones_items')
    """).fetchall()

    nombres_tablas = {row["name"] for row in tablas}

    detalle_query = None

    if "cotizacion_detalle" in nombres_tablas:
        detalle_query = """
            SELECT
                d.id,
                d.cotizacion_id,
                d.producto_id,
                d.cantidad,

                d.costo_unitario,
                d.subtotal_costo,
                d.margen_porcentaje,
                d.precio_venta_unitario,
                d.subtotal_venta,
                d.descuento_porcentaje,
                d.precio_venta_con_descuento,
                d.subtotal_venta_con_descuento,
                d.descuento_total,
                d.margen_final,

                p.codigo AS producto_codigo,
                p.descripcion AS producto_descripcion,
                p.marca AS producto_marca,
                p.unidad AS producto_unidad
            FROM cotizacion_detalle d
            JOIN productos p ON p.id = d.producto_id
            WHERE d.cotizacion_id = ?
            ORDER BY d.id ASC
        """
    elif "cotizaciones_items" in nombres_tablas:
        detalle_query = """
            SELECT
                d.id,
                d.cotizacion_id,
                d.producto_id,
                d.cantidad,

                d.costo_unitario,
                d.subtotal_costo,
                d.margen_porcentaje,
                d.precio_venta_unitario,
                d.subtotal_venta,
                d.descuento_porcentaje,
                d.precio_venta_con_descuento,
                d.subtotal_venta_con_descuento,
                d.descuento_total,
                d.margen_final,

                p.codigo AS producto_codigo,
                p.descripcion AS producto_descripcion,
                p.marca AS producto_marca,
                p.unidad AS producto_unidad
            FROM cotizaciones_items d
            JOIN productos p ON p.id = d.producto_id
            WHERE d.cotizacion_id = ?
            ORDER BY d.id ASC
        """

    det = []
    if detalle_query:
        det = conn.execute(detalle_query, (cotizacion_id,)).fetchall()

    conn.close()

    return {
        "id": cab["id"],
        "numero_cotizacion": cab["numero_cotizacion"],
        "fecha_creacion": cab["fecha_creacion"],
        "estado": cab["estado"],
        "subtotal": cab["subtotal"],
        "igv": cab["igv"],
        "total": cab["total"],
        "notas": cab["notas"] or "",

        "cliente": {
            "id": cab["cliente_id"],
            "razon_social": cab["cliente_razon_social"],
            "tipo_documento": cab["cliente_tipo_documento"],
            "numero_documento": cab["cliente_numero_documento"],
            "direccion_fiscal": cab["cliente_direccion_fiscal"],
        },

        "items": [
            {
                "producto_id": r["producto_id"],
                "codigo": r["producto_codigo"],
                "descripcion": r["producto_descripcion"],
                "marca": r["producto_marca"],
                "unidad": r["producto_unidad"],

                "cantidad": r["cantidad"],
                "costo_unitario": r["costo_unitario"],
                "subtotal_costo": r["subtotal_costo"],
                "margen_porcentaje": r["margen_porcentaje"],
                "precio_venta_unitario": r["precio_venta_unitario"],
                "subtotal_venta": r["subtotal_venta"],
                "descuento_porcentaje": r["descuento_porcentaje"],
                "precio_venta_con_descuento": r["precio_venta_con_descuento"],
                "subtotal_venta_con_descuento": r["subtotal_venta_con_descuento"],
                "descuento_total": r["descuento_total"],
                "margen_final": r["margen_final"],
            }
            for r in det
        ]
    }



# =========================
# Seeds
# =========================
def crear_usuario(usuario: str, password: str, rol: str, nombre_completo: str, email: str = ""):
    if rol not in ("administrador", "usuario"):
        raise ValueError("rol inválido")

    pwd_hash = generate_password_hash(password)
    with db_tx() as conn:
        conn.execute("""
            INSERT INTO usuarios (usuario, password, rol, nombre_completo, email)
            VALUES (?, ?, ?, ?, ?)
        """, (usuario, pwd_hash, rol, nombre_completo, email))