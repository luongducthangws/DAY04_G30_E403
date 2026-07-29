from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any


def _parse_date(date_str: str) -> datetime:
    return datetime.strptime(date_str.strip(), "%Y-%m-%d")


def datetime_utils(
    action: str = "current_time",
    start_date: str | None = None,
    end_date: str | None = None,
    days: int = 0,
) -> dict[str, Any]:
    """Provides current time, date difference calculations, and relative date arithmetic.

    Args:
        action: "current_time", "date_diff", or "add_days".
        start_date: Date string YYYY-MM-DD for date_diff or add_days.
        end_date: Date string YYYY-MM-DD for date_diff.
        days: Integer number of days to add/subtract in add_days.

    Returns:
        Dictionary containing result string, details dictionary, and error.
    """
    clean_action = (action or "current_time").strip().lower()

    try:
        if clean_action == "current_time":
            now = datetime.now(timezone.utc)
            date_str = now.strftime("%Y-%m-%d")
            return {
                "action": "current_time",
                "result": date_str,
                "details": {
                    "iso_datetime": now.isoformat(),
                    "year": now.year,
                    "month": now.month,
                    "day": now.day,
                },
                "error": None,
            }

        elif clean_action == "date_diff":
            if not start_date or not end_date:
                return {
                    "action": "date_diff",
                    "result": None,
                    "details": {},
                    "error": "Both start_date and end_date (YYYY-MM-DD) are required for date_diff.",
                }
            d1 = _parse_date(start_date)
            d2 = _parse_date(end_date)
            diff_days = (d2 - d1).days
            return {
                "action": "date_diff",
                "result": f"{diff_days} days",
                "details": {
                    "start_date": start_date,
                    "end_date": end_date,
                    "days_difference": diff_days,
                },
                "error": None,
            }

        elif clean_action == "add_days":
            base_date = _parse_date(start_date) if start_date else datetime.now(timezone.utc)
            new_date = base_date + timedelta(days=days)
            new_date_str = new_date.strftime("%Y-%m-%d")
            return {
                "action": "add_days",
                "result": new_date_str,
                "details": {
                    "original_date": base_date.strftime("%Y-%m-%d"),
                    "days_added": days,
                    "target_date": new_date_str,
                },
                "error": None,
            }

        else:
            return {
                "action": action,
                "result": None,
                "details": {},
                "error": f"Unknown action '{action}'. Supported actions are 'current_time', 'date_diff', 'add_days'.",
            }

    except ValueError as ve:
        return {
            "action": action,
            "result": None,
            "details": {},
            "error": f"Invalid date format (expected YYYY-MM-DD): {ve}",
        }
    except Exception as exc:
        return {
            "action": action,
            "result": None,
            "details": {},
            "error": f"Failed datetime calculation: {exc}",
        }
