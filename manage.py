#!/usr/bin/env python
import os
import sys

if __name__ == '__main__':
    debug_status = os.getenv('DEBUG', 'False') == 'True'
    #debugging only happens locally, so if debug is true, then use settings, otherwise use prod settings
    if debug_status:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bmt_gpt.settings')
    else:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bmt_gpt.settings_production')

    if (debug_status):
        import debugpy
        try:
            debugpy.listen(("web", 3000))
            print('Debugger Attached!')
        except:
            'Debugger not attached'
        # debugpy.wait_for_client()
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)