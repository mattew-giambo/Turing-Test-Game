const partita_section = document.getElementById("partita-section");
const sessione_section = document.getElementById("sessione-section");
const partita_terminata_section = document.getElementById("partita-terminata-section");
const game_id = window.location.pathname.split("/")[2]; // /verdict-game/id

async function send_verdict(is_ai){
    const data ={
        is_ai: is_ai
    }
    const response = await fetch(`/send-pending-verdict/${game_id}`, {
       method: "POST",
       headers: {"Content-Type": "application/json"},
       body: JSON.stringify(data)
    });

    if(!response.ok){
        const errorData = response.json();
        console.error(errorData.detail)
        return window.location.pathname = "/";
    }

    const response_data = await response.json();

    if(response_data.is_won){
        document.getElementById("vittoria-msg").innerText = response_data.message;
        document.getElementById("azione-punti").innerText = "vinto";
    }
    else{
        document.getElementById("sconfitta-msg").innerText = response_data.message;
        document.getElementById("azione-punti").innerText = "perso";
    }
    document.getElementById("punti-valore").innerText = response_data.points;
    document.getElementById("label-punti").innerText = (response_data.points == 1)? "punto":"punti";

    sessione_section.style.display = "none";
    partita_terminata_section.style.display = "block";
}

document.getElementById("umano-btn").addEventListener("click", async()=>{
    await send_verdict(false);
});

document.getElementById("macchina-btn").addEventListener("click", async()=>{
    await send_verdict(true);
});

const profilo_btn = document.getElementById("profilo-btn");
const url = new URL(profilo_btn.href);

const token = new URLSearchParams(window.location.search).get("token");

url.searchParams.set("token", token);

profilo_btn.href = url.toString();