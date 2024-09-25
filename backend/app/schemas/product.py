from pydantic import BaseModel, ConfigDict


class ProductBase(BaseModel):
    name: str
    description: str


class ProductCreate(ProductBase):
    pass


class Product(ProductBase):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: int
