const sessione_section = document.getElementById("sessione-section");
const partita_terminata_section = document.getElementById("partita-terminata-section");
const game_id = window.location.pathname.split("/")[2]; // /verdict-game/id
const vittoria = document.getElementById("vittoria-div");
const sconfitta = document.getElementById("sconfitta-div");


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

async function send_verdict(is_ai){
    try{
        const data ={
            is_ai: is_ai
        }
        const response = await fetch(`/send-pending-verdict/${game_id}`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(data)
        });

        if(!response.ok){
            const errorData = await response.json();
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
        document.getElementById("label-punti").innerText = (response_data.points == 1)? "punto":"punti";

        sessione_section.style.display = "none";
        partita_terminata_section.style.display = "block";
    }
    catch (error){
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