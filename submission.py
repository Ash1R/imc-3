from datamodel import Order, OrderDepth, TradingState
from typing import Dict, List, Tuple
import jsonpickle

# Position limits and strike prices
POSITION_LIMITS = {
    "VOLCANIC_ROCK": 400,
    "VOLCANIC_ROCK_VOUCHER_9500": 200,
    "VOLCANIC_ROCK_VOUCHER_9750": 200,
    "VOLCANIC_ROCK_VOUCHER_10000": 200,
    "VOLCANIC_ROCK_VOUCHER_10250": 200,
    "VOLCANIC_ROCK_VOUCHER_10500": 200,
}
STRIKE_PRICES = {
    "VOLCANIC_ROCK_VOUCHER_9500": 9500,
    "VOLCANIC_ROCK_VOUCHER_9750": 9750,
    "VOLCANIC_ROCK_VOUCHER_10000": 10000,
    "VOLCANIC_ROCK_VOUCHER_10250": 10250,
    "VOLCANIC_ROCK_VOUCHER_10500": 10500,
}

class Trader:
    def run(self, state: TradingState) -> Tuple[Dict[str, List[Order]], int, str]:
        orders = {}
        conversions = 0
        new_positions = state.position.copy()

        # Restore memory
        try:
            last_data = jsonpickle.decode(state.traderData)
        except:
            last_data = {"last_rock_price": 10000}

        rock_price_guess = last_data.get("last_rock_price", 10000)

        for product in state.order_depths:
            depth = state.order_depths[product]
            position = state.position.get(product, 0)
            limit = POSITION_LIMITS.get(product, 100)
            product_orders = []

            if product == "VOLCANIC_ROCK":
                # Estimate fair price as mid-price
                if depth.buy_orders and depth.sell_orders:
                    best_bid = max(depth.buy_orders)
                    best_ask = min(depth.sell_orders)
                    fair_price = (best_bid + best_ask) // 2
                else:
                    fair_price = rock_price_guess

                rock_price_guess = fair_price  # remember for next round

                # Buy below fair
                for ask, volume in sorted(depth.sell_orders.items()):
                    if ask < fair_price and position + abs(volume) <= limit:
                        qty = min(abs(volume), limit - position)
                        product_orders.append(Order(product, ask, qty))
                        position += qty

                # Sell above fair
                for bid, volume in sorted(depth.buy_orders.items(), reverse=True):
                    if bid > fair_price and position - volume >= -limit:
                        qty = min(volume, position + limit)
                        product_orders.append(Order(product, bid, -qty))
                        position -= qty

            elif product.startswith("VOLCANIC_ROCK_VOUCHER_"):
                strike = STRIKE_PRICES[product]
                intrinsic = max(0, rock_price_guess - strike)
                cheap_cutoff = intrinsic * 0.8
                expensive_cutoff = intrinsic * 1.2

                for ask, volume in sorted(depth.sell_orders.items()):
                    if ask < cheap_cutoff and position + abs(volume) <= limit:
                        qty = min(abs(volume), limit - position)
                        product_orders.append(Order(product, ask, qty))
                        position += qty

                for bid, volume in sorted(depth.buy_orders.items(), reverse=True):
                    if bid > expensive_cutoff and position - volume >= -limit:
                        qty = min(volume, position + limit)
                        product_orders.append(Order(product, bid, -qty))
                        position -= qty

            if product_orders:
                orders[product] = product_orders
                new_positions[product] = position

        traderData = jsonpickle.encode({"last_rock_price": rock_price_guess})
        return orders, conversions, traderData
