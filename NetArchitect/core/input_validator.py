from core.models import NetworkScenario


def validate_scenario(data: dict) -> NetworkScenario:
    """Validate raw preset/custom input and return a typed scenario."""
    return NetworkScenario.model_validate(data)
