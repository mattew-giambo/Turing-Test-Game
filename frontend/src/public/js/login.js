document.getElementById("login-form").addEventListener("submit", async(e)=>{
    e.preventDefault();

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    const data = {
        user_name: username,
        password: password
    }

    try {
        const response = await fetch("/login", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(data)
        });

        const response_data = await response.json();
        console.log("response_data.detail:", response_data.detail);

        if (!response.ok) {
            document.getElementById("msg-error").innerText = response_data.detail;
            document.getElementById("msg-error").style.display = "block";

            setTimeout(() => {
                document.getElementById("msg-error").style.display = "none";
                document.getElementById("msg-error").innerText = "";
            }, 3000);
            return;
        }

        const url = new URL(`/profilo/${response_data.user_id}`, window.location.origin);
        url.searchParams.set("token", `${response_data.token}`);
        return window.location.href= url.toString();
    } catch (error) {
        console.error("Errore nella fetch:", error);
        document.getElementById("msg-error").innerText = "Errore durante il login.";
        document.getElementById("msg-error").style.display = "block";

        setTimeout(() => {
            document.getElementById("msg-error").style.display = "none";
            document.getElementById("msg-error").innerText = "";
        }, 3000);
    }
});