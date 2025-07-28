document.getElementById("registration-form").addEventListener("submit", async (e)=>{
    e.preventDefault();

    const user_name = document.getElementById("username").value;
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const conferma_password = document.getElementById("conferma_password").value;

    if(password !== conferma_password) {
        document.getElementById("msg-error").innerText = "Le password non coincidono.";
        document.getElementById("msg-error").style.display = "block";

        setTimeout(() => {
            document.getElementById("msg-error").style.display = "none";
            document.getElementById("msg-error").innerText = "";
        }, 3000);
        return;
    }

    const data = {
        user_name: user_name,
        email: email,
        password: password
    };

    try {
        const response = await fetch("/register", {
            method: "POST",
            headers: {"Content-Type" : "application/json"},
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const errorData = await response.json();
            document.getElementById("msg-error").innerText = errorData.detail;
            document.getElementById("msg-error").style.display = "block";

            setTimeout(() => {
                document.getElementById("msg-error").style.display = "none";
                document.getElementById("msg-error").innerText = "";
            }, 3000);
            return;
        }
        
        window.location.pathname = "/login";

    } catch (error) {
        console.error("Errore nella fetch:", error);
        document.getElementById("msg-error").innerText = "Errore durante la registrazione.";
        document.getElementById("msg-error").style.display = "block";

        setTimeout(() => {
            document.getElementById("msg-error").style.display = "none";
            document.getElementById("msg-error").innerText = "";
        }, 3000);
    }
});
