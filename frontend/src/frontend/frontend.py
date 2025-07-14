from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
import requests
from models.user_info import UserInfo
from models.confirm_game import ConfirmGame
from config.constants import API_BASE_URL
from typing import *

app = FastAPI()
BASE_DIR = os.path.dirname(__file__)
# MIDDLEWARE PER LA GESTIONE DEI FILE STATICI
templates = Jinja2Templates(directory= os.path.join(BASE_DIR, "../public/templates"))

app.mount("/assets", StaticFiles(directory= os.path.join(BASE_DIR, "../public/assets")))
app.mount("/css", StaticFiles(directory= os.path.join(BASE_DIR, "../public/css")))
app.mount("/js", StaticFiles(directory= os.path.join(BASE_DIR, "../public/js")))

@app.get("/")
def get_home_page(request: Request):
    return templates.TemplateResponse(
        "home.html", {"request": request}
    )

@app.get("/login")
def get_login_page(request: Request):
    return templates.TemplateResponse(
        "login.html", {"request": request}
    )

@app.get("/register")
def get_register_page(request: Request):
    return templates.TemplateResponse(
        "register.html", {"request": request}
    )

# start_game.html, contiene la schermata con AVVIA PARTITA GIUDICE PARTECIPANTE
@app.get("/start-game")
def get_start_game_page(request: Request):
    return templates.TemplateResponse(
        "start_game.html", {"request": request}
    )

# Endpoint per gestire l'avvio effettivo della partita classica
@app.post("/start-classic-game")
def start_game(payload: UserInfo, request: Request):
    try:
        response = requests.post(os.path.join(API_BASE_URL, "/start-game-api"), json= payload.model_dump())
        response.raise_for_status()
    except requests.RequestException as e:
        error_data: Dict = response.json()
        raise HTTPException(
            status_code= error_data.get("status_code", 500),
            detail= error_data.get("detail", "Errore sconosciuto")
        )
    response_data = ConfirmGame.model_validate(response.json())

    # DA MODIFICARE PERCHE NON DOBBIAMO METTERE CHE RESTITUISCE IL TEMPLATE, MA SOLO IL GAME ID, IN QUANTO 
    # SUCCESSIVAMENTE IL CLIENT FARA' UNA GET ALLA PARTITA 
    if response_data.player_role == "judge":
        return templates.TemplateResponse(
            "judge_game.html", {
                "request": request,  
                "game_id": response_data.game_id, 
                "player_id": response_data.player_id, 
                "player_name": response_data.player_name}
        )
    else:
        return templates.TemplateResponse(
            "participant_game.html", {
                "request": request,  
                "game_id": response_data.game_id, 
                "player_id": response_data.player_id, 
                "player_name": response_data.player_name}
        )





