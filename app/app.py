from app.routing import document_router
import app.routing.file_upload_router
from app.exceptions.handler import app_exception_handler, unhandled_exception_handler
from app.exceptions.base_exception import AppException
import app.routing.otp_router
from fastapi import FastAPI
from app.routing import hello_router, user_router, otp_router, file_upload_router, chat_router


app = FastAPI()

app.include_router(hello_router.router)
app.include_router(user_router.router)
app.include_router(otp_router.router)
app.include_router(file_upload_router.router)
app.include_router(document_router.router)
app.include_router(chat_router.router)


app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

