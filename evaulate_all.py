import pandas as pd
from datamodel import OrderDepth, Trade, TradingState, Listing, Observation
from submission import Trader

def build_order_book(row):
    depth = OrderDepth()
    for i in range(1, 4):
        bid_price = row.get(f"bid_price_{i}")
        bid_volume = row.get(f"bid_volume_{i}")
        ask_price = row.get(f"ask_price_{i}")
        ask_volume = row.get(f"ask_volume_{i}")
        if pd.notna(bid_price) and pd.notna(bid_volume):
            depth.buy_orders[int(bid_price)] = int(bid_volume)
        if pd.notna(ask_price) and pd.notna(ask_volume):
            depth.sell_orders[int(ask_price)] = -int(ask_volume)
    return depth

# Load all days of price data
days = [0, 1, 2]
all_prices = {day: pd.read_csv(f"prices_round_3_day_{day}.csv", delimiter=";") for day in days}

# Initialize everything
pnl_by_product = {}
positions = {}
trader = Trader()
traderData = ""

# Evaluate across all days and timestamps
for day, df in all_prices.items():
    df = df.sort_values(by="timestamp")
    for timestamp in df["timestamp"].unique():
        snapshot = df[df["timestamp"] == timestamp]
        order_depths = {}
        listings = {}
        own_trades = {}
        market_trades = {}

        for _, row in snapshot.iterrows():
            product = row["product"]
            depth = build_order_book(row)
            if depth is None:
                continue
            order_depths[product] = depth
            listings[product] = Listing(product, product, "SEASHELLS")
            own_trades[product] = []
            market_trades[product] = []

        for p in order_depths:
            if p not in positions:
                positions[p] = 0

        state = TradingState(
            traderData=traderData,
            timestamp=timestamp,
            listings=listings,
            order_depths=order_depths,
            own_trades=own_trades,
            market_trades=market_trades,
            position=positions.copy(),
            observations=Observation({}, {})
        )

        orders, conversions, traderData = trader.run(state)

        for product, olist in orders.items():
            if product not in pnl_by_product:
                pnl_by_product[product] = 0
            for order in olist:
                if order.quantity > 0:
                    pnl_by_product[product] -= order.price * order.quantity
                    positions[product] += order.quantity
                else:
                    pnl_by_product[product] += order.price * (-order.quantity)
                    positions[product] += order.quantity

# Print final PnL
print("\n=== Final PnL Summary ===")
for product in sorted(pnl_by_product):
    print(f"{product:<35} PnL: {pnl_by_product[product]:>10.2f} | Final Pos: {positions.get(product, 0)}")
