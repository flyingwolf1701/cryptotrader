# config/mapper.py
from automapper import Mapper
from services.binance.models import ExchangeInfo, SymbolInfo, RateLimit

# Initialize a global mapper instance
mapper = Mapper()

# Define mapping from raw JSON (dict) to our ExchangeInfo dataclass
mapper.create_map(dict, ExchangeInfo) \
    .for_member('timezone', lambda src: src.get('timezone')) \
    .for_member('serverTime', lambda src: src.get('serverTime')) \
    .for_member('rateLimits', lambda src: [mapper.map(r, RateLimit) for r in src.get('rateLimits', [])]) \
    .for_member('exchangeFilters', lambda src: src.get('exchangeFilters', [])) \
    .for_member('symbols', lambda src: [mapper.map(s, SymbolInfo) for s in src.get('symbols', [])])