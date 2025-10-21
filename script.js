  // Adresse du serveur Flask
  const SERVER_URL = "//";
  
  /* INITIALISATION DES BOUTONS */
document.addEventListener("DOMContentLoaded", () => {
    // Commandes directionnelles
    document
      .querySelector(".btn-up")
      .addEventListener("click", () => envoyerCommande("avancer"));
/*    document
      .querySelector(".btn-down")
      .addEventListener("click", () => envoyerCommande("arriere")); */
    document
      .querySelector(".btn-left")
      .addEventListener("click", () => envoyerCommande("gauche"));
    document
      .querySelector(".btn-right")
      .addEventListener("click", () => envoyerCommande("droite"));
  
    // Bouton principal : START/STOP
//    document.querySelector(".btn-stop").addEventListener("click", toggleStop);

  
  // État global du robot
//  let robotOff = false;
  
  /*  BOUTON STOP */
  
/*  function toggleStop() {
    const stopButton = document.querySelector(".btn-stop");
    const allButtons = document.querySelectorAll(".btn:not(.btn-stop)");
    robotOff = !robotOff; // inverse l'état
  
    if (robotOff) {
      stopButton.classList.add("active");
      allButtons.forEach((b) => (b.disabled = true));
      console.log(" Robot éteint");
  
      fetch(`${SERVER_URL}/stop?state=off`)
        .then((res) => res.json())
        .then((data) => console.log("Serveur :", data.message))
        .catch((err) => console.error("Erreur serveur STOP :", err));
    } else {
      stopButton.classList.remove("active");
      allButtons.forEach((b) => (b.disabled = false));
      console.log("Robot allumé");
  
      fetch(`${SERVER_URL}/stop?state=on`)
        .then((res) => res.json())
        .then((data) => console.log("Serveur :", data.message))
        .catch((err) => console.error("Erreur serveur START :", err));
    }*/
  })
  
  /* ENVOI DES COMMANDES */
  
  function envoyerCommande(action) {
    if (robotOff) {
      console.warn(" robot en arrêt");
      return;
    }

    console.log(" Envoi commande :", action);
  
    fetch(`${SERVER_URL}/${action}`)
      .then((response) => response.json())
      .then((data) => console.log(" Réponse du robot :", data.message))
      .catch((err) => console.error("Erreur d'envoi :", err));
  }
  
  /* GESTION DE LA BATTERIE */
  
  function updateBatteryLevel(level) {
    const batteryDiv = document.getElementById("battery-level");
    const batteryText = document.getElementById("battery-text");
  
    // Met à jour la barre et le texte
    batteryDiv.style.width = level + "%";
    batteryText.textContent = "Batterie : " + level + "%";
  
    // Couleur selon le niveau
    if (level > 60) {
      batteryDiv.style.backgroundColor = "green";
    } else if (level > 30) {
      batteryDiv.style.backgroundColor = "orange";
    } else {
      batteryDiv.style.backgroundColor = "red";
    }
  }
  
  /* GRAPHIQUE DE CONSOMMATION */
  
  const ctx = document.getElementById("powerChart").getContext("2d");
  const powerChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: [],
      datasets: [
        {
          label: "Consommation (W)",
          data: [],
          borderWidth: 2,
          borderColor: "#8b5a2b",
        },
      ],
    },
    options: {
      scales: {
        y: { beginAtZero: true },
        x: { title: { display: true, text: "Temps (s)" } },
      },
    },
  });
  
  /* MISE À JOUR DU GRAPHIQUE */
  
  function updatePowerChart(time, powerValue) {
    powerChart.data.labels.push(time);
    powerChart.data.datasets[0].data.push(powerValue);
  
    // Ne garde que les 50 derniers points
    if (powerChart.data.labels.length > 50) {
      powerChart.data.labels.shift();
      powerChart.data.datasets[0].data.shift();
    }
  
    powerChart.update();
  }
  
  /* MISE À JOUR DES CAPTEURS */
  
  function updateSensors() {
    fetch(`${SERVER_URL}/capteur`)
      .then((res) => res.json())
      .then((data) => {
        updateBatteryLevel(data.batterie);
        updatePowerChart(data.temps, data.puissance);
      })
      .catch((err) => console.error("Erreur capteur :", err));
    }