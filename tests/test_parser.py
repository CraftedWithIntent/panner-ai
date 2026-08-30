"""Tests for config parser."""
import pytest
import tempfile
import os
from pydantic import ValidationError
from assay.config.parser import parse_suite, SuiteConfig, TestCaseSpec, AssertionSpec


@pytest.fixture
def valid_yaml_content():
    """Valid test suite YAML."""
    return """name: demo-suite
description: "Demo test suite for parser validation"
agent_url: http://localhost:8000/api/agent
test_cases:
  - name: "arithmetic query"
    payload: {query: "What is 2+2?"}
    assertions:
      - type: regex
        expected: "4"
      - type: latency
        expected: 100
        tolerance: 50
      - type: llm_judge
        expected: "response demonstrates mathematical correctness"
  - name: "json response"
    payload: {format: "json"}
    assertions:
      - type: json_schema
        expected: {type: "object", properties: {result: {type: "number"}}}
baseline_file: baseline.json
"""


@pytest.fixture
def temp_yaml(valid_yaml_content):
    """Create temporary YAML file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:\n        f.write(valid_yaml_content)\n        yield f.name\n    os.unlink(f.name)\n\n\nclass TestParseValidYAML:
    """Test parsing valid YAML configurations."""

    def test_parse_valid_suite(self, temp_yaml):
        """Parse valid suite → SuiteConfig."""
        config = parse_suite(temp_yaml)
        assert isinstance(config, SuiteConfig)
        assert config.name == "demo-suite"
        assert config.agent_url == "http://localhost:8000/api/agent"
        assert len(config.test_cases) == 2
        assert config.baseline_file == "baseline.json"

    def test_parse_test_cases(self, temp_yaml):
        """Verify test cases are parsed correctly."""
        config = parse_suite(temp_yaml)
        tc = config.test_cases[0]
        assert tc.name == "arithmetic query"
        assert tc.payload == {"query": "What is 2+2?"}
        assert len(tc.assertions) == 3
        assert tc.timeout_ms == 5000  # default

    def test_parse_assertions(self, temp_yaml):
        """Verify assertions are parsed correctly."""
        config = parse_suite(temp_yaml)
        assertions = config.test_cases[0].assertions
        assert assertions[0].type == "regex"
        assert assertions[0].expected == "4"
        assert assertions[1].type == "latency"
        assert assertions[1].expected == 100
        assert assertions[1].tolerance == 50

    def test_config_is_frozen(self, temp_yaml):
        """Verify SuiteConfig is immutable."""
        config = parse_suite(temp_yaml)
        with pytest.raises(Exception):
            config.name = "modified"

    def test_test_case_is_frozen(self, temp_yaml):
        """Verify TestCaseSpec is immutable."""
        config = parse_suite(temp_yaml)
        with pytest.raises(Exception):
            config.test_cases[0].name = "modified"

    def test_assertion_is_frozen(self, temp_yaml):
        """Verify AssertionSpec is immutable."""
        config = parse_suite(temp_yaml)
        with pytest.raises(Exception):
            config.test_cases[0].assertions[0].type = "modified"


class TestParseValidation:
    """Test validation rules."""

    def test_empty_test_cases(self):
        """Empty test_cases list → ValidationError."""
        yaml_str = """name: test
description: test
agent_url: http://localhost:8000
test_cases: []
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:\n            f.write(yaml_str)\n            temp_file = f.name\n\n        try:
            with pytest.raises(ValidationError):
                parse_suite(temp_file)
        finally:
            os.unlink(temp_file)

    def test_invalid_url(self):
        """Invalid URL → ValidationError."""
        yaml_str = """name: test
description: test
agent_url: not-a-url
test_cases:
  - name: test
    payload: {}
    assertions:
      - type: regex
        expected: "test"
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:\n            f.write(yaml_str)\n            temp_file = f.name\n\n        try:
            with pytest.raises(ValidationError):
                parse_suite(temp_file)
        finally:
            os.unlink(temp_file)

    def test_invalid_timeout(self):
        """Invalid timeout_ms → ValidationError."""
        yaml_str = """name: test
