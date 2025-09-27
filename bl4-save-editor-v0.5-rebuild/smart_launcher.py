import sys, importlib, subprocess
try:
    import PySide6, yaml
except Exception:
    try:
        from bl4_editor.core import logger
        logger.error('Missing dependencies. Run pip install -r requirements.txt')
    except Exception:
        print('Missing dependencies. Run pip install -r requirements.txt')
    sys.exit(1)
subprocess.call([sys.executable, '-m', 'bl4_editor.main'])
