from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel
import uvicorn
import os
from dotenv import load_dotenv


load_dotenv()
IN_API_KEY = str(os.getenv('INCOMING_API_KEY'))
app = FastAPI()


def run_server():
    uvicorn.run(app, host="0.0.0.0", port=80)


class ClientData(BaseModel):
    client_id: str
    client_message: str


@app.post("/send_ai_response")
async def your_endpoint(request: Request, api: str = Header(None), client_data: ClientData = None):
    # Проверка заголовков
    if api != IN_API_KEY:
        raise HTTPException(
            status_code=400, detail="Неверные заголовки запроса")
    # Работа с данными клиента
    if client_data is not None:
        # Здесь можно обработать данные
        print(client_data.client_message)
        return {"client_id": client_data.client_id, "client_message": client_data.client_message}
    else:
        raise HTTPException(
            status_code=400, detail="Отсутствуют данные клиента")

if __name__ == "__main__":
    run_server()
