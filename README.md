# Video Translation Status Client Library

A Python client library for mocking the action of monitoring video translation progress. This library helps you track the status of video translations by polling a status endpoint with exponential backoff strategy to balance performance and server load.

## Installation

```bash
pip install flask requests
```

## How to Use

### 1. Start the Server

First, run the translation server in a terminal:
```bash
python run_server.py
```

The server will start on http://localhost:8000

### 2. Use the Client Library

You can use the client library in three ways:

#### Basic Usage

Simply create a client and wait for completion:

```python
from translation_system import TranslationClient

# Create client
client = TranslationClient("http://localhost:8000")

# Wait for translation to complete
result = client.wait_for_completion()
```

#### Monitor Progress

If you want to track the translation progress:

```python
def status_handler(status):
    if "progress" in status:
        print(f"Progress: {status['progress']}%")
    else:
        print(f"Status: {status['result']}")

client = TranslationClient(
    base_url="http://localhost:8000",
    status_callback=status_handler
)

result = client.wait_for_completion()
```

#### Custom Configuration

Adjust polling behavior and timeouts:

```python
from translation_system import ClientConfig

config = ClientConfig(
    initial_delay=1.0,    # Initial delay between checks (seconds)
    max_delay=5.0,        # Maximum delay between checks
    timeout=30.0         # Overall timeout in seconds
)

client = TranslationClient(
    base_url="http://localhost:8000",
    config=config
)
```

#### Error Handling

```python
from translation_system import TranslationError

try:
    result = client.wait_for_completion()
    print("Translation completed!")
except TranslationError as e:
    print(f"Translation failed: {e}")
```
