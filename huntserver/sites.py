from django.contrib.admin.sites import AdminSite
from django.urls import re_path, reverse
from django.utils.text import capfirst

class StaffPagesAdmin(AdminSite):
    """A Django AdminSite with the ability to register custom staff pages not connected to models."""
    # Pattern taken from django adminplus from jsocol

    def __init__(self, *args, **kwargs):
        self.custom_views = []
        return super(StaffPagesAdmin, self).__init__(*args, **kwargs)

    def register_view(self, path, name=None, urlname=None, visible=True, view=None):
        self.custom_views.append((path, view, name, urlname, visible))

    def get_urls(self):
        urls = super(StaffPagesAdmin, self).get_urls()
        for path, view, name, urlname, visible in self.custom_views:
            urls.insert(0, re_path(r"^%s$" % path, self.admin_view(view), name=urlname))
        return urls

    def get_app_list(self, request, app_label=None):
        app_list = super(StaffPagesAdmin, self).get_app_list(request)
        app_list.insert(0, {
            "name": "Staff Pages",
            "app_label": "staff-pages",
            "app_url": "/staff/",
            "has_module_perms": True,
            "models": [
                {
                    "model": None,
                    "name": name if name else capfirst(view.__name__),
                    "object_name": view.__name__,
                    "perms": {},
                    "admin_url": reverse("admin:%s" % urlname, current_app=self.name),
                    "add_url": None,
                    "view_only": True
                } for path, view, name, urlname, visible in self.custom_views if visible
            ]
        })
        return app_list


huntserver_admin = StaffPagesAdmin()