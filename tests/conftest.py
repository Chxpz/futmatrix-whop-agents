#!/usr/bin/env python3
"""
Pytest configuration and shared fixtures.
"""
import pytest
import asyncio
import logging
import os

# Set test environment variables
os.environ["DATABASE_TEST_MODE"] = "true"
os.environ["LOG_LEVEL"] = "INFO"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(autouse=True)
def setup_logging():
    """Setup logging for tests."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

@pytest.fixture(scope="function") 
def database():
    """Database fixture for testing."""
    from core.database import DatabaseManager
    
    test_config = {
        "url": "test://localhost",
        "test_mode": True
    }
    
    return DatabaseManager(test_config)
    
@pytest.fixture(scope="function")
async def cleanup_after_test():
    """Cleanup fixture that runs after each test."""
    yield
    # Any cleanup logic can go here
    await asyncio.sleep(0.1)  # Brief pause to allow cleanup