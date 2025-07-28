document.getElementById("btn-esci").addEventListener("click", async()=>{
    const user_id = window.location.pathname.split("/")[2];     // /profilo/{id}                       
    await fetch(`/user-disconnect/${user_id}`)
});