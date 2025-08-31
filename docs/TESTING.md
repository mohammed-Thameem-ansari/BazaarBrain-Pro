# BazaarBrain-Pro Testing Guide

This document provides comprehensive testing instructions for all BazaarBrain agents and components.

## 🧪 Test Structure

```
tests/
├── test_reality_capture.py    # OCR and image processing tests
├── test_simulation_agent.py   # Business simulation tests
└── test_intake_agent.py      # Routing and classification tests (future)
```

## 🚀 Quick Start Testing

### 1. Run All Tests
```bash
cd tests
python -m unittest discover -v
```

### 2. Run Specific Test Files
```bash
# Test Reality Capture Agent
python test_reality_capture.py

# Test Simulation Agent  
python test_simulation_agent.py
```

### 3. Run Individual Test Classes
```bash
python -m unittest tests.test_reality_capture.TestRealityCaptureAgent -v
python -m unittest tests.test_simulation_agent.TestSimulationAgent -v
```

## 📋 Reality Capture Agent Tests

### Test Coverage
- **Agent Initialization**: Client setup, prompt loading
- **Image Preprocessing**: Resize, format conversion, error handling
- **JSON Parsing**: Response cleaning, markdown removal, validation
- **Arbitration Logic**: Dual LLM result comparison and merging
- **Mock Processing**: Simulated OCR with mocked LLM responses
- **Results Storage**: File I/O, data persistence
- **Statistics**: Processing metrics and success rates

### Running OCR Tests
```bash
cd tests
python test_reality_capture.py
```

### Expected Output
```
🧪 Running Reality Capture Agent Tests
==================================================
test_agent_initialization (__main__.TestRealityCaptureAgent) ... ok
test_prompt_loading (__main__.TestRealityCaptureAgent) ... ok
test_image_preprocessing (__main__.TestRealityCaptureAgent) ... ok
test_json_parsing (__main__.TestRealityCaptureAgent) ... ok
test_arbitration_logic (__main__.TestRealityCaptureAgent) ... ok
test_mock_processing (__main__.TestRealityCaptureAgent) ... ok
test_results_storage (__main__.TestRealityCaptureAgent) ... ok
test_processing_stats (__main__.TestRealityCaptureAgent) ... ok
test_convenience_function (__main__.TestRealityCaptureIntegration) ... ok
test_agent_imports (__main__.TestRealityCaptureIntegration) ... ok

✅ All tests passed!

📊 Test Summary:
   - Test file: test_reality_capture.py
   - Test classes: 2
   - Test methods: 8+
   - Coverage: OCR, Arbitration, Storage, Stats
```

## 📊 Simulation Agent Tests

### Test Coverage
- **Agent Initialization**: Client setup, prompt loading, sample data
- **Sample Data Validation**: Structure, types, logical constraints
- **JSON Parsing**: Response cleaning, markdown removal, validation
- **Arbitration Logic**: Dual LLM parsing result comparison
- **Fallback Parsing**: Basic keyword detection when LLMs fail
- **Mathematical Simulations**: Price changes, bulk orders, profit calculations
- **Mock Simulations**: Simulated queries with mocked LLM responses
- **Results Storage**: File I/O, data persistence
- **Statistics**: Simulation metrics and success rates

### Running Simulation Tests
```bash
cd tests
python test_simulation_agent.py
```

### Expected Output
```
🧪 Running Simulation Agent Tests
==================================================
test_agent_initialization (__main__.TestSimulationAgent) ... ok
test_prompt_loading (__main__.TestSimulationAgent) ... ok
test_sample_data_structure (__main__.TestSimulationAgent) ... ok
test_json_parsing (__main__.TestSimulationAgent) ... ok
test_arbitration_logic (__main__.TestSimulationAgent) ... ok
test_fallback_parsing (__main__.TestSimulationAgent) ... ok
test_price_increase_simulation (__main__.TestSimulationAgent) ... ok
test_price_decrease_simulation (__main__.TestSimulationAgent) ... ok
test_bulk_order_simulation (__main__.TestSimulationAgent) ... ok
test_unknown_scenario (__main__.TestSimulationAgent) ... ok
test_mock_simulation (__main__.TestSimulationAgent) ... ok
test_results_storage (__main__.TestSimulationAgent) ... ok
test_simulation_stats (__main__.TestSimulationAgent) ... ok
test_convenience_function (__main__.TestSimulationIntegration) ... ok
test_agent_imports (__main__.TestSimulationIntegration) ... ok
test_mathematical_accuracy (__main__.TestSimulationIntegration) ... ok

✅ All tests passed!

📊 Test Summary:
   - Test file: test_simulation_agent.py
   - Test classes: 2
   - Test methods: 12+
   - Coverage: Parsing, Arbitration, Math, Storage, Stats
```

