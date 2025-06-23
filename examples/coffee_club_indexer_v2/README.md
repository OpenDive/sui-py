# Coffee Club Event Indexer

A real-time event indexer for coffee club operations on the Sui blockchain, built with the SuiPy SDK. This indexer processes coffee club events and integrates with physical coffee machines for automated order fulfillment.

## Features

- **Real-time event processing** for coffee club operations using typed `SuiEvent` objects
- **Coffee machine integration** for automated order fulfillment
- **Voice agent notifications** via WebSocket for real-time order updates
- **Mock notification system** for testing voice agent integration
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

# Voice agent settings
export VOICE_AGENT_WEBSOCKET_URL=ws://localhost:8080  # Voice agent WebSocket URL
export VOICE_AGENT_ENABLED=true     # Enable/disable voice notifications

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

### Voice Agent Integration

The indexer can send real-time notifications to a voice agent via WebSocket for enhanced user experience:

**New Order Notifications:**
- Sent when `CoffeeOrderCreated` events are processed
- Includes order ID, coffee type, and priority level

**Order Status Updates:**
- Sent when `CoffeeOrderUpdated` events are processed  
- Includes status changes (Processing, Ready, Completed)
- Automatically sets priority to "urgent" for Ready orders

**Message Format:**
```json
{
  "type": "NEW_COFFEE_REQUEST",
  "order_id": "0x123...",
  "coffee_type": "Espresso",
  "priority": "normal",
  "timestamp": "2024-01-01T12:00:00"
}
```

The voice agent can acknowledge notifications and provide status confirmations.

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
  - `voice_agent_notifier.py` - WebSocket-based voice agent notifications
  - `mock_voice_notifications.py` - Mock notification system for testing
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

### Voice Agent Settings

The indexer supports integration with voice agents for real-time order notifications:

```bash
# Enable voice agent notifications
export VOICE_AGENT_ENABLED=true

# Voice agent WebSocket URL
export VOICE_AGENT_WEBSOCKET_URL=ws://localhost:8080
```

When disabled (`VOICE_AGENT_ENABLED=false`), the indexer will process events normally but skip voice agent notifications.

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

## Mock Notification System

For testing voice agent integration without requiring real blockchain events, use the mock notification system:

### Quick Demo

```bash
# Run a simple demo
python test_mock_notifications.py
```

### Standalone Script Usage

```bash
# Single order simulation
python handlers/mock_voice_notifications.py --scenario single --coffee Espresso --delay 2

# Rush period simulation (5 orders)
python handlers/mock_voice_notifications.py --scenario rush_period --orders 5 --delay 1

# Test all coffee types
python handlers/mock_voice_notifications.py --scenario mixed --delay 1.5

# Test error handling
python handlers/mock_voice_notifications.py --scenario errors

# Use custom voice agent URL
python handlers/mock_voice_notifications.py --scenario single --websocket-url ws://localhost:9000

# Enable verbose logging
python handlers/mock_voice_notifications.py --scenario rush_period --verbose
```

### Module Usage

```python
from handlers import MockNotificationGenerator

# Initialize generator
generator = MockNotificationGenerator()

# Simulate single order
await generator.simulate_single_order(
    coffee_type="Americano",
    delay_between_status=2.0
)

# Simulate rush period
order_ids = await generator.simulate_rush_period(
    num_orders=10,
    delay_between_orders=0.5,
    delay_between_status=1.0
)

# Test all coffee types
await generator.simulate_mixed_coffee_types(delay=1.0)
```

### Available Scenarios

- **`single`** - Complete lifecycle of one order (Created → Processing → Ready → Completed)
- **`rush_period`** - Multiple concurrent orders with staggered timing
- **`mixed`** - One order of each coffee type (Espresso, Americano, Doppio, Long, Coffee, HotWater)
- **`errors`** - Test error handling with invalid URLs and disabled notifications

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

### Testing Voice Agent Integration

For development without a voice agent server:

```bash
# Disable voice agent notifications
export VOICE_AGENT_ENABLED=false

# Test with mock notifications (voice agent not required)
python test_mock_notifications.py

# Test specific scenarios
python handlers/mock_voice_notifications.py --scenario errors
```

The mock notification system works independently and will show connection warnings when the voice agent server is not running, which is expected behavior for testing.

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
ENV VOICE_AGENT_ENABLED=true
ENV VOICE_AGENT_WEBSOCKET_URL=ws://voice-agent:8080

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
python indexer.py 2>&1 | grep "Voice agent"
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

**Voice Agent Connection Issues:**
```bash
# Test WebSocket connectivity
wscat -c $VOICE_AGENT_WEBSOCKET_URL

# Test with mock notifications
python handlers/mock_voice_notifications.py --scenario errors

# Check voice agent server status
curl -I http://localhost:8080/health  # If your voice agent has health endpoint
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