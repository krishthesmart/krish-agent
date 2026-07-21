"""
Example: Sample Python module to generate tests for.
Shows what the worker and reviewer will work with.
"""


def add(a: int, b: int) -> int:
    """Add two numbers and return the result."""
    return a + b


def divide(a: float, b: float) -> float:
    """
    Divide a by b.

    Raises:
        ValueError: If b is zero.
    """
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


def filter_even_numbers(numbers: list) -> list:
    """Filter and return only even numbers from a list."""
    return [n for n in numbers if n % 2 == 0]


def greet(name: str, formal: bool = False) -> str:
    """
    Generate a greeting message.

    Args:
        name: The person's name.
        formal: If True, use formal greeting; otherwise casual.

    Returns:
        A greeting string.
    """
    if formal:
        return f"Good day, {name}."
    return f"Hey {name}!"


def process_data(data: dict) -> dict:
    """
    Process a data dictionary by extracting and transforming values.

    Expected input:
        {"name": str, "age": int, "email": str}

    Returns:
        {"name": str (uppercase), "age": int, "email": str (lowercase)}

    Raises:
        KeyError: If required fields are missing.
        TypeError: If types are incorrect.
    """
    if not isinstance(data, dict):
        raise TypeError("Input must be a dictionary")

    required_keys = {"name", "age", "email"}
    if not required_keys.issubset(data.keys()):
        raise KeyError(f"Missing required keys: {required_keys - set(data.keys())}")

    return {
        "name": data["name"].upper(),
        "age": data["age"],
        "email": data["email"].lower()
    }


class Calculator:
    """Simple calculator class."""

    def __init__(self, initial_value: float = 0):
        """Initialize with an initial value."""
        self.value = initial_value

    def add(self, x: float) -> float:
        """Add a value and return the result."""
        self.value += x
        return self.value

    def subtract(self, x: float) -> float:
        """Subtract a value and return the result."""
        self.value -= x
        return self.value

    def multiply(self, x: float) -> float:
        """Multiply by a value and return the result."""
        self.value *= x
        return self.value

    def reset(self) -> None:
        """Reset the calculator to zero."""
        self.value = 0

    def get_value(self) -> float:
        """Get the current value."""
        return self.value
