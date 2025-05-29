# SuiPy Event Indexer

A production-ready event indexer for the Sui blockchain built with the SuiPy SDK. This example demonstrates how to use the typed Extended API schemas to build a real-time blockchain data indexing system.

## Features

- **Real-time Event Processing**: Continuously polls the Sui blockchain for new events
- **Typed Event Handling**: Uses SuiPy's typed `SuiEvent` objects for type safety
- **Automatic Resumption**: Tracks cursors in the database to resume from where it left off
- **Database Persistence**: Stores indexed data using SQLAlchemy 2.0 with async support
- **Configurable**: Environment-based configuration for different networks and contracts
- **Robust Error Handling**: Retry logic with exponential backoff
- **Multi-Database Support**: Works with SQLite (default) and PostgreSQL
- **Modular Architecture**: Easy to extend with new event handlers

## Architecture

The indexer is structured similarly to the TypeScript reference implementation:

```
event_indexer/
├── config.py              # Configuration management
├── database.py             # Database connection and session management
├── models.py               # SQLAlchemy database models
├── indexer.py              # Main indexer logic
├── handlers/               # Event handlers
│   ├── __init__.py
│   ├── escrow_handler.py   # Handles escrow events
│   └── locked_handler.py   # Handles lock events
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Quick Start

### 1. Install Dependencies

```bash
cd examples/event_indexer
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file or set environment variables:

```bash
# Network configuration
export SUI_NETWORK=mainnet
export SUI_RPC_URL=https://fullnode.mainnet.sui.io:443

# Contract configuration (replace with your actual package ID)
export SWAP_PACKAGE_ID=0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef

# Database configuration
export DATABASE_URL=sqlite+aiosqlite:///./indexer.db
export DATABASE_ECHO=false

# Indexer settings
export POLLING_INTERVAL_MS=1000
export BATCH_SIZE=100
export MAX_RETRIES=3
export RETRY_DELAY_MS=5000
```

### 3. Run the Indexer

```bash
python -m event_indexer.indexer
```

Or run as a module:

```bash
python -c "from event_indexer import main; import asyncio; asyncio.run(main())"
```

## Configuration

The indexer is configured through environment variables or the `config.py` file:

| Variable | Default | Description |
|----------|---------|-------------|
| `SUI_NETWORK` | `mainnet` | Sui network to connect to |
| `SUI_RPC_URL` | Network default | Custom RPC endpoint URL |
| `SWAP_PACKAGE_ID` | Example ID | Package ID of the swap contract to monitor |
| `DATABASE_URL` | SQLite file | Database connection URL |
| `DATABASE_ECHO` | `false` | Enable SQL query logging |
| `POLLING_INTERVAL_MS` | `1000` | Polling interval in milliseconds |
| `BATCH_SIZE` | `100` | Number of events to fetch per batch |
| `MAX_RETRIES` | `3` | Maximum retry attempts on errors |
| `RETRY_DELAY_MS` | `5000` | Base retry delay in milliseconds |

## Database Schema

The indexer creates three tables:

### Cursors
Tracks the last processed event for each event type:
```sql
CREATE TABLE cursors (
    id VARCHAR(255) PRIMARY KEY,      -- Event type identifier
    event_seq VARCHAR(50) NOT NULL,   -- Event sequence number
    tx_digest VARCHAR(100) NOT NULL,  -- Transaction digest
    created_at DATETIME,
    updated_at DATETIME
);
```

### Escrows
Tracks escrow objects from the swap contract:
```sql
CREATE TABLE escrows (
    object_id VARCHAR(66) PRIMARY KEY,  -- Sui object ID
    sender VARCHAR(66),                 -- Escrow sender address
    recipient VARCHAR(66),              -- Escrow recipient address
    key_id VARCHAR(66),                 -- Key object ID
    item_id VARCHAR(66),                -- Item object ID
    swapped BOOLEAN DEFAULT FALSE,      -- Whether escrow was swapped
    cancelled BOOLEAN DEFAULT FALSE,    -- Whether escrow was cancelled
    created_at DATETIME,
    updated_at DATETIME
);
```

### Locked
Tracks locked objects from the swap contract:
```sql
CREATE TABLE locked (
    object_id VARCHAR(66) PRIMARY KEY,  -- Sui object ID
    creator VARCHAR(66),                -- Lock creator address
    key_id VARCHAR(66),                 -- Key object ID
    item_id VARCHAR(66),                -- Item object ID
    deleted BOOLEAN DEFAULT FALSE,      -- Whether lock was destroyed
    created_at DATETIME,
    updated_at DATETIME
);
```

## Event Handlers

The indexer processes two types of events:

### Lock Events (`lock` module)
- **LockCreated**: Creates a new lock record
- **LockDestroyed**: Marks a lock as deleted

### Escrow Events (`shared` module)
- **EscrowCreated**: Creates a new escrow record
- **EscrowSwapped**: Marks an escrow as swapped
- **EscrowCancelled**: Marks an escrow as cancelled

