from django.conf.urls import url
from oscar.core.loading import get_class
from .views import ProductClassView

BaseCatalogueApplication = get_class('catalogue.app', 'BaseCatalogueApplication')
ReviewsApplication = get_class('catalogue.app', 'ReviewsApplication')

class CustomCatalogueApplication(BaseCatalogueApplication):
	product_class_view = ProductClassView

	def get_urls(self):
		urlpatterns = super(CustomCatalogueApplication, self).get_urls()
		urlpatterns += [
            #url(r'^product_class(?P<product_class_slug>[\w-]+(/[\w-]+)*)_(?P<pk>\d+)/$',
            #	self.product_class_view.as_view(), name='product_class'),
			]
		return self.post_process_urls(urlpatterns)

class CatalogueApplication(CustomCatalogueApplication, ReviewsApplication):
    """
    Composite class combining Products with Reviews
    """


application = CatalogueApplication()