
def snake_to_camel(snake_str: str) -> str:
    """Convert a snake_case string to camelCase."""
    parts = snake_str.split('_')
    return parts[0] + ''.join(word.capitalize() for word in parts[1:])


def snake_to_upper_camel(snake_str: str) -> str:
    """Convert a snake_case string to UpperCamelCase."""
    parts = snake_str.split('_')
    return ''.join(word.capitalize() for word in parts)
