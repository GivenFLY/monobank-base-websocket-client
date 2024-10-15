from dataclasses import dataclass


@dataclass
class WidgetData:
    type: str
    token: str
    widgetId: str
    shortName: str
