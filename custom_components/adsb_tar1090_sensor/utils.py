"""Provide generic utility functions."""

def generate_entity_id(domain: str, entity_name: str) -> str:
    """Generate a unique entity ID."""
    return f"{domain}_{entity_name.lower().replace(' ', '_')}"
