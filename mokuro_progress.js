document.addEventListener("DOMContentLoaded", function () {
  // Sicherstellen, dass das Eingabefeld existiert
  const input = document.getElementById("pageIdxInput");

  if (!input) {
    console.error("❌ Kein Eingabefeld gefunden!");
    return;
  }

  // Den aktuellen Pfad der Seite extrahieren und dekodieren
  let path = decodeURIComponent(window.location.pathname).replace(/^\/static/, ".");
  console.log("📖 Aktueller dekodierter Pfad:", path);

  // Umwandlung des Pfads in relativ (entfernt das führende '/')
  if (path.startsWith('/manga')) {
    path = '.' + path;  // Fügt './' vor dem Pfad hinzu, um ihn relativ zu machen
  }

  console.log("📖 Umgewandelter Pfad:", path);

  // Normalisierung der Pfade für den Vergleich
  function normalize(path) {
    return path.replace(/^\/static\//, "").replace(/\\/g, "/").toLowerCase();
  }

  const totalPages = parseInt(input?.max || "0", 10);
  let lastSentPage = -1;

  console.log("📖 Hamsti-Progress aktiv für:", path);

  // Fortschritt vom Server lesen und die Seite setzen
  fetch("/progress")
    .then(res => res.json())
    .then(data => {
      console.log("📖 Fortschritt vom Server geladen:", data);

      // Ausgabe des gesuchten Pfads und aller gespeicherten Pfade zur Fehlerbehebung
      console.log("📖 Gesuchter Pfad:", path);
      data.forEach(entry => console.log(`📖 Gespeicherter Pfad: ${entry.path}`));

      // Vergleiche den dekodierten Pfad mit den gespeicherten Pfaden
      const match = data.find(entry => normalize(entry.path) === normalize(path)); // Normalisierung beider Pfade
      if (match) {
        const page_idx = match.page_idx || 0;
        input.value = page_idx + 1; // Seite auf den gespeicherten Fortschritt setzen
        input.dispatchEvent(new Event("change")); // Änderung des Eingabewerts auslösen
        lastSentPage = match.page_idx;
        console.log(`📖 Fortschritt angewendet: Seite ${page_idx + 1}`);
      } else {
        console.log("📖 Kein Fortschritt für diesen Pfad gefunden.");
      }
    })
    .catch(err => {
      console.error("Fehler beim Abrufen des Fortschritts:", err);
    });

  // Fortschritt senden bei Änderung
  setInterval(() => {
    const current = parseInt(input.value, 10) - 1;
    if (Number.isNaN(current) || current === lastSentPage) return;

    lastSentPage = current;

    console.log("📤 Fortschritt Seite:", current);

    fetch("/update_progress", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        path,
        page_idx: current,
        last_page_idx: totalPages
      })
    })
      .then(r => r.json())
      .then(res => console.log("✅ Serverantwort:", res))
      .catch(console.error);
  }, 300);
});


(function () {
  // 🖌️ Stil einfügen
  const style = document.createElement("style");
  style.textContent = `
    #hamsti-nav-buttons {
      position: fixed;
      top: 42px;
      z-index: 9999;
    }

    .hamsti-button {
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 8px;
      background-color: #fff;
      opacity: 0.9;
      border-radius: 8px;
      color: #333;
      cursor: pointer;
      transition: background-color 0.3s ease;
      border: none;
      box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
      margin:12px;
    }

    .hamsti-button:hover {
      background-color: #e0e0e0;
    }

    .hamsti-button svg {
      width: 24px;
      height: 24px;
    }
  `;
  document.head.appendChild(style);

  const normalize = path => path.replace(/^\.\//, "").replace(/^\/+/, "");

  const nav = document.createElement("div");
  nav.id = "hamsti-nav-buttons";

  // 🏠 Bookshelf
  const backToShelf = document.createElement("a");
  backToShelf.className = "hamsti-button";
  backToShelf.href = "/serve_bookshelf";
  backToShelf.title = "home";
  backToShelf.innerHTML = `
    <svg xmlns="http://www.w3.org/2000/svg" fill="none"
         viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round"
            d="m2.25 12 8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875
             c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25" />
    </svg>
  `;

  // ⬅️ Zurück
  const prev = document.createElement("button");
  prev.className = "hamsti-button";
  prev.title = "previous volume";
  prev.innerHTML = `
    <svg xmlns="http://www.w3.org/2000/svg" fill="none"
         viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round"
            d="m11.25 9-3 3m0 0 3 3m-3-3h7.5M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
    </svg>
  `;
  prev.onclick = () => {
    fetch("/progress")
      .then(r => r.json())
      .then(data => {
        const current = normalize(decodeURIComponent(window.location.pathname));
        const idx = data.findIndex(e => normalize(e.path) === current);
        if (idx > 0) {
          location.href = "/" + normalize(data[idx - 1].path);
        } else {
          alert("Kein vorheriges Volume 🐾");
        }
      });
  };

  // ➡️ Weiter
  const next = document.createElement("button");
  next.className = "hamsti-button";
  next.title = "next volume";
  next.innerHTML = `
    <svg xmlns="http://www.w3.org/2000/svg" fill="none"
         viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round"
            d="m12.75 15 3-3m0 0-3-3m3 3h-7.5M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
    </svg>
  `;
  next.onclick = () => {
    fetch("/progress")
      .then(r => r.json())
      .then(data => {
        const current = normalize(decodeURIComponent(window.location.pathname));
        const idx = data.findIndex(e => normalize(e.path) === current);
        if (idx >= 0 && idx + 1 < data.length) {
          location.href = "/" + normalize(data[idx + 1].path);
        } else {
          alert("Kein nächstes Volume gefunden 🥺");
        }
      });
  };

  // 🧩 Zusammenbauen
  nav.appendChild(backToShelf);
    nav.appendChild(next);
  nav.appendChild(prev);

  document.body.appendChild(nav);
  
document.addEventListener("keydown", e => {
  if (e.key === "Escape") {
    window.location.replace(window.location.origin + "/serve_bookshelf");
  }
});

})();

