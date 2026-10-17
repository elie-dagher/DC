"""
Module: Data Engine

Problem:
Creating clients, recording trades, and ingesting market data requires calling
functions across multiple modules. This creates messy imports and repeated
setup code across files.

Description:
Single entry point for all data operations. Initializes database tables,
creates clients, records trades, and fetches/caches market data through
one unified interface. Holdings are not stored; they are derived from trades.

Key Functions:
- initialize_database: Initialize all DuckDB tables
- create_client: Add a client to the clients table
- add_prices_data: Fetch and cache market data for a ticker

Dependencies:
- clients.py: Client database operations
- trade.py: Trade ledger operations
- ingestion.py: Market data fetching and caching

Example:
    >>> conn = get_conn()
    >>> initialize_database(conn)
    >>> create_client(conn, c1)
    >>> trade(conn, t1)
    >>> add_prices_data(conn, "AMZN", "2024-01-01", "2024-12-31")
"""

import duckdb as dd
from datetime import date
from typing import Optional

from src.utils.config import get_conn
from src.utils.operations_models import Client
from src.utils.stock_models import Company
from src.data.clients import create_clients_table, add_client, get_client_data
from src.data.trade import Transaction, create_trades_table, trade, show_trades
from src.data.ingestion import get_prices, cache_prices, get_cached_price
from src.features.returns import simple_returns, log_returns, cumulative_returns, annualized_return, volatility
# from src.portfolio.reporting import generate_report
from src.data.companies import create_company_attributes_table, append_company, get_company_attributes

# ── Setup DuckDB Tables ──────────────────────────────────────────────────────────────────
def initialize_database(conn: dd.DuckDBPyConnection) -> None:
    create_company_attributes_table(conn)
    create_clients_table(conn)
    create_trades_table(conn)
    print("Database Initilized")

# ── Initialize Client Data ──────────────────────────────────────────────────────────────────
def create_client(conn: dd.DuckDBPyConnection, client: Client) -> None:
    add_client(conn, client)
    print(f"Successfully added {client.name}. ID={client.client_id}")

# ── Initialize Company Data ──────────────────────────────────────────────────────────────────
def create_company(conn: dd.DuckDBPyConnection, company: Company, as_of_date: date) -> None:
    append_company(conn, company, as_of_date)
    print(f"Successfully added {company.name} to companies table")

# ── Finanical Metric and Market Data Ingestion ──────────────────────────────────────────────────────────────────
def add_prices_data(conn: dd.DuckDBPyConnection, ticker: str, start_date: str, end_date: str) -> None:
    prices = get_prices(ticker, start_date, end_date)
    cache_prices(conn, prices, ticker)
    print(f"{ticker} prices cached from {start_date} to {end_date}.")

# ── Main Method ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Demo data (client "John") goes to the test database, never the real one
    conn = get_conn()

    ticker1 = "AMZN"
    ticker2 = "AAPL"
    
    start_date = '2025-01-01'
    end_date = '2025-12-31'

    # Ingest Prices Data (must happen before building trades that read cached prices)
    add_prices_data(conn, ticker1, start_date, end_date)
    add_prices_data(conn, ticker2, start_date, end_date)

    client1 = Client(client_id=1, name='John', risk_tolerance='medium',
                            #  age=None, cash_position=, considerations=None
                             goals='Saving for retirement'
                             )

    trades = [Transaction(client_id=1, account="TFSA", Date=date(2025, 1, 2), action="buy", tckr=ticker1, quantity=10,
                          price=get_cached_price(conn, ticker1, '2025-01-02'), currency="USD"),
              Transaction(client_id=1, account="TFSA", Date=date(2025, 1, 2), action="buy", tckr=ticker2, quantity=10,
                          price=get_cached_price(conn, ticker2, '2025-01-02'), currency="USD"),
              Transaction(client_id=1, account="TFSA", Date=date(2025, 6, 2), action="sell", tckr=ticker2, quantity=10,
                          price=get_cached_price(conn, ticker2, '2025-06-02'), currency="USD"),
        ]

    company = Company(name="Amazon", ticker="AMZN", sector="Consumer", industry="Retail", company_type="Mature")
    
    # Create DuckDB Tables
    initialize_database(conn)

    # Append and Portray Company
    create_company(conn, company, None)   
    print(get_company_attributes(conn, ticker1).to_string())   

    # Create and Portray Client
    create_client(conn, client1)
    print(get_client_data(conn, client1.client_id).to_string())

    # Record and Portray Trades (client must exist first)
    for t in trades:
        trade(conn, t)
    show_trades(conn, client1.client_id)

    # Calculate returns
    print(simple_returns(conn, "AMZN"))
    print(annualized_return(conn, "AMZN", start_date, end_date))
    print(volatility(simple_returns(conn, "AMZN")))

    # generate_report(conn, 1, start_date, end_date)    
    
    