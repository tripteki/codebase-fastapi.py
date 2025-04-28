from typing import Any
from fastapi import APIRouter, Depends
from fastapi_limiter.depends import RateLimiter
from pydantic import BaseModel, Field
from src.app.configs.app_config import AppConfig
from src.app.dtos.app_dto import Description
from src.app.dtos.app_response_dto import AppSuccessResponseDto
from src.app.services.app.health.service import AppHealthService

class VersionResponseDto (BaseModel):
    """
    VersionResponseDto
    """
    version: str = Field (..., json_schema_extra={"example": "string"})

class StatusResponseDto (BaseModel):
    """
    StatusResponseDto
    """
    status: Any = Field (..., json_schema_extra={"example": "string"})
    memory: Any = Field (None, json_schema_extra={"example": {}})
    database: Any = Field (..., json_schema_extra={"example": {}})
    cache: Any = Field (..., json_schema_extra={"example": {}})

appRouter = APIRouter (prefix="/api")

class AppController:
    """
    AppController
    """
    @staticmethod
    @appRouter.get (
        "/version",
        tags=["Stats"],
        dependencies=[Depends (RateLimiter (times=5, seconds=5))],
        response_model=AppSuccessResponseDto[VersionResponseDto],
        responses={
            200: {
                "description": Description.OK,
                "content": {
                    "application/json": {
                        "example": {
                            "status": 0,
                            "message": "string",
                            "data": {
                                "version": "string"
                            }
                        }
                    }
                }
            }
        }
    )
    async def version () -> AppSuccessResponseDto[VersionResponseDto]:
        """
        Show Version
        """
        appConfig = AppConfig.config ()
        return AppSuccessResponseDto (
            data=VersionResponseDto (version=appConfig.app_version)
        )

    @staticmethod
    @appRouter.get (
        "/status",
        tags=["Stats"],
        dependencies=[Depends (RateLimiter (times=10, seconds=5))],
        response_model=AppSuccessResponseDto[StatusResponseDto],
        responses={
            200: {
                "description": Description.OK,
                "content": {
                    "application/json": {
                        "example": {
                            "status": 0,
                            "message": "string",
                            "data": {
                                "status": "string",
                                "memory": {},
                                "database": {},
                                "cache": {}
                            }
                        }
                    }
                }
            }
        }
    )
    async def status () -> AppSuccessResponseDto[StatusResponseDto]:
        """
        Health Check Status
        """
        healthData = await AppHealthService.checkAll ()
        info = healthData.get ("info", {})
        memory_info = {}
        if "memory_allocation" in info:
            memory_info["memory_allocation"] = info.get ("memory_allocation")
        if "memory_total" in info:
            memory_info["memory_total"] = info.get ("memory_total")
        return AppSuccessResponseDto (
            data=StatusResponseDto (
                status=healthData.get ("status"),
                memory=memory_info if memory_info else None,
                database=info.get ("database"),
                cache=info.get ("cache")
            )
        )
