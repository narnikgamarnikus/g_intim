from io import BytesIO
from openpyxl import load_workbook

from .base import PortationBase
from oscar.apps.catalogue.models import Product
from oscar.apps.catalogue.models import Category
from oscar.apps.catalogue.models import ProductCategory
from oscar.apps.catalogue.models import ProductAttributeValue
from oscar.apps.catalogue.models import AttributeOption
from oscar.apps.catalogue.models import ProductClass


class CatalogueImporter(PortationBase):

    def __init__(self, file):
        self.wb = load_workbook(BytesIO(file.read()))

    def handle(self):
        self.statistics = {
            'created': 0,
            'updated': 0,
            'errors': [],
        }
        self._import()
        return self.statistics

    def _import(self):
        ws = self.wb.active
        self.max_row = ws.max_row
        for row in ws:
            if row[0].row != 1:
                try:
                    self.create_update_product(row)
                except:
                    self.statistics['errors'].append(str(row[0].row))

    def create_update_product(self, data):
        field_values = data[0:len(self.FIELDS)]
        values = [item.value for item in field_values]
        values = dict(zip(self.FIELDS, values))
        product = None

        product = self._get__or_create_product(values[self.ID], values[self.UPC])
        p_class = self._get__or_create_product_class(values[self.PRODUCT_CLASS])
        
        product = self._product_save(product, p_class, values[self.TITLE], 
                                values[self.DESCRIPTION], values[self.UPC])

        ProductCategory.objects.filter(product=product).delete()
        self.save_product_attributes(product, data)

        for category in self._get_or_create_categories(values[self.CATEGORY]):
            product_category = self._product_category_save(product, category)

        return product

    def save_product_attributes(self, product, data):
        
        self.attributes_to_import = product.product_class.attributes.all()
        attrs_values = data[len(self.FIELDS):]
        i = 0
        for attr in self.attributes_to_import:
            try:
                value_obj = product.attribute_values.get(attribute=attr)
            except ProductAttributeValue.DoesNotExist:
                value_obj = ProductAttributeValue()
                value_obj.attribute = attr
                value_obj.product = product
            try:
                value_obj._set_value(attrs_values[i].value)
            except AttributeOption.DoesNotExist:
                attr_option = AttributeOption.objects.create(
                    group=value_obj.attribute.option_group,
                    option=attrs_values[i].value
                )
                value_obj._set_value(attr_option)
            i += 1
            value_obj.save()

    def _get_or_create_categories(self, categories_list):

        categories_list = categories_list.split(', ')

        if isinstance(categories_list, type(None)):
            categories_list = []
        else:
            categories = Category.objects.filter(
            name__in=categories_list)

        if not categories:
            categories = [
                Category.add_root(name=category.strip())
                for category
                in categories_list
            ]

        return categories

    def _get__or_create_product(self, id, upc):
        
        product = Product()
        
        try:
            product = Product.objects.get(id = id)
            self.statistics['updated'] += 1
        except Product.DoesNotExist:
            pass

        if not product is None:
            try:
                product = Product.objects.get(upc = upc)
                self.statistics['updated'] += 1
            except Product.DoesNotExist:
                pass

        return product

    def _get__or_create_product_class(self, name):
        
        product_class, created = ProductClass.objects.get_or_create(name=name)

        if created:
            self.statistics['created'] += 1
        else:
            self.statistics['updated'] += 1

        return product_class

    def _product_save(self, product, product_class, title, description, product_upc):
        
        product.product_class = product_class
        product.title = title
        product.description = description
        product.upc = product_upc

        product.save()

        return product

    def _product_category_save(self, product, category):

        product_category = ProductCategory()
        
        product_category.product = product
        product_category.category = category
        
        product_category.save()

        return product_category