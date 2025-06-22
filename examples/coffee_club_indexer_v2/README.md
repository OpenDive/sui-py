# Coffee Club Event Indexer

A real-time event indexer for coffee club operations on the Sui blockchain, built with the SuiPy SDK. This indexer processes coffee club events and integrates with physical coffee machines for automated order fulfillment.

## Features

- **Real-time event processing** for coffee club operations using typed `SuiEvent` objects
- **Coffee machine integration** for automated order fulfillment
- **Automatic cursor tracking** and resumption from database
- **Database persistence** with Prisma Client Python
- **Auto-setup** - works out of the box with zero configuration
- **Configurable retry logic** with exponential backoff
- **Support for SQLite and PostgreSQL**
- **Modular event handler architecture**
- **Schema-first database design**
- **Production-ready** error handling and logging

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Set up your environment variables:

```bash
# Network settings
export SUI_NETWORK=testnet          # mainnet, testnet, devnet
export SUI_RPC_URL=https://...      # Custom RPC endpoint (optional)

# Coffee club contract settings  
export PACKAGE_ID=0x123...          # Your coffee club package ID

# Coffee machine settings
export MAC_ADDRESS=AA:BB:CC:DD:EE:FF # Coffee machine MAC address
export CONTROLLER_PATH=../delonghi_controller/src/delonghi_controller.py
export COFFEE_MACHINE_ENABLED=true  # Enable/disable machine integration

# Database settings
export DATABASE_URL=file:./coffee_club.db    # SQLite file path
# export DATABASE_URL=postgresql://...       # For PostgreSQL

# Indexer settings (optional)
export POLLING_INTERVAL_MS=5000     # Polling frequency
export ERROR_RETRY_INTERVAL_MS=30000 # Error retry delay
export BATCH_SIZE=100               # Events per batch
export MAX_RETRIES=3                # Retry attempts
```

### 3. Run the Indexer

```bash
python indexer.py
```

That's it! The indexer will automatically:
- Set up the database client on first run
- Create the SQLite database and tables
- Start monitoring coffee club events
- Trigger coffee machine when orders are processed
- Resume from where it left off on restart

## Architecture

### Event Types

The indexer processes three main event types:

- **`CafeCreated`** - New cafe registration events
- **`CoffeeOrderCreated`** - New coffee order events
- **`CoffeeOrderUpdated`** - Order status change events

### Coffee Machine Integration

When an order reaches the "Processing" status, the indexer:

1. Fetches the complete order object from the blockchain
2. Extracts the coffee type (espresso, americano, doppio, etc.)
3. Triggers the external coffee machine controller
4. Logs the operation results

Supported coffee types:
- `espresso`
- `americano`
- `doppio`
- `long`
- `coffee`
- `hotwater`

### Database Schema

```prisma
model Cafe {
  objectId    String    @id
  creator     String
  name        String?
  location    String?
  description String?
  status      String?
  createdAt   DateTime
  updatedAt   DateTime?
}

model CoffeeOrder {
  objectId  String    @id
  status    String
  createdAt DateTime
  updatedAt DateTime?
}

model Cursor {
  id       String @id
  eventSeq String
  txDigest String
}
```

### Key Components

- **`indexer.py`** - Main indexer with event polling and cursor management
- **`config.py`** - Environment-based configuration for coffee club settings
- **`handlers/`** - Event processing modules
  - `cafe_handler.py` - Processes cafe creation events
  - `order_handler.py` - Processes order events and triggers coffee machine
- **`coffee_machine/`** - Coffee machine integration
  - `controller.py` - Async coffee machine controller
- **`schema.prisma`** - Database schema definition
- **`setup.py`** - Auto-setup and Prisma client generation

## Configuration

### Coffee Machine Settings

The indexer supports integration with DeLonghi coffee machines via external Python controllers:

```bash
# Enable coffee machine integration
export COFFEE_MACHINE_ENABLED=true

# Coffee machine Bluetooth MAC address
export MAC_ADDRESS=AA:BB:CC:DD:EE:FF

# Path to the DeLonghi controller script
export CONTROLLER_PATH=../delonghi_controller/src/delonghi_controller.py
```

