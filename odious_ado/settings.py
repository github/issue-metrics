# -*- coding: utf-8 -*-
import os
from functools import lru_cache
from typing import Dict, List
import uuid

from dotenv import load_dotenv
from pydantic import BaseModel, BaseSettings
from pydantic.fields import Field

from odious_ado import __name__ as app_name
from odious_ado import __version__ as app_version


class BaseConfig(BaseSettings):
    APP_NAME: str = app_name
    APP_ROOT: str = os.path.realpath(
        os.path.join(
            os.path.dirname(os.path.dirname(os.path.realpath(__file__))), os.pardir
        )
    )

    PROJECT_ROOT: str = os.path.realpath(os.path.join(APP_ROOT, os.pardir))
    VERSION: str = app_version

    ENVIRONMENT: str = "local"

    # AWS configuration
    # Force load dotenv to use role arn, client id, user pool id for cognito app client.
    load_dotenv()

    # pyroscope
    PYROSCOPE_SERVER_ADDRESS: str = os.getenv("PYROSCOPE_HOST", "http://localhost:4040")
    PYROSCOPE_TAGS: dict = {"region": f'{os.getenv("REGION", "localhost")}'}

    # Github Settings
    GITHUB_ACCESS_TOKEN: str = Field(..., env='OA_GITHUB_ACCESS_TOKEN')

    # Azure Settings
    ADO_PAT: str = os.getenv("OA_ADO_PAT")
    ADO_ORG_ID: str = os.getenv("OA_ADO_ORG_ID", "")
    ADO_FQDN: str = f"https://dev.azure.com"
    ADO_ORGANIZATION_URL: str = f"{ADO_FQDN}/{ADO_ORG_ID}"

    # pydantic configuration
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @classmethod
    @lru_cache()
    def get_settings(cls, **overrides):
        # TODO: override settings that are passed and look up env vars to override values
        return cls(**overrides)

