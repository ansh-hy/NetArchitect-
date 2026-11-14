import pytest
from core.media_engine import select_media, validate_copper_request, PhysicalDistanceViolationError

@pytest.mark.parametrize("distance,expected", [
    (0,"Cat6a Copper"), (50,"Cat6a Copper"), (100,"Cat6a Copper"),
    (101,"OM4 Multimode Fiber"), (250,"OM4 Multimode Fiber"),
    (400,"OM4 Multimode Fiber"), (400.01,"OS2 Single-Mode Fiber"),
    (22000,"OS2 Single-Mode Fiber")])
def test_distance_bands(distance, expected):
    assert select_media(distance).media == expected

@pytest.mark.parametrize("distance", [-1,-0.01])
def test_negative_distance_rejected(distance):
    with pytest.raises(ValueError): select_media(distance)

def test_non_numeric_distance_rejected():
    with pytest.raises(TypeError): select_media("100")

def test_copper_exactly_100m_allowed():
    assert validate_copper_request(100) is None

@pytest.mark.parametrize("distance", [100.01,150,400,1000])
def test_copper_over_100m_rejected(distance):
    with pytest.raises(PhysicalDistanceViolationError): validate_copper_request(distance)

def test_rationale_uses_actual_distance():
    assert "250 m" in select_media(250).rationale
