import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask
from backend.database import init_db, seed_demo_data
from backend.routes import bp
from backend.admin_routes import admin_bp

app = Flask(
    __name__,
    template_folder=os.path.join("frontend", "templates"),
    static_folder=os.path.join("frontend", "static"),
)

app.secret_key = "health-platform-secret-key-2024"
app.config["SESSION_COOKIE_HTTPONLY"] = True

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

@app.template_filter("month_name")
def month_name_filter(month_int):
    try:
        return MONTHS[int(month_int) - 1]
    except (IndexError, ValueError):
        return "—"

app.register_blueprint(bp)
app.register_blueprint(admin_bp)

if __name__ == "__main__":
    init_db()
    seed_demo_data()
    print("\n  Health Consultation Platform")
    print("  Running at: http://127.0.0.1:5000")
    print("  Demo credentials:")
    print("    Admin   -> admin@health.com   / admin123")
    print("    Doctor  -> doctor@health.com  / doctor123")
    print("    Patient -> patient@health.com / patient123\n")
    app.run(debug=True, port=5000)
