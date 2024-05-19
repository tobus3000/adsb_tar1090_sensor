"""Provide generic utility functions."""

def generate_entity_id(domain: str, integration_name: str, entity_name: str) -> str:
    """Generate a unique entity ID."""
    integration = integration_name.lower().replace(' ','_')
    entity = entity_name.lower().replace(' ', '_')
    return f"{domain}_{integration}_{entity}"
