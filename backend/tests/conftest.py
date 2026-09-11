"""
GrowFlow — root test configuration.

Gate 01: structural foundation only.
No product test fixtures are defined here yet.
Those are established in Gate 02+ as each layer is implemented.

Test categories (markers):
    unit        — pure unit tests, no external dependencies
    integration — database / external service tests
    api         — HTTP/API-level tests via TestClient
    e2e         — full end-to-end workflow tests
    slow        — long-running tests

Marker usage:
    pytest -m unit
    pytest -m "not e2e"
    pytest -m "integration and not slow"
"""

# Fixtures and shared test configuration will be added in Gate 02+
# as application components are established.
