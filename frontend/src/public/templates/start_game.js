const profilo_stats = document.getElementById("profilo_stats");
const url = new URL(profilo_stats.href);

const params = new URLSearchParams(window.location.search);
const token = params.get("token");

url.searchParams.set("token", token);
profilo_stats.href = url.toString();

const user_id = window.location.pathname.split("/")[2];

const judge_btn = document.getElementById("judge_btn");
const part_btn = document.getElementById("part_btn");

const generic_game = document.getElementById("generic_game");
const judge_game = document.getElementById("judge_game");

const classic_mod = document.getElementById("classic_mod");
const verdict_mod = document.getElementById("verdict_mod");

judge_btn.addEventListener("click", () => {
    generic_game.style.display = "none";
    judge_game.style.display = "block";
});

part_btn.addEventListener("click", () => {
    url = new URL(`/participant-game/${user_id}`, window.location.origin);
    url.searchParams.set("token", token);
    window.location.href = url.toString();
});

classic_mod.addEventListener("click", () => {
    url = new URL(`/judge-game/${user_id}`, window.location.origin);
    url.searchParams.set("token", token);
    window.location.href = url.toString();
});

verdict_mod.addEventListener("click", () => {
    url = new URL(`/verdict-game/${user_id}`, window.location.origin);
    url.searchParams.set("token", token);
    window.location.href = url.toString();
});