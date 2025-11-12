"""Tests for main API endpoints"""

import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_root() -> None:
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Senda API - Conversational AI Platform"
    }


def test_health() -> None:
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
