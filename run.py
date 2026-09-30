"""
run.py — application entry point.

Run with:
    python run.py
"""
from app import create_app

app = create_app()

if __name__ == "__main__":
    # debug=True enables auto-reload and detailed error pages during development
    app.run(debug=True, host="127.0.0.1", port=5000)
