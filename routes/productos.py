# from flask import Blueprint, request, jsonify
# from database import buscar_productos, obtener_producto_completo_por_id

# productos_bp = Blueprint("productos", __name__)

# @productos_bp.route("/api/productos/buscar")
# def api_buscar_productos():
#     q = request.args.get("q", "")
#     return jsonify({
#         "success": True,
#         "data": buscar_productos(q)
#     })

# @productos_bp.route("/api/productos/<int:producto_id>")
# def api_producto_por_id(producto_id):
#     data = obtener_producto_completo_por_id(producto_id)

#     if not data:
#         return jsonify({"success": False, "error": "Producto no encontrado"}), 404

#     return jsonify({
#         "success": True,
#         "data": data
#     })
