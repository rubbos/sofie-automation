def reorder_name(name: str) -> str:
    try:
        lastnames, initial = name.split(", ")
        return f"{initial} {lastnames}"
    except ValueError:
        raise ValueError("Invalid name format.")
