# SuiPy Event Indexer

A real-time event indexer for the Sui blockchain built with the SuiPy SDK. This example demonstrates how to use typed Extended API schemas with Prisma Client Python for production-grade blockchain data indexing.

## Features

- **Real-time event processing** using typed `SuiEvent` objects
- **Automatic cursor tracking** and resumption from database
- **Database persistence** with Prisma Client Python
- **Auto-setup** - works out of the box with zero configuration
- **Configurable retry logic** with exponential backoff
- **Support for SQLite and PostgreSQL**
- **Modular event handler architecture**
- **Schema-first database design**
- **Production-ready** error handling and logging
- **✅ Fully tested** - Handles escrow and lock events correctly

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Indexer

```bash
python indexer.py
```

That's it! The indexer will automatically:
- Set up the database client on first run
- Create the SQLite database and tables
- Start monitoring blockchain events
- Resume from where it left off on restart

## Auto-Setup

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

## Configuration

The indexer can be configured via environment variables:

```bash
# Network settings
export SUI_NETWORK=mainnet          # mainnet, testnet, devnet
export SUI_RPC_URL=https://...      # Custom RPC endpoint

# Contract settings  
export SWAP_PACKAGE_ID=0x123...     # Target contract package ID

# Database settings
export DATABASE_URL=file:./my.db    # SQLite file path
# export DATABASE_URL=postgresql://... # For PostgreSQL

# Indexer settings
export POLLING_INTERVAL_MS=1000     # Polling frequency
export BATCH_SIZE=100               # Events per batch
export MAX_RETRIES=3                # Retry attempts
export RETRY_DELAY_MS=5000          # Retry delay
```

## Architecture

### Database Schema

The indexer uses a Prisma schema that exactly mirrors the TypeScript reference implementation:

```prisma
model Escrow {
  id        Int     @id @default(autoincrement())
  objectId  String  @unique
  sender    String?
  recipient String?
  keyId     String?
  itemId    String?
  swapped   Boolean @default(false)
  cancelled Boolean @default(false)
}

model Locked {
  id       Int     @id @default(autoincrement())
  objectId String  @unique
  creator  String?
  keyId    String?
  itemId   String?
  deleted  Boolean @default(false)
}

model Cursor {
  id       String @id
  eventSeq String
  txDigest String
}
```

### Event Handlers

- **`escrow_handler.py`** - Processes escrow creation, swapping, and cancellation
- **`locked_handler.py`** - Processes lock creation and destruction
- **Modular design** - Easy to add new event types

### Key Components

- **`indexer.py`** - Main indexer with event polling and cursor management
- **`config.py`** - Environment-based configuration
- **`setup.py`** - Auto-setup and Prisma client generation
- **`handlers/`** - Event processing modules
- **`schema.prisma`** - Database schema definition

## Development

### Running Tests

```bash
pip install pytest pytest-asyncio
python -m pytest test_indexer.py -v
```

### Database Operations

```bash
# View database
prisma studio

# Reset database
rm indexer.db
prisma db push

# Generate client after schema changes
prisma generate
```

### Adding New Event Types

1. Define event classes in a new handler file
2. Implement the handler function
3. Add the event tracker to `indexer.py`
4. Update the database schema if needed

## Production Deployment

### PostgreSQL Setup

```bash
# Update environment
export DATABASE_URL=postgresql://user:pass@host:5432/dbname

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

CMD ["python", "indexer.py"]
```

### Monitoring

The indexer provides structured logging for monitoring:

```bash
# Run with debug logging
export LOG_LEVEL=DEBUG
python indexer.py

# Monitor specific events
tail -f indexer.log | grep "escrow"
```

## Troubleshooting

### Common Issues

**Import Error: No module named 'prisma'**
```bash
# Run auto-setup
python setup.py

# Or manually
prisma generate
```

**Database Connection Error**
```bash
# Check database URL
echo $DATABASE_URL

# Reset database
rm indexer.db
prisma db push
```

**RPC Connection Error**
```bash
# Check network connectivity
curl -X POST $SUI_RPC_URL -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","id":1,"method":"sui_getLatestCheckpointSequenceNumber"}'
```

### Getting Help

- Check the logs for detailed error messages
- Verify environment variables are set correctly
- Ensure you have internet access (Prisma downloads binaries)
- Try running `python setup.py` manually

## Comparison with TypeScript

This Python implementation provides feature parity with the TypeScript reference:

| Feature | TypeScript | Python |
|---------|------------|--------|
| Database ORM | Prisma | Prisma Client Python |
| Schema | ✅ Identical | ✅ Identical |
| Event Processing | ✅ | ✅ |
| Cursor Tracking | ✅ | ✅ Fixed |
| Auto-setup | ❌ Manual | ✅ Automatic |
| Type Safety | ✅ | ✅ |
| Error Handling | ✅ | ✅ Enhanced |

The Python version adds auto-setup for improved developer experience while maintaining full compatibility with the TypeScript implementation. 