import pandas as pd
from datamodel import OrderDepth, Trade, TradingState, Listing, Observation
from submission import Trader

# === Load CSV ===
prices = pd.read_csv("prices_round_3_day_0.csv", delimiter=";")

# === Simulate OrderDepth ===
def build_order_book(prices_df, product):
    # Filter for latest timestamp
    product_df = prices_df[prices_df["product"] == product]
    if product_df.empty:
        return None
    
    latest_row = product_df.iloc[-1]

    depth = OrderDepth()
    for i in range(1, 4):
        bid_price = latest_row.get(f"bid_price_{i}")
        bid_volume = latest_row.get(f"bid_volume_{i}")
        ask_price = latest_row.get(f"ask_price_{i}")
        ask_volume = latest_row.get(f"ask_volume_{i}")
        if pd.notna(bid_price) and pd.notna(bid_volume):
            depth.buy_orders[int(bid_price)] = int(bid_volume)
        if pd.notna(ask_price) and pd.notna(ask_volume):
            depth.sell_orders[int(ask_price)] = -int(ask_volume)
    return depth

# === Create order_depths ===
products = prices["product"].unique()
order_depths = {}
for product in products:
    depth = build_order_book(prices, product)
    if depth:
        order_depths[product] = depth

# === Create mock TradingState ===
listings = {p: Listing(p, p, "SEASHELLS") for p in order_depths}
own_trades = {p: [] for p in order_depths}
market_trades = {p: [] for p in order_depths}
positions = {p: 0 for p in order_depths}
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

# === Run Trader ===
trader = Trader()
orders, conversions, traderData = trader.run(state)

# === Output Results ===
print("ORDERS:")
for product, olist in orders.items():
    for order in olist:
        print(order)

print("\nCONVERSIONS:", conversions)
print("\nTRADER DATA:", traderData)
