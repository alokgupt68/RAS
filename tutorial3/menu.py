"""
This file was generated with the custommenu management command, it contains
the classes for the admin menu, you can customize this class as you want.

To activate your custom menu add the following to your settings.py::
    ADMIN_TOOLS_MENU = 'tutorial3.menu.CustomMenu'
"""

try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from admin_tools.menu import items, Menu


class CustomMenu(Menu):
    """
    Custom Menu for tutorial3 admin site.
    """
    def __init__(self, **kwargs):
        Menu.__init__(self, **kwargs)
        self.children += [
            items.MenuItem(_('Home'), reverse('admin:index')),
            
            items.AppList(
                _('Masters'),
                exclude=('django.contrib.*',)
            ),
            items.AppList(
                _('Administration'),
                models=('django.contrib.*',)
            ),
            items.MenuItem('Attendance Entry',
                children=[
                    items.MenuItem('Single Timesheet', 'http://127.0.0.1:8000/accounts/login/gensal/timesheet/'),
                    items.MenuItem('Timesheet Grid', 'http://127.0.0.1:8000/accounts/login/gensal/multimesheet/'),
                    items.MenuItem('Upload Timesheet', 'http://127.0.0.1:8000/accounts/login/gensal/upload/'),
                ]
                ),
                        items.MenuItem('Salary Generation',
                children=[
                    items.MenuItem('Single Resource Salary', 'http://127.0.0.1:8000/accounts/login/gensal/gensal/'),
                    #items.MenuItem('Salary Grid', 'http://127.0.0.1:8000/accounts/login/gensal/multimesheet/'),
                ]
                ),
        ]

    def init_with_context(self, context):
        """
        Use this method if you need to access the request context.
        """
        return super(CustomMenu, self).init_with_context(context)
