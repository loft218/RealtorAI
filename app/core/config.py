from dotenv import load_dotenv
import os

load_dotenv()


class Settings:
    # LLM相关配置
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY")
    DEEPSEEK_API_URL: str = os.getenv("DEEPSEEK_API_URL")

    # 数据库配置
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "password")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_NAME: str = os.getenv("DB_NAME", "realtor")

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    # 默认评分权重（可从 .env 或写死）
    DEFAULT_WEIGHTS: dict = {
        "base_score": 0.1,
        "living_score": 0.1,
        "traffic_score": 0.4,
        "school_score": 0.1,
        "hospital_score": 0.1,
        "park_score": 0.1,
        "restaurant_score": 0.1,
    }


settings = Settings()
