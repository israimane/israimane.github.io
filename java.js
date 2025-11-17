document.addEventListener("DOMContentLoaded", () => {

    // ============================
    // Gestion des boutons simples
    // ============================
    function envoyerCommandeSimple(cmd, val, time) {
        fetch(`/commandes?type=${cmd}&val=${val}&time=${time}`, { method: 'POST' })
            .then(() => console.log(`Commande envoyée: ${cmd}, val=${val}, time=${time}`))
            .catch(err => console.error(err));
    }

    // Réduire le temps pour des mouvements plus réactifs
    const btnTime = 0.3; // secondes

    document.querySelector(".btn-up").addEventListener("click", () => envoyerCommandeSimple('forward', 0.5, btnTime));
    document.querySelector(".btn-left").addEventListener("click", () => envoyerCommandeSimple('left', 0.5, btnTime));
    document.querySelector(".btn-right").addEventListener("click", () => envoyerCommandeSimple('right', 0.5, btnTime));
    document.querySelector(".btn-down").addEventListener("click", () => envoyerCommandeSimple('backward', 0.5, btnTime));
    document.querySelector(".btn-dance").addEventListener("click", () => envoyerCommandeSimple('dance', 0, btnTime));

    // ============================
    // Initialisation du joystick
    // ============================
    const joystick = nipplejs.create({
        zone: document.getElementById('joystick-container'),
        mode: 'static',
        position: { left: '50%', top: '50%' },
        color: 'blue',
        size: 120
    });

    let lastCommandTime = 0;

    joystick.on('move', (evt, data) => {
        if (!data || !data.vector) return;

        const now = Date.now();
        if (now - lastCommandTime < 500) return; // 1 commande / 0,5 sec

        // Limiter la vitesse pour que les virages ne fassent pas 180°
        let leftSpeed = data.vector.y + data.vector.x;
        let rightSpeed = data.vector.y - data.vector.x;

        // Limiter les valeurs à [-0.6, 0.6] pour éviter rotations trop violentes
        leftSpeed = Math.max(Math.min(leftSpeed, 0.6), -0.6);
        rightSpeed = Math.max(Math.min(rightSpeed, 0.6), -0.6);

        fetch(`/commandes?type=joystick&left=${leftSpeed.toFixed(2)}&right=${rightSpeed.toFixed(2)}&time=0.3`, {
            method: 'POST'
        }).catch(err => console.error(err));

        lastCommandTime = now;
    });

    joystick.on('end', () => {
        fetch(`/commandes?type=joystick&left=0&right=0&time=0.1`, { method: 'POST' })
            .catch(err => console.error(err));
    });

});
