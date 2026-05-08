// État global
let selectedId = null;

// Chargement des livres
async function loadLivres(query = "") {
    const url = query ? `/api/recherche?q=${encodeURIComponent(query)}` : "/api/livres";
    const response = await fetch(url);
    const livres = await response.json();
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
        editBtn.className = "action-btn";
        editBtn.onclick = () => fillForm(l);
        const delBtn = document.createElement("button");
        delBtn.innerHTML = "🗑️";
        delBtn.className = "action-btn";
        delBtn.onclick = () => deleteLivre(l.id);
        actions.appendChild(editBtn);
        actions.appendChild(delBtn);
    });
}

// Remplir le formulaire pour modification
function fillForm(livre) {
    selectedId = livre.id;
    document.getElementById("titre").value = livre.titre;
    document.getElementById("auteur").value = livre.auteur;
    document.getElementById("categorie").value = livre.categorie || "";
    document.getElementById("annee").value = livre.annee || "";
    document.getElementById("quantite").value = livre.quantite;
    document.getElementById("statut").value = livre.statut;
    document.getElementById("formMsg").innerText = `✏️ Modification du livre #${livre.id}`;
}

// Vider le formulaire
function clearForm() {
    selectedId = null;
    document.getElementById("titre").value = "";
    document.getElementById("auteur").value = "";
    document.getElementById("categorie").value = "";
    document.getElementById("annee").value = "";
    document.getElementById("quantite").value = "1";
    document.getElementById("statut").value = "disponible";
    document.getElementById("formMsg").innerText = "";
}

// Ajouter un livre
async function addLivre() {
    const data = {
        titre: document.getElementById("titre").value.trim(),
        auteur: document.getElementById("auteur").value.trim(),
        categorie: document.getElementById("categorie").value.trim(),
        annee: parseInt(document.getElementById("annee").value) || 0,
        quantite: parseInt(document.getElementById("quantite").value) || 1,
        statut: document.getElementById("statut").value
    };
    if (!data.titre || !data.auteur) {
        alert("Le titre et l'auteur sont obligatoires.");
        return;
    }
    await fetch("/api/livres", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });
    loadLivres();
    clearForm();
}

