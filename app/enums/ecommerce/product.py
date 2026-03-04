from enum import Enum

class ProductStatus(str, Enum):
    HOT = "hot"
    SALES = "sales"
    NEW = "new"      