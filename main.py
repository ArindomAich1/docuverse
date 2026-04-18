from app.app import app
import os
from app.utils.logging_utils import setup_logging

setup_logging(
    log_level=os.getenv("LOG_LEVEL", "INFO"),
    log_to_file=os.getenv("LOG_TO_FILE", "false").lower() == "true"
)

def main():
    print("Hello from docuverse!")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
