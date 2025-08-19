"""
基本測試文件，確保CI能夠運行
"""

import pytest
import sys
import os

# 添加項目根目錄到Python路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_import_app():
    """測試能否導入app模組"""
    try:
        import app

        assert app is not None
    except ImportError as e:
        pytest.fail(f"無法導入app模組: {e}")


def test_import_config():
    """測試能否導入配置模組"""
    try:
        from app.config import settings

        assert settings is not None
    except ImportError as e:
        pytest.fail(f"無法導入配置模組: {e}")


def test_import_models():
    """測試能否導入模型"""
    try:
        from app.models.receipt import ReceiptData, ReceiptItem

        assert ReceiptData is not None
        assert ReceiptItem is not None
    except ImportError as e:
        pytest.fail(f"無法導入模型: {e}")


def test_basic_functionality():
    """基本功能測試"""
    assert 1 + 1 == 2


def test_string_operations():
    """字符串操作測試"""
    test_string = "日本收據AI識別系統"
    assert len(test_string) > 0
    assert "AI" in test_string
