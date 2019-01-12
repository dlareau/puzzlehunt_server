#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "puzzlehunt_server.settings.local_settings")

    from django.core.management import execute_from_command_line

    is_testing = 'test' in sys.argv

    if is_testing:
        import coverage
        cov = coverage.coverage(source=['huntserver'], omit=['*/tests/*', '*/migrations/*'])
        # cov.set_option('report:show_missing', True)
        cov.erase()
        cov.start()

    execute_from_command_line(sys.argv)

    if is_testing:
        cov.stop()
        cov.save()
        cov.html_report(directory='cover')
        cov.report()