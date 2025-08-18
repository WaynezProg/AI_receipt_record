import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_read_main():
    """測試根端點"""
    response = client.get("/")
    assert response.status_code == 200


def test_health_check():
    """測試健康檢查端點"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "services" in data


def test_api_docs():
    """測試API文檔端點"""
    response = client.get("/docs")
    assert response.status_code == 200


def test_summary_endpoint():
    """測試摘要端點"""
    response = client.get("/summary")
    assert response.status_code == 200
    data = response.json()
    assert "uploaded_receipts" in data
    assert "processed_csv_files" in data
    assert "system_status" in data


def test_receipts_endpoint():
    """測試收據列表端點"""
    response = client.get("/receipts")
    assert response.status_code == 200
    data = response.json()
    assert "receipts" in data
    assert "total_count" in data
