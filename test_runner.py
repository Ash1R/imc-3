from datamodel import OrderDepth, Trade, TradingState, Listing, Observation
from submission import Trader

# Setup fake order book for testing
depth = OrderDepth()
depth.buy_orders = {950: 10, 940: 5}
depth.sell_orders = {960: -8, 970: -4}

# Let's simulate multiple vouchers and the rock
order_depths = {
    "VOLCANIC_ROCK": OrderDepth()
}
order_depths["VOLCANIC_ROCK"].buy_orders = {9950: 20}
order_depths["VOLCANIC_ROCK"].sell_orders = {10050: -20}

for strike in [9500, 9750, 10000, 10250, 10500]:
    symbol = f"VOLCANIC_ROCK_VOUCHER_{strike}"
    order_depths[symbol] = OrderDepth()
    order_depths[symbol].buy_orders = {strike - 20: 10}
    order_depths[symbol].sell_orders = {strike + 20: -10}

# Simulate position
positions = {product: 0 for product in order_depths}

# Empty values for unused fields
listings = {product: Listing(product, product, "SEASHELLS") for product in order_depths}
own_trades = {product: [] for product in order_depths}
market_trades = {product: [] for product in order_depths}
observations = Observation({}, {})

state = TradingState(
    traderData="",
    timestamp=0,
    listings=listings,
    order_depths=order_depths,
    own_trades=own_trades,
    market_trades=market_trades,
    position=positions,
    observations=observations
)

# Run your Trader
trader = Trader()
orders, conversions, traderData = trader.run(state)

print("ORDERS:")
for product, product_orders in orders.items():
    for o in product_orders:
        print(f"{product}: {o}")

print("\nCONVERSIONS:", conversions)
print("\nTRADER DATA:", traderData)
