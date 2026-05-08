let selectedId = null;

async function loadLivres(query = "") {
    const url = query ? `/api/recherche?q=${encodeURIComponent(query)}` : "/api/livres";
    try {
        const res = await fetch(url);
        const livres = await res.json();
        const tbody = document.getElementById("table-body");
        tbody.innerHTML = "";
        livres.forEach(l => {
            const row = tbody.insertRow();
            row.insertCell(0).innerText = l.id;
            row.insertCell(1).innerText = l.titre;
            row.insertCell(2).innerText = l.auteur;
            row.insertCell(3).innerText = l.categorie || "—";
            row.insertCell(4).innerText = l.annee || "—";
            row.insertCell(5).innerText = l.quantite;
            const statCell = row.insertCell(6);
            statCell.innerText = l.statut;
            statCell.className = `statut-${l.statut}`;
            const actions = row.insertCell(7);
            const editBtn = document.createElement("button");
            editBtn.innerHTML = "✏️";
            editBtn.onclick = () => fillForm(l);
            const delBtn = document.createElement("button");
            delBtn.innerHTML = "🗑️";
            delBtn.onclick = () => deleteLivre(l.id);
            actions.appendChild(editBtn);
            actions.appendChild(delBtn);
        });
    } catch (err) {
        document.getElementById("table-body").innerHTML = '<tr><td colspan="8">❌ Erreur chargement livres</td></tr>';
    }
}

function fillForm(l) { selectedId = l.id; document.getElementById("titre").value = l.titre; document.getElementById("auteur").value = l.auteur; document.getElementById("categorie").value = l.categorie || ""; document.getElementById("annee").value = l.annee; document.getElementById("quantite").value = l.quantite; document.getElementById("statut").value = l.statut; document.getElementById("formMsg").innerText = `Modification ID ${l.id}`; }
function clearForm() { selectedId = null; document.getElementById("titre").value = ""; document.getElementById("auteur").value = ""; document.getElementById("categorie").value = ""; document.getElementById("annee").value = ""; document.getElementById("quantite").value = "1"; document.getElementById("statut").value = "disponible"; document.getElementById("formMsg").innerText = ""; }
async function addLivre() { const data = { titre: document.getElementById("titre").value, auteur: document.getElementById("auteur").value, categorie: document.getElementById("categorie").value, annee: parseInt(document.getElementById("annee").value)||0, quantite: parseInt(document.getElementById("quantite").value)||1, statut: document.getElementById("statut").value }; if(!data.titre||!data.auteur) return alert("Titre et auteur requis"); await fetch("/api/livres", {method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(data)}); loadLivres(); clearForm(); }
async function updateLivre() { if(!selectedId) return alert("Sélectionnez un livre"); const data = { titre: document.getElementById("titre").value, auteur: document.getElementById("auteur").value, categorie: document.getElementById("categorie").value, annee: parseInt(document.getElementById("annee").value)||0, quantite: parseInt(document.getElementById("quantite").value)||1, statut: document.getElementById("statut").value }; await fetch(`/api/livres/${selectedId}`, {method:"PUT",headers:{"Content-Type":"application/json"},body:JSON.stringify(data)}); loadLivres(); clearForm(); }
async function deleteLivre(id) { if(confirm("Supprimer ?")) { await fetch(`/api/livres/${id}`, {method:"DELETE"}); if(selectedId===id) clearForm(); loadLivres(); } }
async function deleteSelected() { if(selectedId) deleteLivre(selectedId); else alert("Sélectionnez un livre"); }
async function sendQuestion(question) { if(!question.trim()) return; const chatDiv = document.getElementById("chat-messages"); chatDiv.innerHTML += `<div class="message user-message"><strong>🧑 Vous :</strong> ${escapeHtml(question)}</div>`; document.getElementById("question").value = ""; try { const res = await fetch("/api/chat", {method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({question})}); const data = await res.json(); chatDiv.innerHTML += `<div class="message bot-message"><strong>🤖 BiblioBot :</strong> ${escapeHtml(data.reponse)}</div>`; } catch(e) { chatDiv.innerHTML += `<div class="message bot-message"><strong>🤖 BiblioBot :</strong> ❌ Erreur de connexion</div>`; } chatDiv.scrollTop = chatDiv.scrollHeight; }
function escapeHtml(str) { return str.replace(/[&<>]/g, m => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;' }[m] || m)).replace(/\n/g,"<br>"); }
async function saveApiKey() { const key = document.getElementById("apiKey").value.trim(); if(!key) return; await fetch("/api/config", {method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({api_key:key})}); document.getElementById("apiStatus").innerHTML = "✅ Clé sauvegardée (en mémoire)"; }
async function checkApiStatus() { const res = await fetch("/api/config"); const data = await res.json(); document.getElementById("apiStatus").innerHTML = data.has_key ? "✅ Clé active" : "⚠️ Aucune clé (mode local)"; }
function switchTab(tabId) { document.querySelectorAll(".tab").forEach(t=>t.classList.remove("active")); document.getElementById(`${tabId}-tab`).classList.add("active"); document.querySelectorAll(".nav-btn").forEach(b=>b.classList.remove("active")); document.querySelector(`.nav-btn[data-tab="${tabId}"]`).classList.add("active"); if(tabId==="livres") loadLivres(); if(tabId==="config") checkApiStatus(); }
document.addEventListener("DOMContentLoaded", () => { document.querySelectorAll(".nav-btn").forEach(b=>b.addEventListener("click",()=>switchTab(b.dataset.tab))); document.getElementById("addBtn").addEventListener("click",addLivre); document.getElementById("updateBtn").addEventListener("click",updateLivre); document.getElementById("deleteBtn").addEventListener("click",deleteSelected); document.getElementById("clearBtn").addEventListener("click",clearForm); document.getElementById("searchBtn").addEventListener("click",()=>loadLivres(document.getElementById("searchInput").value)); document.getElementById("resetBtn").addEventListener("click",()=>{document.getElementById("searchInput").value=""; loadLivres();}); document.getElementById("sendBtn").addEventListener("click",()=>sendQuestion(document.getElementById("question").value)); document.querySelectorAll(".example-btn").forEach(btn=>btn.addEventListener("click",()=>sendQuestion(btn.innerText))); document.getElementById("saveKeyBtn").addEventListener("click",saveApiKey); loadLivres(); });
