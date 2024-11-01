"""
Module: Monobank Base WebSocket Client

This module provides a custom WebSocket client for interacting with Base Monobank's WebSocket API.
It extends the `WebSocketApp` class from the `websocket-client` library to facilitate connecting,
sending commands, receiving messages, and managing the connection lifecycle with Base Monobank's WebSocket server.

Classes:
- `MonobankBaseWebSocketApp`: Extends `WebSocketApp` and provides additional features specific to Base Monobank's API.

Usage Example:
```python
from monobank_base_websocket_client import MonobankBaseWebSocketApp

# Initialize the WebSocket client
widget_url = "https://example.com/widget/url"
base_monobank_ws_app = MonobankBaseWebSocketApp(widget_url)

# Run the WebSocket client
monobank_ws_app.run_forever()
```
"""

import json
import logging
import threading
from functools import cached_property

from websocket import WebSocketApp

from monobank_base_websocket._parser import parse_widget_url

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

WEBSOCKET_URL = "wss://base.monobank.com.ua/ext/api/web/wss"

SEC_WEBSOCKET_PROTOCOL = (
    "mono, "
    "eyJxclRva2VuIjoid19jMmQwM2JlYmViYmZjYzEwMWUzNzdkNmRiNDNhMzk3NDIyMTE5NjdhZDZkZjFjMDllYjdmZGY4OGIyOGNjZTY3ODE4NmU3NDEifQ"
)


class MonobankBaseWebSocketApp(WebSocketApp):
    def __init__(self, widget_url, *args, **kwargs):
        """
        Initialize the MonobankBaseWebSocketApp instance.

        :param widget_url: The URL of the widget, used to extract widget-specific data.
        :param *args: Additional positional arguments to pass to the parent WebSocketApp class.
        :param **kwargs: Additional keyword arguments to pass to the parent WebSocketApp class.

        The constructor sets up the WebSocket connection URL, headers, and callback handlers.
        It also removes the 'url' key from kwargs if present to avoid conflicts with the internal URL.
        Custom headers are defined, including the 'Sec-WebSocket-Protocol' for Monobank communication.
        """
        # Remove 'url' from kwargs if present to avoid conflicts
        self._url = WEBSOCKET_URL
        self.widget_url = widget_url

        self._header = kwargs.pop("header", {})
        self._header["Sec-WebSocket-Protocol"] = SEC_WEBSOCKET_PROTOCOL

        # Store user-provided callback handlers
        self._on_message = kwargs.pop("on_message", None)
        self._on_error = kwargs.pop("on_error", None)
        self._on_close = kwargs.pop("on_close", None)
        self._on_open = kwargs.pop("on_open", None)

        # Initialize the parent WebSocketApp with overridden handlers
        super().__init__(
            *args,
            url=self._url,
            header=self._header,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
            on_open=self.on_open,
            **kwargs,
        )

        # Initialize ping thread related attributes
        self._ping_interval = 5  # seconds
        self._ping_thread = None
        self._ping_stop_event = threading.Event()

    def _send_command(self, command, data: dict = None) -> None:
        """
        Send a command to the server.

        :param command: The command name.
        :param data: A dictionary containing the command data.
        """
        request_body = {
            "c": command,
        }
        if data:
            request_body["data"] = data
        raw_data = json.dumps(request_body)
        self.send(raw_data)
        logger.debug(f"Sent command: {raw_data}")

    @cached_property
    def widget_data(self):
        """
        Parse the widget URL to extract necessary data.
        Assumes that `parse_widget_url` returns an object with `widget_id` and `short_name` attributes.
        """
        parsed = parse_widget_url(self.widget_url)
        logger.debug(f"Parsed widget data: {parsed}")
        return parsed

    def on_message(self, ws, message):
        """
        Handle incoming messages from the WebSocket.
        """
        logger.debug(f"Received message: {message}")
        try:
            message_data = json.loads(message)
            if message_data.get("c") == "ping":
                self.handle_pong(message_data)
        except json.JSONDecodeError:
            logger.warning("Received non-JSON message.")
        except Exception as e:
            logger.error(f"Error processing message: {e}")

        if self._on_message:
            self._on_message(ws, message)

    def handle_pong(self, message_data):
        """
        Handle server's response to a ping.

        :param message_data: The parsed JSON message from the server.
        """
        conn_trace = message_data.get("data", {}).get("connTrace")
        trace_id = message_data.get("traceId")
        status = message_data.get("s")
        if status == 200:
            logger.debug(
                f"Ping acknowledged. connTrace: {conn_trace}, traceId: {trace_id}"
            )
        else:
            logger.warning(f"Ping failed with status: {status}, traceId: {trace_id}")

    def on_error(self, ws, error):
        """
        Handle errors from the WebSocket.
        """
        logger.error(f"WebSocket error: {error}")
        if self._on_error:
            self._on_error(ws, error)

    def on_close(self, ws, close_status_code, close_msg):
        """
        Handle the closing of the WebSocket connection.
        """
        logger.info(
            f"WebSocket closed with code: {close_status_code}, message: {close_msg}"
        )
        self.stop_ping()
        if self._on_close:
            self._on_close(ws, close_status_code, close_msg)

    def on_open(self, ws):
        """
        Handle the opening of the WebSocket connection.
        Sends the subscribe command upon successful connection.
        Also starts the ping thread.
        """
        logger.info("WebSocket connection opened.")
        try:
            data = {
                "event": "/ext/api/web/update-widget",
                "params": {
                    "widgetId": self.widget_data.widgetId,
                    "shortName": self.widget_data.shortName,
                },
            }
            self._send_command("subscribe", data=data)
            logger.info("Subscribe command sent.")
        except AttributeError as e:
            logger.error(f"Error accessing widget data: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during on_open: {e}")

        # Start the ping thread
        self.start_ping()

        if self._on_open:
            self._on_open(ws)

    def start_ping(self):
        """
        Start a background thread that sends a ping every `self._ping_interval` seconds.
        """
        if self._ping_thread and self._ping_thread.is_alive():
            logger.warning("Ping thread is already running.")
            return

        self._ping_stop_event.clear()
        self._ping_thread = threading.Thread(target=self._ping_loop, daemon=True)
        self._ping_thread.start()
        logger.info("Ping thread started.")

    def stop_ping(self):
        """
        Stop the background ping thread.
        """
        if self._ping_thread and self._ping_thread.is_alive():
            self._ping_stop_event.set()
            self._ping_thread.join()
            logger.info("Ping thread stopped.")

    def _ping_loop(self):
        """
        The loop that sends ping commands at regular intervals.
        """
        logger.debug("Entering ping loop.")
        while not self._ping_stop_event.is_set():
            try:
                ping_payload = {"c": "ping"}
                self._send_command("ping")
                logger.debug("Ping command sent.")
            except Exception as e:
                logger.error(f"Error sending ping: {e}")
            # Wait for the specified interval or until stop event is set
            if self._ping_stop_event.wait(self._ping_interval):
                break
        logger.debug("Exiting ping loop.")
