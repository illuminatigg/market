from django_filters import rest_framework as filters

from .models import Product


class CharFilterInFilter(filters.BaseInFilter, filters.CharFilter):
    pass


class ProductFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='iexact')
    quantity__gt = filters.NumberFilter(field_name='quantity', lookup_expr='gt')
    quantity__lt = filters.NumberFilter(field_name='quantity', lookup_expr='lt')
    manufacturer__name__in = CharFilterInFilter(field_name='manufacturer__name', lookup_expr='in')
    category__name__in = CharFilterInFilter(field_name='category', lookup_expr='icontains')
    store_house__name__in = CharFilterInFilter(field_name='store_house', lookup_expr='icontains')
    available = filters.BooleanFilter(field_name='available')

    class Meta:
        model = Product
        fields = ['name', 'quantity', 'manufacturer', 'category', 'store_house', 'available']