from typing import Literal
from pydantic import BaseModel, Field, IPvAnyNetwork, ConfigDict, field_validator


class HostRequirement(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    hosts: int = Field(gt=0, le=16_777_214)


class VLANRequirement(BaseModel):
    vlan_id: int = Field(ge=1, le=4094)
    name: str = Field(min_length=1, max_length=32)
    purpose: str = "General"


class NetworkScenario(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=100)
    profile: Literal["campus_lan", "metro_man", "global_wan", "custom"]
    sites: int = Field(ge=1, le=100)
    buildings: int = Field(ge=1, le=500)
    endpoints: int = Field(gt=0, le=1_000_000)
    max_link_distance_m: float = Field(ge=0, le=10_000_000)
    root_network: IPvAnyNetwork
    subnet_count: int = Field(ge=1, le=4094)
    required_bandwidth_mbps: int = Field(gt=0, le=10_000_000)
    multi_site: bool = False
    cloud_boundary: bool = False
    external_as_boundary: bool = False
    redundancy_required: bool = False
    latency_target_ms: float | None = Field(default=None, gt=0, le=10000)
    connectivity: str | None = None
    vpn_required: bool = False
    routing_domains: list[str] = Field(default_factory=list)
    vlan_requirements: list[VLANRequirement] = Field(default_factory=list)
    subnet_requirements: list[HostRequirement] = Field(default_factory=list)

    @field_validator("root_network")
    @classmethod
    def require_ipv4(cls, value):
        if value.version != 4:
            raise ValueError("Only IPv4 root networks are supported in this project.")
        return value
