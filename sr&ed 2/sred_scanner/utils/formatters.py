def fmt_currency(amount):
    """Format a number as Canadian currency."""
    if amount is None:
        return "N/A"
    if amount < 0:
        return f"-${abs(amount):,.0f}"
    return f"${amount:,.0f}"


def fmt_percentage(value):
    """Format a decimal as a percentage string."""
    if value is None:
        return "N/A"
    return f"{value:.1%}"


def status_badge(status):
    """Return emoji badge for a given status string."""
    mapping = {
        "COMPLETE": "COMPLETE",
        "PASS": "PASS",
        "ISSUES_FOUND": "ISSUES FOUND",
        "INCOMPLETE": "INCOMPLETE",
        "WARNING": "WARNING",
        "NOT_CALCULATED": "BLOCKED",
        "NOT_SIGNED": "NOT READY",
        "STRONG": "ELIGIBLE",
        "MEDIUM": "ELIGIBLE WITH RISK",
        "INELIGIBLE": "INELIGIBLE",
    }
    return mapping.get(status, status)


def severity_color(severity):
    """Return a color string for a severity level."""
    return {
        "HIGH": "#C4838E",
        "MEDIUM": "#C7A56A",
        "LOW": "#8FAE86",
    }.get(severity, "#888888")
