import urllib.parse

from monobank_base_websocket._dataclasses import WidgetData


def parse_widget_url(widget_url: str) -> WidgetData:
    """
    Parse widget url and return WidgetData object
    :param widget_url: widget url
    :return: WidgetData object
    """
    parsed_url = urllib.parse.urlparse(widget_url)
    query = urllib.parse.parse_qs(parsed_url.query)
    return WidgetData(
        type=parsed_url.scheme,
        token=query.get("token")[0],
        widgetId=query.get("widgetId")[0],
        shortName=query.get("shortName")[0],
    )
