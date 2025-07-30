document.getElementById("participant-form").addEventListener("submit", async (e) => {
    e.preventDefault(); 

    const form = e.target;
    const answers = [
        form.answer1.value,
        form.answer2.value,
        form.answer3.value
    ];

    const popup = document.getElementById("popup");
    const hMessage = document.getElementById("hMessage");
    const pMessage = document.getElementById("pMessage");
    const closeBtn = document.getElementById("close-popup-btn");
    const game_id = window.location.pathname.split("/")[2];

    const showPopup = (title, message) => {
        hMessage.textContent = title;
        pMessage.textContent = message;
        popup.style.display = "flex";
    };

    const hidePopup = () => {
        popup.style.display = "none";
    };

    closeBtn.addEventListener("click", hidePopup);

    try {
        const response = await fetch(`/send-answers-participant-game/${game_id}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ answers })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || "Errore nell'invio delle risposte");
        }

        const result = await response.json();
        console.log("Risposte inviate con successo:", result);

        showPopup(
            "Invio completato",
            "Tutto è andato a buon fine! Verrai reindirizzato al profilo per attendere l’esito..."
        );

        setTimeout(() => {
            const params = new URLSearchParams(window.location.search);
            const token = params.get("token");

            const closeBtn = document.getElementById("close-popup-btn");
            const newUrl = new URL(closeBtn.href);
            newUrl.searchParams.set("token", token);
            window.location.href = newUrl.toString();
        }, 3000);

    } catch (error) {
        console.error("Errore invio risposte:", error);

        showPopup(
            "Errore",
            "Si è verificato un errore durante l'invio. Per favore riprova..."
        );

        setTimeout(() => {
            hidePopup();
        }, 3000);
    }
});

