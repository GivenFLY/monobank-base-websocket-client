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

## Advanced Usage

```python
import logging

from monobank_base_websocket.app import MonobankBaseWebSocketApp

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
WIDGET_URL = "your_widget_url_here"

# Example Usage
if __name__ == "__main__":

    def custom_on_message(ws, message):
        logger.info(f"Custom handler received message: {message}")

    def custom_on_error(ws, error):
        logger.error(f"Custom handler encountered error: {error}")

    def custom_on_close(ws, code, reason):
        logger.info(f"Custom handler detected closure: {code} - {reason}")

    def custom_on_open(ws):
        logger.info("Custom handler confirmed WebSocket is open.")

    # Initialize the WebSocket app
    ws_app = MonobankBaseWebSocketApp(
        widget_url=WIDGET_URL,
        on_message=custom_on_message,
        on_error=custom_on_error,
        on_close=custom_on_close,
        on_open=custom_on_open,
    )

    # Run the WebSocket app
    try:
        logger.info("Starting WebSocket client.")
        ws_app.run_forever()
    except KeyboardInterrupt:
        logger.info("WebSocket client stopped manually.")
    except Exception as e:
        logger.error(f"WebSocket client encountered an exception: {e}")
    finally:
        ws_app.stop_ping()

```

## Dependencies
- `websocket-client`
