"""Fictional widget-service entry point."""


def greet(widget: str) -> str:
    """Return a greeting for a widget."""
    return f"Hello, {widget}!"


if __name__ == "__main__":
    print(greet("widget"))
