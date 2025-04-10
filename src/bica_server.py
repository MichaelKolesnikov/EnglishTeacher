from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, TypeAdapter
from pydantic.tools import parse_obj_as
from server.virtual_tutor import VirtualTutor, DummyVirtualTutor
import uvicorn
import json
import argparse


# убираем кэширование файлов, а то плохо выходит
class StaticFilesWithoutCaching(StaticFiles):
    def is_not_modified(self, *args, **kwargs) -> bool:
        return False


class WssItem(BaseModel):
    type: str
    content: str
    timestamp: str


class PostItem(BaseModel):
    input: str | None = None
    direction: str | None = None


vt_list = {}

app = FastAPI()
with open("server/prompts/start_prompt.md") as f:
    start_prompt = f.read()

viz_vt = DummyVirtualTutor(236, start_prompt)


class VizItem(BaseModel):
    input_text: str


@app.get("/")
def process_root():
    return {"message": "Hello, world!!!"}


@app.post("/getAnswerDialog")
async def process_post_viz1(item: VizItem):
    viz_vt.logger_dialog.info(f"User (viz):{item.input_text}")
    answer = await viz_vt.generate_answer(item.input_text)
    viz_vt.logger_dialog.info(f"Tutor (viz): {answer}")
    return {"answer_text": answer,
            "emotion": 3}


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    @staticmethod
    async def send_personal_message(message: dict, websocket: WebSocket):
        await websocket.send_json(message)


manager = ConnectionManager()


@app.websocket("/test_1/wss/{client_id}")
async def websocket_endpoint_3(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        virtual_tutor = VirtualTutor(client_id, start_prompt)
        while True:
            data = await websocket.receive_text()
            data_dict = json.loads(data)
            data_model = TypeAdapter(WssItem).validate_python(data_dict)
            actor_replica = await virtual_tutor.generate_answer(data_model.content)
            data_model.content = actor_replica
            await manager.send_personal_message(data_model.model_dump(), websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.post("/test/{client_id}/getAnswer")
async def process_post(client_id: int, item: PostItem):
    if not client_id in vt_list.keys():
        vt_list[client_id] = VirtualTutor(client_id, start_prompt)
    # print(f"client id: {client_id} item: {item.input}")
    vt_list[client_id].logger_dialog.info(f"User (viz): {item.input}")
    print(f"item.input: {item.input}")
    print(f"type: {type(item.input)}")
    answer = await vt_list[client_id].generate_answer(item.input)
    vt_list[client_id].logger_dialog.info(f"Tutor (viz): {answer}")
    return {
        "Desk": "",
        "Reply": answer,
        "Direction": "player",
        "Happy": 1,
        "Sad": 0.1,
        "Surprise": 0.1,
        "Disgust": 0,
        "Angry": 0,
        "Afraid": 0
    }


app.mount("/test_1", StaticFilesWithoutCaching(directory="./ui_moral_1", html=True), name="static")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--local", action="store_true",
                        dest="local", help="запуск сервера локально")

    console_args = parser.parse_args()

    host_ip = "0.0.0.0"
    if console_args.local:
        host_ip = "127.0.0.1"

    uvicorn.run("bica_server:app", host=host_ip, port=7777, reload=True)


if __name__ == "__main__":
    main()
