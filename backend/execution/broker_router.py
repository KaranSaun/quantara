"""
APEX OS — Broker Router
Unified broker interface. Swap brokers via config.
"""

import logging
from dataclasses import dataclass
from typing import Optional
from config import ACTIVE_BROKERS, BROKER_CONFIGS

logger = logging.getLogger("apex.broker_router")


@dataclass
class Position:
    symbol: str
    quantity: int
    avg_price: float
    ltp: float
    pnl: float
    product_type: str


@dataclass
class Order:
    symbol: str
    qty: int
    price: float
    order_type: str  # "LIMIT" | "MARKET"
    side: str        # "BUY" | "SELL"
    product: str     # "INTRADAY" | "CARRYFORWARD"


@dataclass
class OrderResponse:
    order_id: str
    status: str
    message: str


@dataclass
class Margins:
    available: float
    used: float
    total: float


@dataclass
class Portfolio:
    positions: list[Position]
    total_pnl: float
    margins: Margins


class BrokerRouter:
    def __init__(self):
        self.brokers = {}
        for name in ACTIVE_BROKERS:
            name = name.strip()
            if name == "angel_one":
                from execution.angel_one import AngelOneBroker
                self.brokers[name] = AngelOneBroker()
            # Add more brokers here as implemented
        logger.info(f"Broker router initialized with: {list(self.brokers.keys())}")

    def _get_broker(self, name: str | None = None):
        if name:
            return self.brokers.get(name)
        # Return first active broker
        if self.brokers:
            return next(iter(self.brokers.values()))
        raise RuntimeError("No brokers configured")

    async def get_positions(self, broker: str | None = None) -> list[Position]:
        b = self._get_broker(broker)
        return await b.get_positions()

    async def get_pnl_today(self, broker: str | None = None) -> float:
        b = self._get_broker(broker)
        return await b.get_pnl_today()

    async def get_portfolio(self, broker: str | None = None) -> Portfolio:
        b = self._get_broker(broker)
        return await b.get_portfolio()

    async def get_margins(self, broker: str | None = None) -> Margins:
        b = self._get_broker(broker)
        return await b.get_margins()

    async def place_order(self, order: Order, broker: str | None = None) -> OrderResponse:
        """ALWAYS requires explicit user confirmation before calling this."""
        logger.warning(f"ORDER REQUEST: {order.side} {order.qty}x {order.symbol} @ {order.price}")
        b = self._get_broker(broker)
        return await b.place_order(order)
