from aiogram import Router

from my_app.bot.handlers.middleware.auth import AuthMiddleware

router = Router()
router.message.middleware(AuthMiddleware())