When disabled (`COFFEE_MACHINE_ENABLED=false`), the indexer will still process events but skip coffee machine operations.

### Network Configuration

```bash
# Use testnet (default)
export SUI_NETWORK=testnet

# Use mainnet
export SUI_NETWORK=mainnet

# Use custom RPC endpoint
export SUI_RPC_URL=https://my-custom-rpc.com
```

### Performance Tuning

```bash
# Fast polling for high-throughput scenarios
export POLLING_INTERVAL_MS=1000

# Larger batches for better throughput
export BATCH_SIZE=200

# Aggressive retries for unstable networks
export MAX_RETRIES=5
export ERROR_RETRY_INTERVAL_MS=10000
```

## Development

### Auto-Setup

The indexer includes intelligent auto-setup that:

- **Detects** if the database client needs to be generated
- **Automatically runs** `prisma generate` behind the scenes
- **Provides clear feedback** during setup
- **Caches setup** for fast subsequent runs
- **Gracefully handles errors** with helpful instructions

### Manual Setup (if needed)

If auto-setup fails, you can run setup manually:

```bash
python setup.py
```

Or use Prisma CLI directly:

```bash
prisma generate
prisma db push  # Optional: explicitly create database
```

### Database Operations

```bash
# View database
prisma studio

# Reset database
rm coffee_club.db
prisma db push

# Generate client after schema changes
prisma generate
```

### Adding New Event Types

1. Define event classes in a new handler file
2. Implement the handler function following the existing pattern
3. Add the event tracker to `indexer.py`
4. Update the database schema if needed

Example:

```python
# In handlers/new_handler.py
class NewEvent:
    def __init__(self, data: Dict[str, Any]):
        self.field = data["field"]

async def handle_new_events(events: List[SuiEvent], event_type: str, db: Prisma) -> None:
    # Process events...
    pass

# In indexer.py
EventTracker(
    type=f"{package_id}::coffee_club::NewEvent",
    filter=EventFilter.by_move_event_type(f"{package_id}::coffee_club::NewEvent"),
    callback=handle_new_events
)
```

### Testing Coffee Machine Integration

For development without hardware:

```bash
# Disable coffee machine
export COFFEE_MACHINE_ENABLED=false

# Or use a mock controller
export CONTROLLER_PATH=./mock_controller.py
```

Create a mock controller for testing:

```python
#!/usr/bin/env python3
# mock_controller.py
import sys
print(f"Mock coffee machine: Making {sys.argv[2]} coffee")
print("Coffee ready!")
```

## Production Deployment

### PostgreSQL Setup

```bash
# Update environment
export DATABASE_URL=postgresql://user:pass@host:5432/coffee_club

# Generate client for PostgreSQL
prisma generate
prisma db push
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python setup.py  # Pre-generate client

# Set environment variables
ENV SUI_NETWORK=mainnet
ENV PACKAGE_ID=0x...
ENV COFFEE_MACHINE_ENABLED=true

CMD ["python", "indexer.py"]
```

### Monitoring

The indexer provides structured logging for monitoring:

```bash
# Run with debug logging
export LOG_LEVEL=DEBUG
python indexer.py

# Monitor specific components
python indexer.py 2>&1 | grep "CAFE HANDLER"
python indexer.py 2>&1 | grep "ORDER HANDLER"
python indexer.py 2>&1 | grep "Coffee machine"
```

## Troubleshooting

### Common Issues

**Prisma Client Import Error:**
```bash
# Regenerate client
python setup.py
# or
prisma generate
```

**Coffee Machine Not Responding:**
```bash
# Check controller path
ls -la $CONTROLLER_PATH

# Test controller manually
python3.13 $CONTROLLER_PATH $MAC_ADDRESS espresso

# Check Bluetooth connectivity
hcitool scan
```

**Network Connection Issues:**
```bash
# Test RPC connectivity
curl -X POST $SUI_RPC_URL -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","method":"sui_getLatestSuiSystemState","params":[],"id":1}'
```

**Database Issues:**
```bash
# Reset database
rm coffee_club.db
prisma db push

# Check database file permissions
ls -la coffee_club.db
```

### Logging

Enable debug logging for detailed troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is part of the SuiPy SDK and follows the same license terms. 