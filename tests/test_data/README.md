# Test Data

This directory contains sample JSON responses from Sui RPC API for testing and validation.

## Structure

```
test_data/
├── write_api/          # Write API samples
│   └── execute_transaction_block_success.json
├── read_api/           # Read API samples  
└── move_utils/         # Move Utils API samples
```

## Usage

```python
from tests.test_data import load_json

# Load a sample response
sample_data = load_json("write_api/execute_transaction_block_success.json")

# Use in tests
response = SuiTransactionBlockResponse.from_dict(sample_data)
assert response.digest is not None
```

## Adding New Samples

1. Create JSON files with descriptive names:
   - `{method_name}_{scenario}.json`
   - Example: `execute_transaction_block_with_events.json`

2. Include all required fields for the response type
3. Use realistic data from actual API responses
4. Add comments with `_comment` fields if needed

## Sample Types Needed

### Write API
- [x] `execute_transaction_block_success.json` (placeholder created)
- [ ] `execute_transaction_block_with_events.json`
- [ ] `dry_run_transaction_block.json`
- [ ] `dev_inspect_transaction_block.json`

### Read API
- [ ] `get_transaction_block.json`
- [ ] `get_object.json`
- [ ] `get_checkpoint.json`

### Move Utils API
- [ ] `get_move_function_arg_types.json`
- [ ] `get_normalized_function.json`
