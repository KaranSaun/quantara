"""
APEX OS — Angel One SmartAPI Broker Integration
"""

import logging
from typing import Optional
from config import BROKER_CONFIGS
from execution.broker_router import Position, Order, OrderResponse, Margins, Portfolio

logger = logging.getLogger("apex.angel_one")


class AngelOneBroker:
    def __init__(self):
        self.config = BROKER_CONFIGS.get("angel_one", {})
        self._session = None
        self._auth_token = None

    async def _ensure_session(self):
        if self._session:
            return
        try:
            from SmartApi import SmartConnect
            import pyotp

            client_id = self.config.get("client_id", "")
            password = self.config.get("password", "")
            totp_secret = self.config.get("totp_secret", "")

            if not all([client_id, password, totp_secret]):
                logger.warning("Angel One credentials not fully configured")
                return

            obj = SmartConnect(api_key=client_id)
            totp = pyotp.TOTP(totp_secret).now()
            data = obj.generateSession(client_id, password, totp)

            if data.get("status"):
                self._session = obj
                self._auth_token = data["data"]["jwtToken"]
                logger.info("Angel One session established")
            else:
                logger.error(f"Angel One auth failed: {data}")
        except ImportError:
            logger.warning("SmartApi not installed. Run: pip install smartapi-python")
        except Exception as e:
            logger.error(f"Angel One session error: {e}")

    async def get_positions(self) -> list[Position]:
        await self._ensure_session()
        if not self._session:
            return []
        try:
            data = self._session.position()
            if not data or not data.get("data"):
                return []
            return [
                Position(
                    symbol=p.get("tradingsymbol", ""),
                    quantity=int(p.get("netqty", 0)),
                    avg_price=float(p.get("averageprice", 0)),
                    ltp=float(p.get("ltp", 0)),
                    pnl=float(p.get("pnl", 0)),
                    product_type=p.get("producttype", ""),
                )
                for p in data["data"]
            ]
        except Exception as e:
            logger.error(f"Get positions error: {e}")
            return []

    async def get_pnl_today(self) -> float:
        positions = await self.get_positions()
        return sum(p.pnl for p in positions)

    async def get_margins(self) -> Margins:
        await self._ensure_session()
        if not self._session:
            return Margins(available=0, used=0, total=0)
        try:
            data = self._session.rmsLimit()
            if not data or not data.get("data"):
                return Margins(available=0, used=0, total=0)
            d = data["data"]
            return Margins(
                available=float(d.get("availablecash", 0)),
                used=float(d.get("utiliseddebits", 0)),
                total=float(d.get("net", 0)),
            )
        except Exception as e:
            logger.error(f"Get margins error: {e}")
            return Margins(available=0, used=0, total=0)

    async def get_portfolio(self) -> Portfolio:
        positions = await self.get_positions()
        margins = await self.get_margins()
        total_pnl = sum(p.pnl for p in positions)
        return Portfolio(positions=positions, total_pnl=total_pnl, margins=margins)

    async def place_order(self, order: Order) -> OrderResponse:
        await self._ensure_session()
        if not self._session:
            return OrderResponse(order_id="", status="FAILED", message="No session")
        try:
            params = {
                "variety": "NORMAL",
                "tradingsymbol": order.symbol,
                "symboltoken": "",  # Would need lookup
                "transactiontype": order.side,
                "exchange": "NFO",
                "ordertype": order.order_type,
                "producttype": order.product,
                "duration": "DAY",
                "price": str(order.price),
                "quantity": str(order.qty),
            }
            data = self._session.placeOrder(params)
            return OrderResponse(
                order_id=str(data) if data else "",
                status="PLACED",
                message="Order placed successfully",
            )
        except Exception as e:
            logger.error(f"Place order error: {e}")
            return OrderResponse(order_id="", status="FAILED", message=str(e))
