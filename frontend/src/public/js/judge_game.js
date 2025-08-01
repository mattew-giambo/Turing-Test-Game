const partita_section = document.getElementById("partita-section");
const sessione_section = document.getElementById("sessione-section");
const partita_terminata_section = document.getElementById("partita-terminata-section");
const game_id = window.location.pathname.split("/")[2]; // /judge-game/id
const vittoria = document.getElementById("vittoria-div");
const sconfitta = document.getElementById("sconfitta-div");
const popup = document.getElementById("popup");

const popup_errore = document.getElementById("popup-errore");
const hMessage = document.getElementById("hMessage");
const pMessage = document.getElementById("pMessage");

const showPopup_errore = (title, message) => {
        hMessage.textContent = title;
        pMessage.textContent = message;
        popup_errore.style.display = "flex";
};

const hidePopup_errore = () => {
    popup_errore.style.display = "none";
};

document.getElementById("form-partita").addEventListener("submit", async(e)=>{
    try{
        e.preventDefault();
        popup.style.display = "flex";
        const domanda1 = document.getElementById("domanda1").value;
        const domanda2 = document.getElementById("domanda2").value;
        const domanda3 = document.getElementById("domanda3").value;
        
        const data ={
            questions_list: new Array(domanda1, domanda2, domanda3)
        }

        const response = await fetch(`/send-questions-judge-game/${game_id}`, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(data)
        });

        if(!response.ok){
            const errorData = response.json();
            throw new Error(errorData.detail || "Errore nell'invio delle domande");
        }
        const answers_list = (await response.json()).answers_list;
        document.getElementById("sessione-domanda-1").innerText = domanda1;
        document.getElementById("sessione-domanda-2").innerText = domanda2;
        document.getElementById("sessione-domanda-3").innerText = domanda3;

        document.getElementById("sessione-risposta-1").innerText = answers_list[0];
        document.getElementById("sessione-risposta-2").innerText = answers_list[1];
        document.getElementById("sessione-risposta-3").innerText = answers_list[2];

        setTimeout(()=>{
            partita_section.style.display = "none";
            sessione_section.style.display = "flex";
            popup.style.display = "none";
        }, Math.floor(Math.random() * 6)*1000); // wait randomico tra 0 e 6sec
    }catch(error){
        console.log("Errore: ", error);
        showPopup_errore(
            "Errore",
            "Si è verificato un errore."
        );

        setTimeout(() => {
            hidePopup_errore();
            window.location.href = (new URL("/", window.location.origin)).toString();
        }, 3000);
    }
});

async function send_verdict(is_ai){
    try{
        const data ={
            is_ai: is_ai
        }
    const response = await fetch(`/send-judge-answer/${game_id}`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(data)
        });

        if(!response.ok){
            const errorData = response.json();
            throw new Error(errorData.detail || "Errore nell'invio del verdetto");
        }

        const response_data = await response.json();

        if(response_data.is_won){
            vittoria.style.display = "flex";
            document.getElementById("vittoria-msg").innerText = response_data.message;
            document.getElementById("azione-punti").innerText = "vinto";
        }
        else{
            sconfitta.style.display = "flex";
            document.getElementById("sconfitta-msg").innerText = response_data.message;
            document.getElementById("azione-punti").innerText = "perso";
        }
        document.getElementById("punti-valore").innerText = response_data.points;
        document.getElementById("label-punti").innerText = "TuringCoin"

        sessione_section.style.display = "none";
        partita_terminata_section.style.display = "block";
    }catch(error){
        console.log("Errore: ", error);
        showPopup_errore(
            "Errore",
            "Si è verificato un errore."
        );

        setTimeout(() => {
            hidePopup_errore();
            window.location.href = (new URL("/", window.location.origin)).toString();
        }, 3000);
    }
}

const umanoBtn = document.getElementById("umano-btn");
const macchinaBtn = document.getElementById("macchina-btn");

umanoBtn.addEventListener("click", async()=>{
    umanoBtn.classList.add("selected-btn");
    macchinaBtn.classList.remove("selected-btn");
    await send_verdict(false);
});

macchinaBtn.addEventListener("click", async()=>{
    macchinaBtn.classList.add("selected-btn");
    umanoBtn.classList.remove("selected-btn");
    await send_verdict(true);
});

const profilo_btn = document.getElementById("profilo-btn");
const url = new URL(profilo_btn.href);

const token = new URLSearchParams(window.location.search).get("token");

url.searchParams.set("token", token);

profilo_btn.href = url.toString();