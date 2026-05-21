from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import base64

print("🔵 [1] Iniciando app.py...")

app = Flask(__name__)

# ==================== CONFIGURACIÓN SUPABASE ====================
_a = base64.b64decode('cG9zdGdyZXNxbDovLy9wb3N0Z3Jlcy50a2Ztd3ZzZW52Z3B5ZXh2ZGNhdDphZG1pbjM1NjE5NjdrY2ZAYXdzLTEtdXMtZWFzdC0xLnBvb2xlci5zdXBhYmFzZS5jb206NjU0My9wb3N0Z3Jlcw==').decode('utf-8')
app.config['SQLALCHEMY_DATABASE_URI'] = _a
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'sb_secret_k56lhPYVINqZMj_BZexRbw_JzeBx8Hx'

db = SQLAlchemy()
db.init_app(app)

print("🔵 [2] Base de datos configurada")

# ==================== BLUEPRINTS ====================
print("🔵 [3] Importando blueprints...")

try:
    from routes.usuarios import usuarios_bp
    print("✅ [4] usuarios_bp importado")
except Exception as e:
    print(f"❌ [4] Error en usuarios_bp: {e}")

try:
    from routes.cotizaciones import cotizaciones_bp
    print("✅ [5] cotizaciones_bp importado")
except Exception as e:
    print(f"❌ [5] Error en cotizaciones_bp: {e}")

try:
    from routes.mantenedor_productos import productos_bp
    print("✅ [6] productos_bp importado")
except Exception as e:
    print(f"❌ [6] Error en productos_bp: {e}")

try:
    from routes.kardex import kardex_bp
    print("✅ [7] kardex_bp importado")
except Exception as e:
    print(f"❌ [7] ERROR IMPORTANDO KARDEX_BP: {e}")
    import traceback
    traceback.print_exc()

print("🔵 [8] Registrando blueprints...")
app.register_blueprint(usuarios_bp)
app.register_blueprint(cotizaciones_bp)
app.register_blueprint(productos_bp)
app.register_blueprint(kardex_bp)

print(f"🔵 [9] Blueprints registrados: {list(app.blueprints.keys())}")

print("🚀 [10] Servidor Flask iniciado correctamente con Supabase")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("✅ [11] Base de datos inicializada")
    app.run(debug=True, host='0.0.0.0', port=5000)