document.getElementById("participant-form").addEventListener("submit", async (e) => {
    e.preventDefault(); 

    const form = e.target;
    const formData = new FormData(form);  // raccoglie tutti gli input con attributo name

    try {
        const response = await fetch(`/send-answers-participant-game/${game_id}`, {
            method: "POST",
            body: formData  
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || "Errore nell'invio delle risposte");
        }

        const result = await response.json();
        console.log("Risposte inviate con successo:", result);

        const user_id = window.location.pathname.split("/")[2];
        const params = new URLSearchParams(window.location.search);
        const token = params.get("token");

        const newUrl = new URL(`/profilo/${user_id}`, window.location.origin);
        newUrl.searchParams.set("token", token);
        window.location.href = newUrl.toString();
    } catch (error) {
        alert("Errore: " + error.message);
        console.error("Errore invio risposte:", error);
    }
});