## 🔧 Test Dependencies

### Required Packages
```bash
pip install pillow unittest-mock
```

### Optional Dependencies
```bash
pip install pytest pytest-cov  # For advanced testing
```

## 📁 Test Data

### Mock Images
- **Test Receipts**: Generated programmatically using PIL
- **Format**: JPEG, 400x300 pixels
- **Content**: Sample grocery store receipt with items, prices, totals

### Mock Business Data
- **Products**: Rice, Sugar, Wheat, Oil, Pulses
- **Data Fields**: Price, cost, sales volume, profit margin, units
- **Realistic Values**: Based on typical grocery store pricing

## 🎯 Test Scenarios

### Reality Capture Agent
1. **Image Processing**: Valid/invalid images, different formats
2. **OCR Accuracy**: Text extraction, number recognition
3. **Arbitration**: Conflicting LLM outputs, fallback scenarios
4. **Error Handling**: Network failures, invalid responses
5. **Data Storage**: Result persistence, file management

### Simulation Agent
1. **Query Parsing**: Natural language to structured parameters
2. **Mathematical Accuracy**: Price calculations, profit analysis
3. **Scenario Coverage**: Price changes, bulk orders, edge cases
4. **Data Validation**: Input constraints, logical consistency
5. **Performance**: Response times, memory usage

## 🚨 Common Test Issues

### Import Errors
```python
# If you get import errors, ensure the path is correct:
import sys
sys.path.append('..')
from agents.reality_capture_agent import RealityCaptureAgent
```

### Missing Dependencies
```bash
# Install required packages:
pip install pillow openai google-generativeai
```

### File Permission Errors
```bash
# Ensure write permissions for test directories:
chmod 755 tests/
chmod 644 tests/*.py
```

## 📈 Test Metrics

### Coverage Goals
- **Unit Tests**: 90%+ code coverage
- **Integration Tests**: All agent interactions
- **Edge Cases**: Error conditions, boundary values
- **Performance**: Response time benchmarks

### Success Criteria
- All tests pass without errors
- Mock data validates correctly
- Mathematical calculations are accurate
- File I/O operations succeed
- Error handling works as expected

## 🔮 Future Testing

### Planned Test Additions
- **Intake Agent Tests**: Routing logic, classification accuracy
- **End-to-End Tests**: Complete user workflows
- **Performance Tests**: Load testing, response times
- **Integration Tests**: Database connectivity, API endpoints

### Test Automation
- **CI/CD Integration**: GitHub Actions, automated testing
- **Coverage Reports**: HTML reports, trend analysis
- **Performance Monitoring**: Response time tracking
- **Regression Testing**: Automated comparison with baselines

## 📞 Test Support

### Getting Help
1. Check the test output for specific error messages
2. Verify all dependencies are installed
3. Ensure file paths and permissions are correct
4. Review the test code for configuration issues

### Debugging Tests
```python
# Add debug output to tests:
import logging
logging.basicConfig(level=logging.DEBUG)

# Use print statements for troubleshooting:
print(f"Debug: {variable_name}")
```

### Test Maintenance
- Update tests when agent interfaces change
- Add tests for new features
- Refactor tests for better maintainability
- Document test scenarios and expected outcomes

## 🚀 New: Deploy/E2E Test Scripts

These scripts live under `deploy/` to validate production-like setups:

- `deploy/smoke_test.py` — Quick health and basic API pings
- `deploy/test_docker_api.py` — API tests against a running Docker backend
- `deploy/test_backend_prod.py` — Backend health, transactions, and upload checks
- `deploy/test_integration.py` — Frontend↔Backend UI smoke via Playwright (optional)
- `deploy/test_auth.py` — Auth-protected endpoints with JWT
- `deploy/e2e_test.py` — End-to-end happy-path checks (health, transactions, upload, simulate)

Usage examples:

```bash
# Health and E2E (set E2E_JWT for auth flows)
API_BASE_URL=http://localhost:8000 python deploy/e2e_test.py

# Frontend/Backend UI checks (requires Playwright)
python -m pip install requests playwright && playwright install chromium
python deploy/test_integration.py --frontend http://localhost:3000 --backend http://localhost:8000 --token $JWT
```

## 🧪 CI Notes

- Backend CI: `.github/workflows/backend.yml` runs pytest and builds Docker image
- Frontend CI: `.github/workflows/frontend.yml` runs Jest tests and builds the app
