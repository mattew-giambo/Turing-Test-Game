const profilo_stats = document.getElementById("profilo_stats");
const url = new URL(profilo_stats.href);

const params = new URLSearchParams(window.location.search);
const token = params.get("token");

url.searchParams.set("token", token);
profilo_stats.href = url.toString();