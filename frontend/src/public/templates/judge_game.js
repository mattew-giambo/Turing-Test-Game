const partita_section = document.getElementById("partita-section");
const sessione_section = document.getElementById("sessione-section");
const partita_terminata_section = document.getElementById("partita-terminata-section");
const game_id = window.location.pathname.split("/")[2]; // /judge-game/id

document.getElementById("form-partita").addEventListener("submit", async(e)=>{
    e.preventDefault();

    const domanda1 = document.getElementById("domanda1").value;
    const domanda2 = document.getElementById("domanda2").value;
    const domanda3 = document.getElementById("domanda3").value;
    
    const data ={
        question1: domanda1,
        question2: domanda2,
        question3: domanda3
    }

    const response = await fetch(`/send-questions-judge-game/${game_id}`, {
       method: "POST",
       headers: {"Content-Type": "application/json"},
       body: JSON.stringify(data)
    });

    if(!response.ok){
        const errorData = response.json();
        console.error(errorData.detail)
        return window.location.pathname = "/";
    }

    const answers_list = response.json().answers_list;
    document.getElementById("sessione-domanda-1").innerText = domanda1;
    document.getElementById("sessione-domanda-2").innerText = domanda2;
    document.getElementById("sessione-domanda-3").innerText = domanda3;

    document.getElementById("sessione-risposta-1").innerText = answers_list[0];
    document.getElementById("sessione-risposta-2").innerText = answers_list[1];
    document.getElementById("sessione-risposta-3").innerText = answers_list[2];

    partita_section.style.display = "none";
    sessione_section.style.display = "block";
});

document.getElementById("umano-btn").addEventListener("click", async()=>{
    const data ={
        is_ai: false
    }
    const response = await fetch(`/send-judge-answer/${game_id}`, {
       method: "POST",
       headers: {"Content-Type": "application/json"},
       body: JSON.stringify(data)
    });

    if(!response.ok){
        const errorData = response.json();
        console.error(errorData.detail)
        return window.location.pathname = "/";
    }


});