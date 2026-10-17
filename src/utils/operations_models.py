"""
Module: Data Schemas/Blueprints

Problem:
Client and portfolio data needs structure and validation. Without schemas,
inconsistent data causes bugs in calculations and storage.

Description:
Defines Pydantic models for clients. Ensures all data matches expected types and
constraints before entering the system. Holdings are not part of the client;
they are derived from the trades table (see src/data/trade.py).

Key Classes:
- Client: Represents a client and their profile

Dependencies:
- pydantic: For schema validation
- typing: For type hints
- datetime: For date fields

Note on Optional:
Fields that may be missing are typed `Optional[X] = None` rather than
`X = Field(default=None)`. Both behave the same at runtime, but only the
first is honest about the type, which keeps Pylance quiet.

Example:
    >>> client = Client(client_id=1, name="John", risk_tolerance="medium", goals="Growth")
"""

from typing import Optional
from pydantic import BaseModel, Field


class Client(BaseModel):
    client_id: int
    name: str = Field(default="Anon")
    risk_tolerance: str
    age: Optional[int] = None
    cash_position: Optional[int] = None
    goals: str
    considerations: Optional[str] = None
