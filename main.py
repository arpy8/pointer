import time
import uvicorn
import subprocess
import pyautogui as pg
from pathlib import Path
from termcolor import colored
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse

app = FastAPI()
base_path = Path(__file__).parent
app.mount("/static", StaticFiles(directory=base_path / "static"), name="static")
secret_key = "1234"

@app.get("/favicon")
def get_favicon():
    return FileResponse(base_path / "static" / "cursor.png")

@app.get("/manifest.json")
def get_manifest():
    return FileResponse(base_path / "manifest.json")

@app.get("/", response_class=FileResponse)
async def read_root():
    return base_path / "index.html"

@app.get("/kbd", response_class=FileResponse)
async def read_root():
    return base_path / "keyboard.html"

@app.get("/press/{button}")
def press_key(button: str):
    if "-" in button:
        pg.hotkey(*button.split("-"))
    else:
        pg.press(button)
    return RedirectResponse(url="/", status_code=302)

@app.get("/exec/{command}")
def exec_command(command: str):
    def exec_shutdown():
        pg.hotkey("win", "m")
        time.sleep(0.2)
        pg.hotkey("alt", "f4")
        time.sleep(0.2)
        pg.press("enter")

    def exec_bsod():
        subprocess.run(
            ['bsod'],
            stdout=subprocess.PIPE,
            text=True
        )
        
    def exec_sleep():
        pg.hotkey("win", "m")
        time.sleep(0.2)
        
        pg.hotkey("alt", "f4")
        time.sleep(0.2)

        for _ in range(5):
            pg.press("down", interval=0.05)

        for _ in range(2):
            pg.press("up", interval=0.05)
            
        pg.press("enter")
        
    def exec_volume_up():
        for _ in range(10):
            pg.press("volumeup")

    def exec_volume_down():
        for _ in range(10):
            pg.press("volumedown")
        
    cmd_map = {
        "shutdown": exec_shutdown,
        "bsod": exec_bsod,
        "sleep": exec_sleep,
        "volume-up": exec_volume_up,
        "volume-down": exec_volume_down,
    }
    
    cmd_map[command]()
    
    return RedirectResponse(url="/", status_code=302)

if __name__ == "__main__":
    print(colored(
        [
            line for line in subprocess.run(
                ['ipconfig'],
                stdout=subprocess.PIPE,
                text=True
            ).stdout.splitlines() if "IPv4 Address" in line
        ][-1].strip(),
        "green"
    ), end="\n" * 3)

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=80,
        reload=True
    )