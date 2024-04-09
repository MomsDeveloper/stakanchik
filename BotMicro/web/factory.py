from contextlib import asynccontextmanager
from os import getenv

from aiogram import Bot, Dispatcher
from deta import Deta
from fastapi import FastAPI

from web.routers import root_router
from web.stubs import BotStub, DispatcherStub, SecretStub


def create_app(deta: Deta, bot: Bot, dispatcher: Dispatcher) -> FastAPI:
    webhook_secret = getenv('DETA_SPACE_APP_HOSTNAME', '').split('.')[0]

    app = FastAPI(title='Bot')
    app.dependency_overrides.update({
        BotStub: lambda: bot,
        DispatcherStub: lambda: dispatcher,
        SecretStub: lambda: webhook_secret,
    })

    app.include_router(root_router)
    return app
