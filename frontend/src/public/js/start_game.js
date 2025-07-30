const profilo_stats = document.getElementById("profilo_stats");
const url = new URL(profilo_stats.href);

const params = new URLSearchParams(window.location.search);
const token = params.get("token");
const user_id = window.location.pathname.split("/")[2];

url.searchParams.set("player_id", user_id);
url.searchParams.set("token", token);
profilo_stats.href = url.toString();

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

part_btn.addEventListener("click", async () => {
    try{
        const data = {
            player_id: parseInt(user_id),
            player_role: "participant"
        };

        const response = await fetch("/start-game", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const errorData = await response.json();
            const message = typeof errorData.detail === "string"
                ? errorData.detail
                : JSON.stringify(errorData.detail);
            throw new Error(message || "Errore avvio partita");
        }

        const data_response = await response.json();
        const game_id = data_response.game_id;

        const newUrl = new URL(`/participant-game/${game_id}`, window.location.origin);
        newUrl.searchParams.set("player_id", user_id);
        newUrl.searchParams.set("token", token);
        window.location.href = newUrl.toString();
    } catch (error) {
        alert("Errore: " + error.message);
        console.error("Errore avvio partita partecipante:", error);
    }
});

classic_mod.addEventListener("click", async () => {
    try{
        const data = {
            player_id: parseInt(user_id),
            player_role: "judge"
        };

        const response = await fetch("/start-game", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const errorData = await response.json();
            const detailMsg = typeof errorData.detail === "string"
                ? errorData.detail
                : JSON.stringify(errorData.detail);
            throw new Error(detailMsg || "Errore avvio partita");
        }


        const data_response = await response.json();
        const game_id = data_response.game_id;

        const newUrl = new URL(`/judge-game/${game_id}`, window.location.origin);
        newUrl.searchParams.set("player_id", user_id);
        newUrl.searchParams.set("token", token);
        window.location.href = newUrl.toString();
    } catch (error) {
        alert("Errore: " + error.message);
        console.error("Errore avvio partita partecipante:", error);
    }
});

verdict_mod.addEventListener("click", async () => {
    try{
        const data = {
            player_id: parseInt(user_id),
            player_role: "judge"
        };
        console.log(data);

        const response = await fetch("/start-pending-game", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const errorData = await response.json();
            const message = typeof errorData.detail === "string"
                ? errorData.detail
                : JSON.stringify(errorData.detail);
            throw new Error(message || "Errore avvio partita");
        }

        const data_response = await response.json();
        const game_id = data_response.game_id;

        const newUrl = new URL(`/verdict-game/${game_id}`, window.location.origin);
        newUrl.searchParams.set("player_id", user_id);
        newUrl.searchParams.set("token", token);
        window.location.href = newUrl.toString();
    } catch (error) {
        alert("Errore: " + error.message);
        console.error("Errore avvio partita partecipante:", error);
    }
});