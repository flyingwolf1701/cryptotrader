from automapper import AutoMapper
from services.binance.models.base_models import RateLimit, SymbolInfo, ExchangeInfo

# Initialize the automapper
mapper = AutoMapper()

# Teach Automapper how to extract fields from our dataclasses
# For each dataclass, register its fields via add_spec
mapper.add_spec(RateLimit, lambda cls: list(cls.__dataclass_fields__.keys()))
mapper.add_spec(SymbolInfo, lambda cls: list(cls.__dataclass_fields__.keys()))
mapper.add_spec(ExchangeInfo, lambda cls: list(cls.__dataclass_fields__.keys()))

# Register mappings for nested models first
mapper.create_map(dict, RateLimit).auto_map()
mapper.create_map(dict, SymbolInfo).auto_map()

# Finally, ExchangeInfo (uses nested mappings for rateLimits and symbols)
mapper.create_map(dict, ExchangeInfo).auto_map()

__all__ = ['mapper']