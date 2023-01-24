from configuration.settings import DEBUG

URL = 'http://127.0.0.1:8000' if DEBUG else 'http://31.184.218.182:8001'

REGISTRATION_ENDPOINT = '/api/accounts/client-registration/'
MANUFACTURERS_ENDPOINT = '/api/market/manufacturers-all/'
PRODUCTS_ENDPOINT = '/api/market/products-all/'
CREATE_CART = '/api/market/create-cart/'
UPDATE_CART = '/api/market/create-cart/'
PRODUCT_BY_MANUFACTURER_ENDPOINT = '/api/market/products-by-manufacturer/'
CATEGORIES_ENDPOINT = '/api/market/product-categories/'
CLIENT_AUTH_ENDPOINT = '/api/accounts/client-auth/'
MODIFICATION_BY_PRODUCT = '/api/market/modification-by-product/'