# Monobank Base WebSocket Client

This repository contains a Python WebSocket client for interacting with the Base service from Monobank, a subservice for streamers and content makers. It is built using the `websocket-client` library and provides additional features specific to Monobank, such as custom headers, widget data extraction, and automated ping handling.

## Features
- Handles connection lifecycle events such as `on_open`, `on_message`, `on_close`, and `on_error`.
- Sends periodic ping messages to keep the connection alive.

## Usage
Below is a basic example of how to use the `MonobankBaseWebSocketApp` class:

```python
from monobank_base_websocket.app import MonobankBaseWebSocketApp

# Initialize the WebSocket client
widget_url = "https://example.com/widget/url"
monobank_ws_app = MonobankBaseWebSocketApp(widget_url)

# Run the WebSocket client
monobank_ws_app.run_forever()
```

## Dependencies
- `websocket-client`
- `json`
- `logging`
- `threading`

## License
This project is licensed under the MIT License.
