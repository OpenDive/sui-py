# SuiPy Examples

This directory contains example scripts demonstrating various features of the SuiPy SDK.

## Write API Example

**File**: `write_api_example.py`

Test the Sui Write API with transaction execution, dry runs, and dev inspect functionality.

### Features Demonstrated

- ✅ **Transaction Execution**: Execute signed transactions on the Sui network
- ✅ **Dry Run**: Test transactions without committing to the blockchain
- ✅ **Dev Inspect**: Detailed transaction analysis for development
- ✅ **Response Options**: Configure what data to include in responses
- ✅ **Format Handling**: Support for base64 and hex transaction formats
- ✅ **Error Handling**: Comprehensive error scenarios and recovery

### Quick Start

```bash
# Use built-in example data
python3 examples/write_api_example.py

# Use your own transaction data
python3 examples/write_api_example.py <tx_bytes> <signature>

# Specify sender address explicitly
python3 examples/write_api_example.py <tx_bytes> <signature> <sender>
```

### Working Example

```bash
python3 examples/write_api_example.py \
  "AAAEAQBX81xJQM5DHo5/jceY0CRyy75ofrHiPR08Z87V+uJp0SUeUCIAAAAAIOG7Q2BqQ7ubDu+AMmcKnOMtQ9qlCPVyov5TAUwSBiU5AAgBAAAAAAAAAAEB+kXkr+JWG8JF5msZDy5DkcCptMOkz7UUC2RKVX4Q5Ox6LDkiAAAAAAEBAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGAQAAAAAAAAAAAwIBAAABAQEAALkI7DF3LJccTHGo/QLJ4W/2TmTcck15IDO06bHDVJHrCXJvYm90X3BldAJoaQAAALkI7DF3LJccTHGo/QLJ4W/2TmTcck15IDO06bHDVJHrCXJvYm90X3BldApmZWVkX3RyZWF0AAQBAgADAAAAAAIBAAEDAM0yfOn6ogI/ApPwOB063148bFd7ZbYSZKWoCNyCeblkAU3b6gkObn2/Rr8HB9Vj68sMNC8xqn2QVUDx5HVQNrpUWWVQIgAAAAAg9Rr3yuGntheUmkysknxBWwks+6Wqbh41Z64mAPCD8c3NMnzp+qICPwKT8DgdOt9ePGxXe2W2EmSlqAjcgnm5ZOgDAAAAAAAAhNgxAAAAAAAA" \
  "AAt4ih9jPcbdc3SkSiBI6gbL+3MRnnHs5V3hM1ptgHr/AEu/YjXx2QTh5/orJqYSji/qwvW/zWU0fZqJ8oSWywdunWqkb/0h4vSCCYj1w2OU84nFcZtk45+ZI+TTBcdtYg=="
```

### Parameters

| Parameter | Format | Description | Example |
|-----------|--------|-------------|---------|
| `tx_bytes` | Base64 string | Transaction bytes (400-800+ chars) | `"AAAEAQBX81xJQM5DHo5..."` |
| `signature` | Base64 string | Transaction signature (132 chars) | `"AAt4ih9jPcbdc3SkSiBI..."` |
| `sender` | Hex address | Sender address (optional) | `"0xcd327ce9faa2023f..."` |

### How to Get Transaction Data

#### Using Sui CLI
```bash
# Create and get transaction bytes
sui client transfer-sui --to 0x... --amount 1000000 --dry-run

# Sign the transaction
sui client sign --data <transaction_bytes>
```

#### Using TypeScript SDK
```typescript
// Build transaction
const tx = new TransactionBlock();
tx.transferObjects([coin], recipient);

// Get transaction bytes
const bytes = await tx.build({ client });

// Sign transaction
const signature = await keypair.signTransactionBlock(bytes);
```

### Expected Output

```
🔥 SuiPy Write API Example
==================================================
📝 Using provided transaction data
   Transaction bytes: 608 chars
   Signature: 132 chars
   Sender: 0xcd327ce9faa2023f0293f0381d3adf5e3c6c577b65b61264a5a808dc8279b964

🌐 Connected to Sui testnet

=== Dry Run Transaction ===
✅ Dry run completed in 0.14s
   Transaction status: {'status': 'success'}
   Gas used: {'computationCost': '1000000', 'storageCost': '4278800', ...}

=== Execute Transaction ===
✅ Transaction executed successfully in 0.07s
   Transaction digest: D661ZS4KiX4Zw4zpKcDtWXxmAw5JgsgpNabmMe3Bzmah
   Status: {'status': 'success'}
   Gas used: {'computationCost': '1000000', 'storageCost': '4028000', ...}
```

### Troubleshooting

#### Common Issues

**Invalid transaction bytes format**
- Ensure transaction bytes are in base64 format
- Check that the string is complete (no truncation)

**Invalid signature length**
- Signatures should be exactly 132 characters in base64 format
- Verify the signature corresponds to the transaction bytes

**Network connection issues**
- Ensure internet connectivity
- Check if Sui testnet is accessible
- Try again if there are temporary network issues

**Transaction already executed**
- The example transaction may show as already executed (this is normal)
- Use fresh transaction bytes for new executions

#### Getting Help

- Check the inline documentation in the script
- Review the SuiPy SDK documentation
- Ensure you're using compatible transaction formats

## Other Examples

More examples will be added as the SDK grows. Check this directory for:
- Account management examples
- Transaction building examples
- Crypto and signing examples
- Advanced SDK usage patterns
