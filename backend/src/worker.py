from decimal import Decimal, getcontext
import time
import redis
from redis.exceptions import ConnectionError as RedisConnectionError # Import specific exception
from src.config import *
from src.calculation.pi_algorithm import calculate_pi_to_precision

# Set the Decimal context to allow high-precision math
# MAX_DIGITS is 100, so set precision to 110 for safety
getcontext().prec = MAX_DIGITS + 10

# --- 1. Initialization: Connect and Load State (with Retry) ---
def connect_and_load_state():
    """Attempts to connect to Redis and load the last known precision level."""
    retry_delay = 5
    print("\n--- Worker Initialization Start ---")
    while True:
        try:
            # Synchronous Redis connection
            r = redis.StrictRedis(host=REDIS_HOST, port=6379, decode_responses=True)
            r.ping() # Check connection immediately

            # Load state
            precision_str = r.get(PRECISION_KEY)
            current_precision = int(precision_str) if precision_str else 0
            
            print(f"Worker connected to Redis. Starting from precision: {current_precision} digits.")
            print("--- Worker Initialization Success ---\n")
            return r, current_precision
        
        except RedisConnectionError as e:
            print(f"Redis connection failed ({e}). Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
        except Exception as e:
            # Handle non-connection errors during initialization
            print(f"Error during state loading: {e}. Worker stopping.")
            exit(1)

# Execute initialization logic
r, current_precision = connect_and_load_state()


# --- 2. Main Calculation Loop ---
while True:
    while current_precision < MAX_DIGITS:
        
        # Increment precision *before* the loop's main logic
        # This value will be decremented if the subsequent Redis persistence fails.
        current_precision += 1 

        print(f"Attempting calculation for precision: {current_precision}")

        try:
            # A. Calculate Pi & Circumference
            # This is the resource-intensive step
            pi_str = calculate_pi_to_precision(current_precision)
            pi_decimal = Decimal(pi_str) 
            circumference = 2 * pi_decimal * Decimal(SUN_RADIUS_KM)

            # Define the template for quantization (e.g., '0.000' for precision 3)
            quantizer = Decimal('0.' + '0' * current_precision)

            # Quantize Pi and convert to string for saving
            pi_decimal_quantized = pi_decimal.quantize(quantizer)
            pi_str_quantized = str(pi_decimal_quantized)
            
            # Quantize the Decimal object, then immediately convert it to a plain string
            circumference_decimal = circumference.quantize(quantizer)
            circumference_str = str(circumference_decimal)

        except Exception as e:
            # Handle errors during the math calculation itself (e.g., memory exhaustion)
            print(f"CRITICAL: Math calculation failed for precision {current_precision}: {e}")
            current_precision -= 1 # Prevent trying this failing precision again immediately
            time.sleep(30) # Wait longer to allow system recovery
            continue # Skip to next loop iteration

        # --- 3. Persistence Block (Redis I/O) ---
        try:
            # B. Persistence and Signaling (Atomic Update)
            with r.pipeline() as pipe:
                pipe.set(PI_KEY, pi_str_quantized)
                pipe.set(PRECISION_KEY, current_precision)
                pipe.set(CIRCUMFERENCE_KEY, circumference_str)
                pipe.publish(REDIS_PUBSUB_CHANNEL, "UPDATE") # Signal API server
                pipe.execute()
            
            print(f"SUCCESS: Precision {current_precision} reached and persisted. Sleeping {1} second(s).")
            # C. Wait or Sleep (Optional: to manage CPU usage)
            time.sleep(1) 
            
        except RedisConnectionError as e:
            # Handle connection error specific to persistence/signaling
            print(f"WARNING: Redis persistence failed: {e}. Backing off and retrying precision {current_precision}...")
            current_precision -= 1 # Must decrement to retry saving *this* precision next time
            time.sleep(5) # Simple back-off for network recovery
            
        except Exception as e:
            # Handle non-connection errors during persistence (e.g., pipe error)
            print(f"WARNING: Unknown persistence error: {e}. Retrying precision {current_precision}...")
            current_precision -= 1
            time.sleep(5)

    # --- 4. Cap Reached ---
    print(f"\nCalculation capped at {MAX_DIGITS} digits. Worker is now idle (maintaining state).")
    time.sleep(3600)