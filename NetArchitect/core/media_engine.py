from dataclasses import dataclass
import math

class PhysicalDistanceViolationError(ValueError):
    """Copper explicitly requested beyond the 100 m assignment limit."""

@dataclass(frozen=True)
class MediaRecommendation:
    media: str
    transceiver: str
    distance_m: float
    rationale: str
    standard_reference: str

def select_media(distance_m: float) -> MediaRecommendation:
    if isinstance(distance_m, bool) or not isinstance(distance_m, (int, float)):
        raise TypeError("Distance must be a number in metres.")
    if not math.isfinite(float(distance_m)):
        raise ValueError("Distance must be a finite number of metres.")
    if distance_m < 0:
        raise ValueError("Distance cannot be negative.")
    if distance_m <= 100:
        return MediaRecommendation("Cat6a Copper", "10GBASE-T", float(distance_m),
            f"Cat6a copper is recommended because {distance_m:g} m is within the assignment's 100 m LAN-access limit.",
            "IEEE 802.3an (10GBASE-T)")
    if distance_m <= 400:
        return MediaRecommendation("OM4 Multimode Fiber", "10GBASE-SR", float(distance_m),
            f"OM4 multimode fiber is recommended because {distance_m:g} m exceeds the 100 m copper limit but is within the assignment's 101–400 m backbone band. 10GBASE-SR commonly uses 850 nm optics; verify OM4 reach, connector loss and optical budget.",
            "IEEE 802.3 (10GBASE-SR; 850 nm optics)")
    transceiver = "10GBASE-LR/ER" if distance_m <= 40000 else "OS2 + optical transport/regeneration"
    extra = (
        "For this distance, a single 10GBASE-LR/ER optic pair is not a direct-span solution; "
        "use a carrier/optical transport design with engineered regeneration/amplification and a verified end-to-end loss budget."
        if distance_m > 40000 else
        "Select 10GBASE-LR/ER optics for actual reach (typically 1310 nm LR / 1550 nm ER families) and verify transmitter/receiver compatibility and optical budget."
    )
    return MediaRecommendation("OS2 Single-Mode Fiber", transceiver, float(distance_m),
        f"OS2 single-mode fiber is recommended because {distance_m:g} m exceeds the assignment's 400 m OM4 band. {extra}",
        "IEEE 802.3 (10GBASE-LR/ER; transport engineering required beyond optic reach)")

def validate_copper_request(distance_m: float) -> None:
    if isinstance(distance_m, bool) or not isinstance(distance_m, (int, float)):
        raise TypeError("Distance must be a number in metres.")
    if not math.isfinite(float(distance_m)):
        raise ValueError("Distance must be a finite number of metres.")
    if distance_m < 0:
        raise ValueError("Distance cannot be negative.")
    if distance_m > 100:
        raise PhysicalDistanceViolationError(
            f"Copper request is {distance_m:g} m; Cat6a limit is 100 m. "
            "Physical distance/signal attenuation violation: use an appropriate fiber design.")
