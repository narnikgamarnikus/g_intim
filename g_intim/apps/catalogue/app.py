from django.conf.urls import url
from oscar.core.loading import get_class
from .views import FilterView

BaseCatalogueApplication = get_class('catalogue.app', 'BaseCatalogueApplication')
ReviewsApplication = get_class('catalogue.app', 'ReviewsApplication')

class CustomCatalogueApplication(BaseCatalogueApplication):
	filter_view = FilterView

	def get_urls(self):
		#urlpatterns = []
		#urlpatterns = super(CustomCatalogueApplication, self).get_urls()
		urlpatterns = [
			url(r'^category/(?P<category_slug>[\w-]+(/[\w-]+)*)_(?P<pk>[\w-]+)/((?P<filter_code>[\w]+)(-(?P<filter_name>[\w/-]+)))*/$',
				self.filter_view.as_view(), name='filter'),
		] + super(CustomCatalogueApplication, self).get_urls()
		return self.post_process_urls(urlpatterns)

class CatalogueApplication(CustomCatalogueApplication, ReviewsApplication):
    """
    Composite class combining Products with Reviews
    """


application = CatalogueApplication()