// Modifier un livre
async function updateLivre() {
    if (!selectedId) {
        alert("Sélectionnez un livre dans la liste d'abord.");
        return;
    }
    const data = {
        titre: document.getElementById("titre").value.trim(),
        auteur: document.getElementById("auteur").value.trim(),
        categorie: document.getElementById("categorie").value.trim(),
        annee: parseInt(document.getElementById("annee").value) || 0,
        quantite: parseInt(document.getElementById("quantite").value) || 1,
        statut: document.getElementById("statut").value
    };
    if (!data.titre || !data.auteur) {
        alert("Le titre et l'auteur sont obligatoires.");
        return;
    }
    await fetch(`/api/livres/${selectedId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });
    loadLivres();
    clearForm();
}

// Supprimer un livre
async function deleteLivre(id) {
    if (confirm("Supprimer définitivement ce livre ?")) {
        await fetch(`/api/livres/${id}`, { method: "DELETE" });
        if (selectedId === id) clearForm();
        loadLivres();
    }
}

// Supprimer depuis le bouton
async function deleteSelected() {
    if (selectedId) {
        await deleteLivre(selectedId);
    } else {
        alert("Aucun livre sélectionné.");
    }
}

// Chatbot
async function sendQuestion(question) {
    if (!question.trim()) return;
    const chatDiv = document.getElementById("chat-messages");
    // Afficher la question de l'utilisateur
    chatDiv.innerHTML += `<div class="message user-message"><strong>🧑 Vous :</strong> ${escapeHtml(question)}</div>`;
    document.getElementById("question").value = "";
    // Appel API
    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question })
        });
        const data = await response.json();
        chatDiv.innerHTML += `<div class="message bot-message"><strong>🤖 BiblioBot :</strong> ${escapeHtml(data.reponse)}</div>`;
    } catch (err) {
        chatDiv.innerHTML += `<div class="message bot-message"><strong>🤖 BiblioBot :</strong> ❌ Désolé, erreur de connexion au serveur.</div>`;
    }
    chatDiv.scrollTop = chatDiv.scrollHeight;
}

function escapeHtml(str) {
    if (!str) return "";
    return str.replace(/[&<>]/g, function(m) {
        if (m === "&") return "&amp;";
        if (m === "<") return "&lt;";
        if (m === ">") return "&gt;";
        return m;
    }).replace(/\n/g, "<br>");
}

// API Key
async function saveApiKey() {
    const key = document.getElementById("apiKey").value.trim();
    if (!key) {
        document.getElementById("apiStatus").innerText = "Veuillez entrer une clé valide.";
        return;
    }
    const response = await fetch("/api/config", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ api_key: key })
    });
    if (response.ok) {
        document.getElementById("apiStatus").innerHTML = "✅ Clé sauvegardée (valable tant que le serveur tourne).";
        document.getElementById("apiKey").value = "";
    } else {
        document.getElementById("apiStatus").innerHTML = "❌ Erreur lors de la sauvegarde.";
    }
}

async function checkApiStatus() {
    const response = await fetch("/api/config");
    const data = await response.json();
    const statusSpan = document.getElementById("apiStatus");
    if (data.has_key) {
        statusSpan.innerHTML = "✅ Une clé API est active. Le chatbot peut utiliser Gemini.";
        statusSpan.className = "status success";
    } else {
        statusSpan.innerHTML = "⚠️ Aucune clé API. Le chatbot fonctionne en mode local (mots-clés).";
        statusSpan.className = "status error";
    }
}

// Navigation entre onglets
function switchTab(tabId) {
    document.querySelectorAll(".tab").forEach(tab => tab.classList.remove("active"));
    document.getElementById(`${tabId}-tab`).classList.add("active");
    document.querySelectorAll(".nav-btn").forEach(btn => btn.classList.remove("active"));
    document.querySelector(`.nav-btn[data-tab="${tabId}"]`).classList.add("active");
    if (tabId === "livres") loadLivres();
    if (tabId === "config") checkApiStatus();
}

// Événements DOM
document.addEventListener("DOMContentLoaded", () => {
    // Liens de navigation
    document.querySelectorAll(".nav-btn").forEach(btn => {
        btn.addEventListener("click", () => switchTab(btn.dataset.tab));
    });
    // Boutons CRUD
    document.getElementById("addBtn").addEventListener("click", addLivre);
    document.getElementById("updateBtn").addEventListener("click", updateLivre);
    document.getElementById("deleteBtn").addEventListener("click", deleteSelected);
    document.getElementById("clearBtn").addEventListener("click", clearForm);
    // Recherche
    document.getElementById("searchBtn").addEventListener("click", () => {
        const q = document.getElementById("searchInput").value;
        loadLivres(q);
    });
    document.getElementById("resetBtn").addEventListener("click", () => {
        document.getElementById("searchInput").value = "";
        loadLivres();
    });
    document.getElementById("searchInput").addEventListener("keypress", (e) => {
        if (e.key === "Enter") loadLivres(e.target.value);
    });
    // Chat
    document.getElementById("sendBtn").addEventListener("click", () => {
        sendQuestion(document.getElementById("question").value);
    });
    document.getElementById("question").addEventListener("keypress", (e) => {
        if (e.key === "Enter") sendQuestion(e.target.value);
    });
    document.querySelectorAll(".example-btn").forEach(btn => {
        btn.addEventListener("click", () => sendQuestion(btn.innerText));
    });
    // API Config
    document.getElementById("saveKeyBtn").addEventListener("click", saveApiKey);
    // Chargement initial
    loadLivres();
});