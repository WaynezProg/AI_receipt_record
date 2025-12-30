import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings
    應用程式設定
    """

    # Azure Computer Vision API settings / Azure Computer Vision API設定
    azure_vision_endpoint: str = ""
    azure_vision_key: str = ""

    # Claude API settings / Claude API設定
    claude_api_key: str = ""

    # Application settings / 應用程式設定
    debug: bool = True
    log_level: str = "INFO"

    # File path settings / 檔案路徑設定
    upload_dir: str = "./data/receipts"
    output_dir: str = "./data/output"

    # Service settings / 服務設定
    max_file_size: int = 10485760  # 10MB
    allowed_extensions: str = "jpg,jpeg,png,pdf"

    @property
    def allowed_extensions_list(self) -> List[str]:
        """
        Get list of allowed file extensions
        獲取允許的檔案擴展名列表
        """
        return [ext.strip() for ext in self.allowed_extensions.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance / 全域設定實例
settings = Settings()


def get_settings() -> Settings:
    """
    Get settings instance
    獲取設定實例
    """
    return settings
