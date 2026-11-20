// --- FASE 1: ESCUCHAR EL CLIC DEL USUARIO ---
document.getElementById('btn-analizar').addEventListener('click', async () => {
    const divResultado = document.getElementById('resultado');
    divResultado.innerHTML = "Analizando pantalla... 🕵️‍♂️";

    // 1. Obtener la pestaña actual de Chrome
    let [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

    // 2. Inyectar nuestro "espía ninja" en la página de X
    chrome.scripting.executeScript({
        target: { tabId: tab.id },
        function: extraerDatosDeLaPantalla,
    }, async (resultados) => {
        
        const datosExtraidos = resultados[0].result;
        
        if (datosExtraidos.error) {
            divResultado.innerHTML = "❌ Por favor, entra al perfil de un usuario.";
            return;
        }

        // 3. Enviar los datos capturados a la ruta B2C de tu API local
        try {
            const respuestaAPI = await fetch('http://localhost:8000/predict_extension', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(datosExtraidos)
            });

            const resultado = await respuestaAPI.json();

            // --- NUEVO ESCUDO PROTECTOR ---
            if (!respuestaAPI.ok) {
                console.error("Datos que provocaron el error:", datosExtraidos);
                divResultado.innerHTML = `⚠️ La API rechazó los datos. Revisa la consola negra de Python.`;
                return; 
            }
            // ------------------------------

            // 4. Mostrar el resultado
            if (resultado.prediction_class === 1) {
                divResultado.innerHTML = `🤖 ¡ALERTA BOT!<br><span class="bot">Probabilidad: ${Math.round(resultado.bot_probability * 100)}%</span>`;
            } else {
                divResultado.innerHTML = `👤 Parece humano.<br><span class="humano">Probabilidad Bot: ${Math.round(resultado.bot_probability * 100)}%</span>`;
            }

        } catch (error) {
            divResultado.innerHTML = "⚠️ Error conectando con la API local. Comprueba que la consola negra de Python esté encendida.";
        }
    });
});

// --- FASE 2: EL "NINJA" QUE SE EJECUTA DENTRO DE TWITTER ---
function extraerDatosDeLaPantalla() {
    try {
        const urlParts = window.location.pathname.split('/');
        const username = urlParts[1];

        if (!username || username === 'home' || username === 'explore' || username === 'messages') {
            return { error: true };
        }

        // --- FUNCIÓN MATEMÁTICA TODOTERRENO BLINDADA ---
        const parsearNumero = (texto) => {
            if (!texto) return 0;
            let numStr = texto.toLowerCase().trim();

            let soloNumeros = numStr.replace(/[^0-9,\.]/g, '');
            // LA CLAVE: Si tras limpiar las letras no queda ningún número, devuelve 0 y evita el NaN
            if (!soloNumeros) return 0; 

            let multiplicador = 1;
            if (numStr.includes('k') || numStr.includes('mil')) multiplicador = 1000;
            if (numStr.includes('m') || numStr.includes('mln')) multiplicador = 1000000;

            if (multiplicador > 1) {
                soloNumeros = soloNumeros.replace(',', '.'); 
                return Math.round(parseFloat(soloNumeros) * multiplicador) || 0;
            } else {
                soloNumeros = soloNumeros.replace(/[,.]/g, ''); 
                return parseInt(soloNumeros, 10) || 0;
            }
        };

        // --- EXTRACCIÓN DEL DOM ---
        let biografia = "";
        try { biografia = document.querySelector('[data-testid="UserDescription"]').innerText; } catch(e) {}

        let ubicacion = "";
        try { ubicacion = document.querySelector('[data-testid="UserLocation"]').innerText; } catch(e) {}

        let estaVerificado = false;
        try { estaVerificado = document.querySelector('[data-testid="icon-verified"]') !== null; } catch(e) {}

        let numSeguidores = 0;
        let numSeguidos = 0;
        try { 
            let links = document.querySelectorAll(`a[href$="/followers"], a[href$="/verified_followers"], a[href$="/following"]`);
            links.forEach(link => {
                let texto = link.innerText;
                if (link.href.includes('following')) numSeguidos = parsearNumero(texto);
                if (link.href.includes('followers')) numSeguidores = parsearNumero(texto);
            });
        } catch(e) {}

        let fechaCreacion = "Desconocida";
        try {
            let itemsPerfil = document.querySelectorAll('[data-testid="UserProfileHeader_Items"] span');
            itemsPerfil.forEach(span => {
                let texto = span.innerText.toLowerCase();
                if (texto.includes('se unió') || texto.includes('joined')) {
                    fechaCreacion = span.innerText; 
                }
            });
        } catch(e) {}

        let numPosts = 0;
        try {
            let h2Elements = document.querySelectorAll('h2[role="heading"]');
            if (h2Elements.length > 0) {
                let headerText = h2Elements[0].nextSibling.innerText; 
                numPosts = parsearNumero(headerText);
            }
        } catch(e) {}

        let esAvatarPorDefecto = false;
        try {
            let avatarImg = document.querySelector('img[src*="profile_images"]');
            if (avatarImg && avatarImg.src.includes('default_profile_images')) {
                esAvatarPorDefecto = true;
            }
        } catch(e) {}

        return {
            screen_name: username,
            followers_count: numSeguidores,
            following_count: numSeguidos,
            created_at: fechaCreacion,
            account_age_days: 1000,
            default_profile_image: esAvatarPorDefecto, 
            default_profile: false,
            has_description: biografia.trim().length > 0,
            description: biografia,
            verified: estaVerificado,
            has_lang: true,
            lang: "es", 
            location: ubicacion,
            statuses_count: numPosts,
            average_tweets_per_day: 1.5,
            geo_enabled: ubicacion.trim().length > 0,
            id: Math.floor(Math.random() * 1000000000) 
        };
    } catch (e) {
        return { error: true, message: e.message };
    }
}