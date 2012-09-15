import win32serviceutil
import win32service
import win32event
import django
from django.core.servers.basehttp import run, AdminMediaHandler, WSGIServerException
from django.core.handlers.wsgi import WSGIHandler
from django.core.servers.basehttp import WSGIServer, WSGIRequestHandler

import sys
import os

class DjangoService(win32serviceutil.ServiceFramework):
    _svc_name_ = "DjangoService"
    _svc_display_name_ = "Django Application Server Service"
    stop_requested = False
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        # Create an event which we will use to wait on.
        # The "service stop" request will set this event.
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

    def SvcStop(self):
        # Before we do anything, tell the SCM we are starting the stop process.
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        # And set my event.
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        import settings
        import imp
        from django.core.management import setup_environ
        from django.core.management import execute_manager
        imp.find_module('settings') 
        setup_environ(settings)
        #execute_manager(settings,argv=['manage.py','runserver','127.0.0.1:80'])
        os.environ['DJANGO_SETTINGS_MODULE'] = 'django_settings_module'
        self.runserver('127.0.0.1:80')
        win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)

    def runserver(self, addrport='', *args, **options):
        if args:
            raise CommandError('Usage is runservice %s' % self.args)
        if not addrport:
            addr = ''
            port = '8000'
        else:
            try:
                addr, port = addrport.split(':')
            except ValueError:
                addr, port = '', addrport
        if not addr:
            addr = '127.0.0.1'

        if not port.isdigit():
            raise CommandError("%r is not a valid port number." % port)

        admin_media_path = options.get('admin_media_path', '')
        shutdown_message = options.get('shutdown_message', '')
        quit_command = (sys.platform == 'win32') and 'CTRL-BREAK' or 'CONTROL-C'

        from django.conf import settings
        from django.utils import translation
        print "\nDjango version %s, using settings %r" % (django.get_version(), settings.SETTINGS_MODULE)
        print "Server is running at http://%s:%s/" % (addr, port)
        print "Quit the server with %s." % quit_command
        print "Should be run as a service, default is noreload (and it has made to be stopped)."

        # django.core.management.base forces the locale to en-us. We should
        # set it up correctly for the first request (particularly important
        # in the "--noreload" case).
        translation.activate(settings.LANGUAGE_CODE)

        try:
            path = admin_media_path or django.__path__[0] + '/contrib/admin/media'
            handler = AdminMediaHandler(WSGIHandler(), path)
            self._run_wsgi(addr, int(port), handler)
        except WSGIServerException, e:
            # Use helpful error messages instead of ugly tracebacks.
            ERRORS = {
                13: "You don't have permission to access that port.",
                98: "That port is already in use.",
                99: "That IP address can't be assigned-to.",
            }
            try:
                error_text = ERRORS[e.args[0].args[0]]
            except (AttributeError, KeyError):
                error_text = str(e)
            sys.stderr.write(self.style.ERROR("Error: %s" % error_text) + '\n')
            # Need to use an OS exit because sys.exit doesn't work in a thread
            os._exit(1)
        except KeyboardInterrupt:
            if shutdown_message:
                print shutdown_message
            sys.exit(0)
    
    def _run_wsgi(self, addr, port, wsgi_handler):
        server_address = (addr, port)
        httpd = WSGIServer(server_address, WSGIRequestHandler)
        httpd.set_app(wsgi_handler)
        #httpd.serve_forever()
        while not self.stop_requested:
            httpd.handle_request()        
        
if __name__=='__main__':
    win32serviceutil.HandleCommandLine(DjangoService)