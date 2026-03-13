# seed_loader.py
# Script de carga de datos semilla (casos prueba) a demanda.
# Idempotente: si ya existe un registro único (usuario/ruc/código), lo omite en vez de fallar.
#
# Uso:
#   python seed_loader.py seed_data.json
# Opcional (reset total):
#   python seed_loader.py seed_data.json --reset

import json
import os
import sys

from database import (
    init_db,
    crear_usuario,
    insertar_cliente,
    insertar_contacto_cliente,
    insertar_punto_entrega,
    insertar_producto,
    insertar_proveedor,
    DB_PATH
)

import sqlite3


def reset_db_file():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"🧹 Base de datos eliminada: {DB_PATH}")
    else:
        print("ℹ️ No existe base de datos para eliminar.")


def safe_run(label, fn, *args, **kwargs):
    """Ejecuta una inserción y si choca con UNIQUE, lo omite sin romper el seed."""
    try:
        return fn(*args, **kwargs)
    except sqlite3.IntegrityError as e:
        msg = str(e).lower()
        if "unique constraint failed" in msg:
            print(f"⚠️ Omitido (ya existe): {label}")
            return None
        raise


def load_seed(path: str, reset: bool = False):
    if reset:
        reset_db_file()

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    init_db()

    # Usuarios (UNIQUE: usuario)
    for u in data.get("usuarios", []):
        safe_run(
            f"usuario={u.get('usuario')}",
            crear_usuario,
            usuario=u["usuario"],
            password=u["password"],
            rol=u["rol"],
            nombre_completo=u["nombre_completo"],
            email=u.get("email", "")
        )

    # Proveedores (UNIQUE: ruc)
    for p in data.get("proveedores", []):
        safe_run(
            f"proveedor ruc={p.get('ruc')}",
            insertar_proveedor,
            razon_social=p["razon_social"],
            ruc=p["ruc"],
            direccion=p["direccion"],
            telefono=p.get("telefono", ""),
            contacto=p.get("contacto", ""),
            email=p.get("email", "")
        )

    # Productos (UNIQUE: codigo) -> OJO: insertar_producto genera código automático.
    # Para evitar duplicar por descripción, en seed lo omitimos si choca.
    for pr in data.get("productos", []):
        safe_run(
            f"producto desc={pr.get('descripcion')}",
            insertar_producto,
            familia=pr["familia"],
            descripcion=pr["descripcion"],
            descripcion_larga=pr.get("descripcion_larga", ""),
            marca=pr.get("marca", ""),
            modelo=pr.get("modelo", ""),
            unidad=pr.get("unidad", "Unidad")
        )

    # Clientes (UNIQUE: numero_documento)
    for c in data.get("clientes", []):
        cliente_id = safe_run(
            f"cliente doc={c.get('numero_documento')}",
            insertar_cliente,
            tipo_documento=c["tipo_documento"],
            numero_documento=c["numero_documento"],
            razon_social=c["razon_social"],
            direccion_fiscal=c["direccion_fiscal"]
        )

        # Si el cliente ya existía, no insertamos contactos/puntos (evita duplicación).
        if not cliente_id:
            continue

        for cc in c.get("contactos", []):
            safe_run(
                f"contacto cliente_id={cliente_id} nombre={cc.get('nombre_contacto')}",
                insertar_contacto_cliente,
                cliente_id=cliente_id,
                nombre_contacto=cc["nombre_contacto"],
                email=cc.get("email", ""),
                telefono=cc.get("telefono", ""),
                cargo=cc.get("cargo", ""),
                principal=cc.get("principal", False)
            )

        for pe in c.get("puntos_entrega", []):
            safe_run(
                f"punto_entrega cliente_id={cliente_id} nombre={pe.get('nombre_punto')}",
                insertar_punto_entrega,
                cliente_id=cliente_id,
                nombre_punto=pe["nombre_punto"],
                direccion=pe["direccion"],
                departamento=pe.get("departamento", ""),
                provincia=pe.get("provincia", ""),
                distrito=pe.get("distrito", ""),
                telefono_contacto=pe.get("telefono_contacto", ""),
                responsable=pe.get("responsable", ""),
                principal=pe.get("principal", False)
            )

    print("✅ Seed finalizado correctamente.")


def main():
    if len(sys.argv) < 2:
        print("Uso: python seed_loader.py seed_data.json [--reset]")
        sys.exit(1)

    seed_path = sys.argv[1]
    reset = "--reset" in sys.argv[2:]
    load_seed(seed_path, reset=reset)


if __name__ == "__main__":
    main()