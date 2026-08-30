import os
import tempfile

import pytest

from assay.config.parser import ConfigParseError, SuiteConfig, parse_suite
from assay.domain.types import AssertionType


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
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(valid_yaml_content)
        f.flush()  # Ensure data is written to disk
        fname = f.name
        yield fname
    os.unlink(fname)


class TestParseValidYAML:
    """Test parsing valid YAML configurations."""

    def test_parse_valid_suite(self, temp_yaml):
        """Parse valid suite -> SuiteConfig."""
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
        assert tc.timeout_ms == 5000

    def test_parse_assertions(self, temp_yaml):
        """Verify assertions are parsed correctly."""
        config = parse_suite(temp_yaml)
        assertions = config.test_cases[0].assertions
        assert assertions[0].type == AssertionType.REGEX
        assert assertions[0].expected == "4"
        assert assertions[1].type == AssertionType.LATENCY
        assert assertions[1].expected == 100
        assert assertions[1].tolerance == 50

    def test_config_is_frozen(self, temp_yaml):
        """Verify SuiteConfig is immutable."""
        config = parse_suite(temp_yaml)
        import pytest as pytest_lib
        with pytest_lib.raises(AttributeError):
            config.name = "modified"

    def test_test_case_is_frozen(self, temp_yaml):
        """Verify TestCaseSpec is immutable."""
        config = parse_suite(temp_yaml)
        import pytest as pytest_lib
        with pytest_lib.raises(AttributeError):
            config.test_cases[0].name = "modified"

    def test_assertion_is_frozen(self, temp_yaml):
        """Verify AssertionSpec is immutable."""
        config = parse_suite(temp_yaml)
        import pytest as pytest_lib
        with pytest_lib.raises(AttributeError):
            config.test_cases[0].assertions[0].type = AssertionType.STATUS_CODE


class TestParseValidation:
    """Test validation rules."""

    def test_empty_test_cases(self):
        """Empty test_cases list -> ValidationError."""
        yaml_str = "name: test\ndescription: test\nagent_url: http://localhost:8000\ntest_cases: []\n"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_str)
            temp_file = f.name
        try:
            with pytest.raises(ConfigParseError):
                parse_suite(temp_file)
        finally:
            os.unlink(temp_file)

    def test_invalid_url(self):
        """Invalid URL -> ValidationError."""
        yaml_str = "name: test\ndescription: test\nagent_url: not-a-url\ntest_cases:\n  - name: test\n    payload: {}\n    assertions:\n      - type: regex\n        expected: test\n"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_str)
            temp_file = f.name
        try:
            with pytest.raises(ConfigParseError):
                parse_suite(temp_file)
        finally:
            os.unlink(temp_file)

    def test_invalid_timeout(self):
        """Invalid timeout_ms -> ValidationError."""
        yaml_str = "name: test\ndescription: test\nagent_url: http://localhost:8000\ntest_cases:\n  - name: test\n    payload: {}\n    timeout_ms: -1\n    assertions:\n      - type: regex\n        expected: test\n"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_str)
            temp_file = f.name
        try:
            with pytest.raises(ConfigParseError):
                parse_suite(temp_file)
        finally:
            os.unlink(temp_file)

    def test_invalid_weight(self):
        """Invalid assertion weight -> ValidationError."""
        yaml_str = "name: test\ndescription: test\nagent_url: http://localhost:8000\ntest_cases:\n  - name: test\n    payload: {}\n    assertions:\n      - type: regex\n        expected: test\n        weight: 1.5\n"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_str)
            temp_file = f.name
        try:
            with pytest.raises(ConfigParseError):
                parse_suite(temp_file)
        finally:
            os.unlink(temp_file)


class TestParseFileHandling:
    """Test file handling."""

    def test_file_not_found(self):
        """Missing file -> FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            parse_suite("/nonexistent/file.yaml")

    def test_malformed_yaml(self):
        """Malformed YAML -> ValidationError."""
        yaml_str = "invalid: yaml: structure: ["
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_str)
            temp_file = f.name
        try:
            with pytest.raises(ConfigParseError):
                parse_suite(temp_file)
        finally:
            os.unlink(temp_file)


class TestParseEdgeCases:
    """Test edge cases."""

    def test_custom_timeout(self):
        """Custom timeout_ms is preserved."""
        yaml_str = "name: test\ndescription: test\nagent_url: http://localhost:8000\ntest_cases:\n  - name: test\n    payload: {q: 1}\n    timeout_ms: 10000\n    assertions:\n      - type: regex\n        expected: test\n"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_str)
            temp_file = f.name
        try:
            config = parse_suite(temp_file)
            assert config.test_cases[0].timeout_ms == 10000
        finally:
            os.unlink(temp_file)

    def test_all_assertion_types(self):
        """All assertion types parse correctly."""
        yaml_str = "name: test\ndescription: test\nagent_url: http://localhost:8000\ntest_cases:\n  - name: test\n    payload: {q: 1}\n    assertions:\n      - type: regex\n        expected: pattern\n      - type: status_code\n        expected: 200\n      - type: latency\n        expected: 100\n        tolerance: 10\n      - type: json_schema\n        expected: {type: object}\n      - type: llm_judge\n        expected: correct response\n"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_str)
            temp_file = f.name
        try:
            config = parse_suite(temp_file)
            assertions = config.test_cases[0].assertions
            types = [a.type for a in assertions]
            assert types == [
                AssertionType.REGEX,
                AssertionType.STATUS_CODE,
                AssertionType.LATENCY,
                AssertionType.JSON_SCHEMA,
                AssertionType.LLM_JUDGE,
            ]
        finally:
            os.unlink(temp_file)

    def test_https_url(self):
        """HTTPS URLs are valid."""
        yaml_str = "name: test\ndescription: test\nagent_url: https://api.example.com/agent\ntest_cases:\n  - name: test\n    payload: {}\n    assertions:\n      - type: regex\n        expected: test\n"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_str)
            temp_file = f.name
        try:
            config = parse_suite(temp_file)
            assert config.agent_url == "https://api.example.com/agent"
        finally:
            os.unlink(temp_file)


class TestDeterminism:
    """Test determinism (same input -> same output)."""

    def test_parse_determinism_100x(self, temp_yaml):
        """Parsing same file 100 times produces identical results."""
        configs = [parse_suite(temp_yaml) for _ in range(100)]
        reference = configs[0]
        for config in configs[1:]:
            assert config.name == reference.name
            assert config.agent_url == reference.agent_url
            assert len(config.test_cases) == len(reference.test_cases)
            for tc1, tc2 in zip(config.test_cases, reference.test_cases):
                assert tc1.name == tc2.name
                assert tc1.payload == tc2.payload
                assert len(tc1.assertions) == len(tc2.assertions)
