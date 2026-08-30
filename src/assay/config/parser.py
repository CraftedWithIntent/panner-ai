"""YAML config parser for Assay test suites."""
from typing import Any, Dict, List, Literal, Optional
import yaml
from pydantic import BaseModel, ValidationError, field_validator


class AssertionSpec(BaseModel):
    """Assertion specification (frozen)."""
    type: Literal["regex", "status_code", "latency", "json_schema", "llm_judge"]
    expected: Any
    tolerance: Optional[float] = None
    weight: float = 1.0

    model_config = {"frozen": True}

    @field_validator("weight")
    @classmethod
    def validate_weight(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError("weight must be between 0.0 and 1.0")
        return v


class TestCaseSpec(BaseModel):
    """Test case specification (frozen)."""
    name: str
    payload: Dict[str, Any]
    assertions: List[AssertionSpec]
    timeout_ms: int = 5000

    model_config = {"frozen": True}

    @field_validator("timeout_ms")
    @classmethod
    def validate_timeout(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("timeout_ms must be positive")
        return v


class SuiteConfig(BaseModel):
    """Test suite configuration (frozen)."""
    name: str
    description: str
    agent_url: str
    test_cases: List[TestCaseSpec]
    baseline_file: Optional[str] = "baseline.json"

    model_config = {"frozen": True}

    @field_validator("agent_url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        if not v.startswith(("http://", "https://")):
            raise ValueError("agent_url must start with http:// or https://")
        return v

    @field_validator("test_cases")
    @classmethod
    def validate_test_cases(cls, v: List[TestCaseSpec]) -> List[TestCaseSpec]:
        if not v:\n            raise ValueError("test_cases must not be empty")
        return v


def parse_suite(yaml_path: str) -> SuiteConfig:
    """Parse YAML test suite file into immutable SuiteConfig."""
    try:
        with open(yaml_path, "r") as f:\n            data = yaml.safe_load(f)\n    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found: {yaml_path}")
    except yaml.YAMLError as e:\n        raise ValidationError(f"Invalid YAML: {e}")

    if not isinstance(data, dict):
        raise ValidationError("YAML root must be a dictionary")

    try:
        return SuiteConfig(**data)
    except ValidationError as e:\n        raise ValidationError(f"Config validation failed: {e}")
