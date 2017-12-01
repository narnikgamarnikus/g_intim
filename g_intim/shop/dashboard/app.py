from django.conf.urls import url
from oscar.apps.dashboard.app import (
    DashboardApplication as CoreDashboardApplication)

from portation.app import application


class DashboardApplication(CoreDashboardApplication):
    portation_app = application

    def get_urls(self):
        processed_urls = super(DashboardApplication, self).get_urls()
        urls = [
            url(r'^portation/', self.portation_app.urls),
        ]
        return processed_urls + self.post_process_urls(urls)


application = DashboardApplication()