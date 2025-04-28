# config/mapper.py
from automapper import Mapper
from services.binance.models import ExchangeInfo, SymbolInfo, RateLimit

# Initialize a global mapper instance
mapper = Mapper()

