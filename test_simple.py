from app import app
def test_routes():
    routes = [r.path for r in app.routes if hasattr(r, "path")]
    assert "/api/v1/auth/register" in routes
