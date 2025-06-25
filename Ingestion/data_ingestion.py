import sys
import os
import requests
import json
import time
from kafka import KafkaProducer
from forex_python.converter import CurrencyRates
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from custom_logger import LLPackerLogger

logger = LLPackerLogger(os.path.basename(__file__), log_level='INFO')
load_dotenv()

producer = KafkaProducer(
    bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVER'),
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)
crypto_topic = os.getenv('CRYPTO_RATE_TOPIC')
currency_exchanege_rate_topic = os.getenv('CURRENCIES_EXCHANGE_RATE_TOPIC')
access_key = os.getenv('ACCESS_KEY')
base_currency = os.getenv('BASE_CURRENCY').split(',')
currencies = os.getenv('CURRENCIES').split(',')
crypto_ids = os.getenv('CRYPTO_IDS').split(',')
endpoint = 'live'

# === Source 1: CurrencyLayer ===
def fetch_from_exchangerate_host():
    access_key = os.getenv('ACCESS_KEY')  # Load from .env or replace directly
    endpoint = 'live'
    all_rates = {}

    for currency in base_currency:
        symbols = ','.join([cur for cur in currencies if cur != currency])
        url = f"http://api.currencylayer.com/{endpoint}?access_key={access_key}&currencies={symbols}&source={currency}&format=1"

        try:
            response = requests.get(url)
            data = response.json()
        except Exception as e:
            logger.error(f"Error calling API for base {currency}: {e}")
            continue

        if not data.get('success', False):
            logger.info(f"CurrencyLayer fetch failed for {currency}: {data.get('error')}")
            continue

        quotes = data['quotes']
        base_rates = {
            k.replace(currency, ''): v
            for k, v in quotes.items()
            if k != f"{currency}{currency}"
        }

        all_rates[currency] = base_rates

    return {
        'source': 'currencylayer',
        'timestamp': int(time.time()),
        'rates_by_base': all_rates
    }

# === Source 2: Forex-Python ===
def fetch_forex_rates():
    c = CurrencyRates()
    rates_by_base = {}

    for base in base_currency:
        base_rates = {}
        for target in currencies:
            if base == target:
                continue
            try:
                rate = c.get_rate(base, target)
                base_rates[target] = round(rate, 6)
            except Exception as e:
                print(f"⚠️ Error fetching rate {base} -> {target}: {e}")
        rates_by_base[base] = base_rates

    return {
        'source': 'forex-python',
        'timestamp': int(time.time()),
        'rates_by_base': rates_by_base
    }

# === Source 3: CoinGecko ===
def fetch_crypto_prices():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        'ids': ','.join(crypto_ids),                     # e.g. ['bitcoin', 'ethereum']
        'vs_currencies': ','.join([cur.lower() for cur in currencies])
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        # Transform into a structure similar to exchange rate data
        rates_by_base = {
            crypto_id.upper(): {cur.upper(): rate for cur, rate in prices.items()}
            for crypto_id, prices in data.items()
        }

        return {
            'source': 'coingecko',
            'timestamp': int(time.time()),
            'rates_by_base': rates_by_base
        }

    except Exception as e:
        print(f"Error fetching crypto prices: {e}")
        return None
    
# === Kafka Producer ===
def send_to_kafka(topic, data):
    if data:
        producer.send(topic, data)
        producer.flush()
        logger.success(f"Sent to topic '{topic}': {data}")

# === Main Loop: Fetch from All Sources ===

while True:
    sources = [fetch_from_exchangerate_host, fetch_forex_rates, fetch_crypto_prices]
    for fetch_func in sources:
        data = fetch_func()
        if data:
            logger.info(f" Sending from source: {data['source']}")
            print(json.dumps(data, indent=2), "\n")
            if fetch_func =='fetch_crypto_prices':
                send_to_kafka(crypto_topic, data)
            else:
                send_to_kafka(currency_exchanege_rate_topic, data)
            logger.success(f" Sent FX data from {data['source']}")
    
    time.sleep(30)
