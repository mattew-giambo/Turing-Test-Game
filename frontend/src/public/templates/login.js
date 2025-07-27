document.getElementById("login-form").addEventListener("submit", async(e)=>{
    e.preventDefault();

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    const msg_error = document.getElementById("msg-error")

    const data = {
        username: username,
        password: password
    }

    const response = await fetch("/loging", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(data)
    });

    const response_data = await response.json();
    if(response.ok){
        const url = new URL(`/profilo/${response_data.user_id}`);
        url.searchParams.set("token", `${response_data.token}`);
        return window.location.href= url;
    }
    else{
        msg_error.innerText= response_data.detail;
        msg_error.style.display = "block";

        setTimeout(()=>{
            msg_error.style.display = "none";
            msg_error.innerText = "";
        }, 3000);

        return;
    }
});