Each handler:
1. Validates event origin
2. Parses typed `SuiEvent` objects
3. Batches updates by object ID
4. Performs efficient database upserts
5. Handles multiple events for the same object

## Type Safety Benefits

The indexer leverages SuiPy's typed schemas for:

```python
# Typed event processing
events: Page[SuiEvent] = await client.extended_api.query_events(
    query=event_filter,
    cursor=cursor,
    limit=batch_size
)

# Type-safe event data access
for event in events:
    print(f"Event: {event.type}")           # str
    print(f"Sender: {event.sender}")        # SuiAddress
    print(f"Package: {event.package_id}")   # ObjectID
    print(f"Data: {event.parsed_json}")     # Optional[Dict[str, Any]]
```

## Error Handling

The indexer includes robust error handling:

- **RPC Errors**: Automatic retry with exponential backoff
- **Validation Errors**: Clear error messages for invalid data
- **Database Errors**: Transaction rollback and retry
- **Network Issues**: Configurable retry limits and delays
- **Graceful Shutdown**: Proper cleanup on interruption

## Database Support

### SQLite (Default)
```bash
export DATABASE_URL=sqlite+aiosqlite:///./indexer.db
```

### PostgreSQL
```bash
export DATABASE_URL=postgresql+asyncpg://user:password@localhost/indexer
pip install asyncpg
```

## Monitoring and Logging

The indexer provides comprehensive logging:

```
2024-01-01 12:00:00 - event_indexer.indexer - INFO - Starting SuiPy Event Indexer...
2024-01-01 12:00:00 - event_indexer.indexer - INFO - Network: mainnet
2024-01-01 12:00:00 - event_indexer.indexer - INFO - RPC URL: https://fullnode.mainnet.sui.io:443
2024-01-01 12:00:00 - event_indexer.indexer - INFO - Setting up listeners for 2 event types
2024-01-01 12:00:01 - event_indexer.handlers.escrow_handler - INFO - Processing 5 escrow events
2024-01-01 12:00:01 - event_indexer.handlers.locked_handler - INFO - Processing 3 lock events
```

## Extending the Indexer

### Adding New Event Types

1. Create a new handler in `handlers/`:
```python
# handlers/my_handler.py
async def handle_my_events(events: List[SuiEvent], event_type: str, session: AsyncSession) -> None:
    # Process events
    pass
```

2. Add to the indexer configuration:
```python
# indexer.py
EventTracker(
    type=f"{CONFIG.swap_contract.package_id}::my_module",
    filter=EventFilter.by_module(CONFIG.swap_contract.package_id, "my_module"),
    callback=handle_my_events
)
```

3. Create corresponding database models in `models.py`

### Custom Event Filters

Use SuiPy's `EventFilter` helpers:

```python
# Filter by specific event type
filter = EventFilter.by_event_type("0x2::coin::CoinCreated")

# Filter by sender
filter = EventFilter.by_sender("0x...")

# Filter by time range
filter = EventFilter.by_time_range(start_time, end_time)

# Custom filter
filter = {"Package": package_id}
```

## Production Deployment

### Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "-m", "event_indexer.indexer"]
```

### Environment Variables
```bash
# Production settings
export SUI_NETWORK=mainnet
export DATABASE_URL=postgresql+asyncpg://user:password@db:5432/indexer
export POLLING_INTERVAL_MS=500
export BATCH_SIZE=200
export MAX_RETRIES=5
```

### Monitoring
- Use structured logging for observability
- Monitor database performance and connection pools
- Set up alerts for indexer failures
- Track event processing latency and throughput

## Comparison with TypeScript Implementation

This Python implementation mirrors the TypeScript reference:

| Feature | TypeScript | Python |
|---------|------------|--------|
| Event Polling | ✅ | ✅ |
| Cursor Tracking | ✅ | ✅ |
| Database Persistence | Prisma | SQLAlchemy |
| Type Safety | ✅ | ✅ (Enhanced) |
| Error Handling | ✅ | ✅ (Enhanced) |
| Modular Handlers | ✅ | ✅ |
| Configuration | ✅ | ✅ (Enhanced) |

### Python Advantages
- **Enhanced Type Safety**: Full type hints with runtime validation
- **Better Error Handling**: Structured exception handling with retry logic
- **Database Flexibility**: Support for multiple database backends
- **Configuration Management**: Environment-based configuration with defaults
- **Async Performance**: Native async/await with efficient connection pooling

## Troubleshooting

### Common Issues

1. **Connection Errors**
   - Check RPC URL and network connectivity
   - Verify Sui network is accessible

2. **Database Errors**
   - Ensure database URL is correct
   - Check database permissions and connectivity

3. **Event Processing Errors**
   - Verify contract package ID is correct
   - Check event structure matches expected format

4. **Performance Issues**
   - Adjust batch size and polling interval
   - Monitor database query performance
   - Consider connection pooling settings

### Debug Mode
```bash
export DATABASE_ECHO=true  # Enable SQL logging
python -c "import logging; logging.basicConfig(level=logging.DEBUG)"
```

## License

This example is part of the SuiPy SDK and follows the same license terms. 