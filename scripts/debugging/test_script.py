from app import app
import api.auth

print("AUTH ROUTER:")
for route in api.auth.router.routes:
    print(
        type(route).__name__,
        getattr(route, "path", None),
        getattr(route, "methods", None)
    )

print("\nAPP ROUTES BEFORE:")
for route in app.routes:
    if hasattr(route, "path"):
        print(
            route.path,
            getattr(route, "methods", None)
        )

app.include_router(
    api.auth.router,
    prefix="/api/v1/auth"
)

print("\nAPP ROUTES AFTER:")
for route in app.routes:
    if hasattr(route, "path"):
        print(route.path)

print("\nAPP IDENTITIES:")
print(id(app))
print(id(api.auth.router))

