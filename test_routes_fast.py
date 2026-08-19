import sys
from unittest.mock import MagicMock
sys.modules['transformers'] = MagicMock()
sys.modules['torch'] = MagicMock()
sys.modules['sentence_transformers'] = MagicMock()
sys.modules['huggingface_hub'] = MagicMock()

from app import app
def _get_paths(routes):
    paths = []
    for r in routes:
        if hasattr(r, 'path'):
            paths.append(r.path)
        elif hasattr(r, 'routes'):
            paths.extend(_get_paths(r.routes))
    return paths

routes = _get_paths(app.routes)
print('AUTH IN ROUTES:', '/api/v1/auth/register' in routes)
print('ROUTES:', routes)
