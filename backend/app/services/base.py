from abc import ABC, abstractmethod

from backend.app.models.product import Option, Order, Part, PriceRule, Product
from backend.app.schemas.order import OrderResponse


class BaseOrderService(ABC):
    @abstractmethod
    def create_order(self, product: Product) -> OrderResponse:
        pass

    @abstractmethod
    def update_order(self, order: Order, option: Option) -> OrderResponse:
        pass


class BasePriceService(ABC):
    @abstractmethod
    def calculate_price(self, order: Order, rules: list[PriceRule]) -> float:
        pass


class BaseSelectionService(ABC):
    @abstractmethod
    def load_compatibilities(
        self,
        parts: list[Part],
        options: list[Option],
        grouped_compatibilities: dict[int, dict[str, list[int]]],
    ):
        pass

    @abstractmethod
    def get_available_options(self, parts: list[Part]) -> dict[int, list[int]]:
        pass

    @abstractmethod
    def is_selection_valid(self):
        pass

    @abstractmethod
    def select_part_options(self, options: list[Option]):
        pass
