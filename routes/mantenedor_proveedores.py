from flask import Blueprint, render_template, request, redirect
from database import db_query, db_execute, obtener_productos
import pandas as pd
from flask import request, redirect, flash
from database import db_query, db_execute

mantenedor_proveedores_bp = Blueprint("mantenedor_proveedores", __name__)

@mantenedor_proveedores_bp.route("/mantenedor/proveedores/gestion")
def gestionar_proveedor():
    return render_template("mantenedor/gestion_proveedores.html")

@mantenedor_proveedores_bp.route("/mantenedor/proveedores/nuevo")
def insertar_proveedor():
    return render_template("mantenedor/nuevo_proveedor.html")