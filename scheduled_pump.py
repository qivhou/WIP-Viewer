from django.core.management import setup_environ
import settings
setup_environ(settings)
from wip.schedule import newtask_run

if __name__ == '__main__':
    print "called to start"
    newtask_run()
    print "execute completed"