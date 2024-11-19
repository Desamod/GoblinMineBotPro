from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

    API_ID: int
    API_HASH: str

    SLEEP_TIME: list[int] = [1800, 2400]
    START_DELAY: list[int] = [5, 25]
    AUTO_MINING: bool = True
    AUTO_BUY_MINE: bool = True
    AUTO_UPGRADE: bool = True
    UPGRADE_MINE: bool = True
    UPGRADE_MINERS: bool = True
    UPGRADE_INVENTORY: bool = True
    UPGRADE_CART: bool = True
    MAX_CART_LEVEL: int = 2
    EXPEDITIONS: bool = True
    CUSTOM_EXPEDITION_COST: int = 1000000
    MIN_EXP_DURATION: int = 360
    AUTO_TASK: bool = True
    JOIN_TG_CHANNELS: bool = True
    AUTO_SPIN: bool = True
    NIGHT_SLEEP: bool = True
    NIGHT_SLEEP_START_TIME: list[int] = [2, 3]
    NIGHT_SLEEP_END_TIME: list[int] = [5, 7]
    REF_ID: str = '7253650410'
    DISABLED_TASKS: list[str] = [
        'Пригласить 10 друзей',
        'Пригласить 5 друзей',
        'Пригласить друга',
        'Поставь реакцию на пост'
    ]


settings = Settings()