description: test
agent_url: http://localhost:8000
test_cases:
  - name: test
    payload: {}
    timeout_ms: -1
    assertions:
      - type: regex
        expected: "test"
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:\n            f.write(yaml_str)\n            temp_file = f.name\n\n        try:
            with pytest.raises(ValidationError):
                parse_suite(temp_file)
        finally:
            os.unlink(temp_file)

    def test_invalid_weight(self):
        """Invalid assertion weight → ValidationError."""
        yaml_str = """name: test
description: test
agent_url: http://localhost:8000
test_cases:
  - name: test
    payload: {}
    assertions:
      - type: regex
        expected: "test"
        weight: 1.5
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:\n            f.write(yaml_str)\n            temp_file = f.name\n\n        try:
            with pytest.raises(ValidationError):
                parse_suite(temp_file)
        finally:
            os.unlink(temp_file)


class TestParseFileHandling:
    """Test file handling."""

    def test_file_not_found(self):
        """Missing file → FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            parse_suite("/nonexistent/file.yaml")

    def test_malformed_yaml(self):
        """Malformed YAML → ValidationError."""
        yaml_str = "invalid: yaml: structure: ["
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:\n            f.write(yaml_str)\n            temp_file = f.name\n\n        try:
            with pytest.raises(ValidationError):
                parse_suite(temp_file)
        finally:
            os.unlink(temp_file)


class TestParseEdgeCases:
    """Test edge cases."""

    def test_custom_timeout(self):
        """Custom timeout_ms is preserved."""
        yaml_str = """name: test
description: test
agent_url: http://localhost:8000
test_cases:
  - name: test
    payload: {q: 1}
    timeout_ms: 10000
    assertions:
      - type: regex
        expected: "test"
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:\n            f.write(yaml_str)\n            temp_file = f.name\n\n        try:
            config = parse_suite(temp_file)
            assert config.test_cases[0].timeout_ms == 10000
        finally:
            os.unlink(temp_file)

    def test_all_assertion_types(self):
        """All assertion types parse correctly."""
        yaml_str = """name: test
description: test
agent_url: http://localhost:8000
test_cases:
  - name: test
    payload: {q: 1}
    assertions:
      - type: regex
        expected: "pattern"
      - type: status_code
        expected: 200
      - type: latency
        expected: 100
        tolerance: 10
      - type: json_schema
        expected: {type: "object"}
      - type: llm_judge
        expected: "correct response"
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:\n            f.write(yaml_str)\n            temp_file = f.name\n\n        try:
            config = parse_suite(temp_file)
            assertions = config.test_cases[0].assertions
            types = [a.type for a in assertions]
            assert types == ["regex", "status_code", "latency", "json_schema", "llm_judge"]
        finally:
            os.unlink(temp_file)

    def test_https_url(self):
        """HTTPS URLs are valid."""
        yaml_str = """name: test
description: test
agent_url: https://api.example.com/agent
test_cases:
  - name: test
    payload: {}
    assertions:
      - type: regex
        expected: "test"
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:\n            f.write(yaml_str)\n            temp_file = f.name\n\n        try:
            config = parse_suite(temp_file)
            assert config.agent_url == "https://api.example.com/agent"
        finally:
            os.unlink(temp_file)


class TestDeterminism:
    """Test determinism (same input → same output)."""

    def test_parse_determinism(self, temp_yaml):
        """Parsing same file produces identical results."""
        config1 = parse_suite(temp_yaml)
        config2 = parse_suite(temp_yaml)

        assert config1.name == config2.name
        assert config1.agent_url == config2.agent_url
        assert len(config1.test_cases) == len(config2.test_cases)
        for tc1, tc2 in zip(config1.test_cases, config2.test_cases):
            assert tc1.name == tc2.name
            assert tc1.payload == tc2.payload
