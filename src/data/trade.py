import duckdb as dd
from pydantic import BaseModel
from typing import Literal
from datetime import date
from src.utils.config import get_conn

class Transaction(BaseModel):
    client_id: int
    account: str
    Date: date
    action: Literal["buy", "sell"]
    tckr: str
    price: float
    quantity: float
    currency: Literal["USD", "CAD"]

def create_trades_table(conn: dd.DuckDBPyConnection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS trades(
            client_id INTEGER NOT NULL,
            account VARCHAR NOT NULL,
            date DATE NOT NULL,
            action VARCHAR NOT NULL CHECK (action IN ('buy', 'sell')),
            tckr VARCHAR NOT NULL,
            price DECIMAL(18,4) NOT NULL CHECK (price > 0),
            quantity DECIMAL(24,10) NOT NULL CHECK (quantity > 0),
            currency VARCHAR NOT NULL CHECK (currency IN ('USD', 'CAD'))
        )
        """)

def trade(conn: dd.DuckDBPyConnection, t: Transaction) -> None:
    # clients and trades live in the same database, so one connection checks both
    if conn.execute("SELECT 1 FROM clients WHERE id = ?", [t.client_id]).fetchone() is None:
        raise ValueError(f"Client ID: {t.client_id} is not in the clients table")

    if t.Date > date.today():
        raise ValueError(f"{t.Date} is in the future.")

    conn.execute(
        "INSERT INTO trades VALUES (?,?,?,?,?,?,?,?)",
        [t.client_id, t.account, t.Date, t.action, t.tckr, t.price, t.quantity, t.currency]
    )

    print(f"Successfully {"bought" if t.action == "buy" else "sold"} {t.quantity} of {t.tckr} @ {t.price}")

def show_trades(conn: dd.DuckDBPyConnection, client_id=None) -> None:
    if client_id is None:
        trades = conn.execute("SELECT * FROM trades ORDER BY date").df()
    else:
        trades = conn.execute("SELECT * FROM trades WHERE client_id = ? ORDER BY date", [client_id]).df()

    if trades.empty:
        print("No trades found.")
        return

    print(trades.to_string(index=False))

if __name__ == "__main__":
    # get_conn opens the test database; real trades are entered through private/enter_trades.py
    conn = get_conn()
    create_trades_table(conn)
    show_trades(conn)
