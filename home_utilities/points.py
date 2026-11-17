"""Water point definitions for the simulated commissioning service."""

from dataclasses import dataclass


@dataclass(frozen=True)
class AnalogPoint:
    instance: int
    name: str
    description: str
    units: str
    sample: float


WATER_ANALOGS = (
    AnalogPoint(1, "WTR_LAST_HOUR", "Last completed reported hour", "usGallons", 12.0),
    AnalogPoint(2, "WTR_TODAY", "Recorded usage today", "usGallons", 30.0),
    AnalogPoint(3, "WTR_YESTERDAY", "Recorded usage yesterday", "usGallons", 120.0),
    AnalogPoint(4, "WTR_24HR", "Rolling 24-hour usage", "usGallons", 110.0),
    AnalogPoint(5, "WTR_MONTH", "Current calendar month", "usGallons", 1496.104),
    AnalogPoint(6, "WTR_CCF_MONTH", "Monthly volume in ft3; divide by 100 for CCF", "cubicFeet", 200.0),
    AnalogPoint(7, "WTR_AVG_GPM", "Average over reported hourly intervals", "usGallonsPerMinute", 0.08),
    AnalogPoint(8, "WTR_PEAK_HOUR", "Maximum reported hourly usage", "usGallons", 24.0),
    AnalogPoint(9, "WTR_DAILY_AVG", "Average daily usage", "usGallons", 105.0),
    AnalogPoint(10, "WTR_30DAY", "Rolling 30-day usage", "usGallons", 3150.0),
    AnalogPoint(11, "WTR_DATA_AGE", "Seconds since newest meter observation", "seconds", 3600.0),
)

WATER_BINARIES = (
    (1, "WTR_LEAK_SUSPECT", "Calculated continuous-use warning"),
    (2, "WTR_HIGH_USE", "Consumption threshold exceeded"),
    (3, "WTR_DATA_VALID", "Meter data meets freshness and completeness requirements"),
)
