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
