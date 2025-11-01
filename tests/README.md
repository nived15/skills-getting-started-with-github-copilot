# Test Suite for Mergington High School Activities API

This directory contains comprehensive tests for the FastAPI application that manages student activities registration.

## Test Files

### `test_api.py`
Main API endpoint tests covering:
- **Root endpoint**: Redirect functionality
- **GET /activities**: Activity retrieval
- **POST /activities/{name}/signup**: Student registration
- **DELETE /activities/{name}/unregister**: Student unregistration
- **Integration scenarios**: Complex workflows
- **Edge cases**: Special characters, error conditions

### `test_data_validation.py`
Data structure and validation tests:
- **Data structure validation**: Required fields, data types
- **Email format validation**: Consistent email formats
- **Capacity constraints**: Maximum participant limits
- **Default data integrity**: Expected activities present

### `test_performance.py`
Performance and load testing:
- **Response time tests**: API performance benchmarks
- **Concurrent request handling**: Multiple simultaneous requests
- **Load scenarios**: Sequential request handling
- **Stress testing**: Capacity limits and large datasets

### `conftest.py`
Test configuration and fixtures:
- **Test client setup**: FastAPI TestClient configuration
- **Data reset fixtures**: Clean state for each test
- **Sample data fixtures**: Test data generation

## Running Tests

### Basic Test Run
```bash
# Run all tests
python -m pytest tests/

# Run with verbose output
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_api.py -v
```

### Coverage Reports
```bash
# Run tests with coverage
python -m pytest tests/ --cov=src

# Generate HTML coverage report
python -m pytest tests/ --cov=src --cov-report=html

# Coverage with missing lines
python -m pytest tests/ --cov=src --cov-report=term-missing
```

### Test Categories
```bash
# Run only API tests
python -m pytest tests/test_api.py

# Run only data validation tests
python -m pytest tests/test_data_validation.py

# Run only performance tests
python -m pytest tests/test_performance.py
```

## Test Coverage

The test suite achieves **100% code coverage** of the FastAPI application, covering:

- ✅ All API endpoints (`GET`, `POST`, `DELETE`)
- ✅ All error conditions (404, 400, 422)
- ✅ Data validation and constraints
- ✅ Edge cases and special characters
- ✅ Integration workflows
- ✅ Performance and load scenarios

## Test Data

Tests use isolated data that resets between test runs to ensure:
- **Clean state**: Each test starts with consistent data
- **No interference**: Tests don't affect each other
- **Predictable results**: Deterministic test outcomes

## Dependencies

The following testing dependencies are required:
- `pytest`: Test framework
- `pytest-asyncio`: Async test support
- `pytest-cov`: Coverage reporting
- `httpx`: HTTP client for FastAPI testing

Install with:
```bash
pip install -r requirements.txt
```