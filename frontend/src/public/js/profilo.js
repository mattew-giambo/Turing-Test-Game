const start_game_btn = document.getElementById("start-game-btn");
const url = new URL(start_game_btn.href);

const token = new URLSearchParams(window.location.search).get("token");

url.searchParams.set("token", token);

start_game_btn.href = url.toString();