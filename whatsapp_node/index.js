// === Dependencias ===
const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const qrcode = require('qrcode');
const {Client, LocalAuth, MessageMedia} = require('whatsapp-web.js');

// === Variables Globales ===
let client;
let lastQR = null;
const SESSION_DIR = path.join(__dirname, 'sessions');
const CLIENT_ID = 'session';
const SESSION_PATH = path.join(SESSION_DIR, CLIENT_ID);
let clientStatus = {
    status: 'inicializando',  // otros posibles: 'qr', 'listo', 'desconectado'
    connected: false,
};

// === Funciones Auxiliares ===
const fileExists = (filePath) => fs.existsSync(filePath);

// === Inicializar Cliente WhatsApp ===
function createWhatsAppClient() {
    const newClient = new Client({
        authStrategy: new LocalAuth({dataPath: './sessions'}),
        puppeteer: {
            headless: true,
            executablePath: '/usr/bin/chromium',
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--disable-gpu',
                '--disable-software-rasterizer',
                '--single-process'
            ],
            dumpio: true,
        },
        takeoverOnConflict: true,
        qrTimeoutMs: 0,
    });

    newClient.on('qr', qr => {
        lastQR = qr;
        clientStatus.status = 'qr';
        clientStatus.connected = false;
        console.log('🧾 QR actualizado');
    });

    newClient.on('authenticated', () => {
        console.log('🔐 Autenticado con éxito');
    });

    newClient.on('ready', () => {
        clientStatus.status = 'listo';
        clientStatus.connected = true;
        lastQR = null;
        console.log('✅ Cliente de WhatsApp listo.');
    });

    newClient.on('disconnected', () => {
        clientStatus.status = 'desconectado';
        clientStatus.connected = false;
        console.log('❌ Cliente desconectado');
    });

    newClient.initialize();
    return newClient;
}

// === Lógica de envío de medios ===
function createSendMediaHandler(client) {
    return async (req, res) => {
        const {number, message, image_path} = req.body;

        if (!number || !message || !image_path) {
            return res.status(400).json({error: 'Faltan datos: number, message o image_path'});
        }

        const chatId = number.includes('@c.us') ? number : `${number}@c.us`;
        const absolutePath = path.resolve(__dirname, image_path);

        if (!fileExists(absolutePath)) {
            return res.status(404).json({error: `Archivo no encontrado: ${image_path}`});
        }

        try {
            const media = MessageMedia.fromFilePath(absolutePath);
            await client.sendMessage(chatId, media, {caption: message});

            console.log(`📤 Enviado a ${chatId}`);
            return res.status(200).json({status: 'Mensaje enviado', number: chatId});

        } catch (error) {
            console.error(`❌ Error al enviar a ${chatId}:`, error);
            return res.status(500).json({error: error.message, number: chatId});
        }
    };
}

// === Express App ===
const app = express();
app.use(cors());
app.use(express.json());

// === Inicializar Cliente y Handlers ===
client = createWhatsAppClient();
app.post('/send-media', createSendMediaHandler(client));

// === Endpoint: Reset limpio ===
app.post('/reset-clean', async (_req, res) => {
    try {
        console.log('🔄 Reiniciando cliente WhatsApp...');

        await client.destroy();

        if (fileExists(SESSION_PATH)) {
            fs.rmSync(SESSION_PATH, {recursive: true, force: true});
            console.log('🗑️ Sesión eliminada');
        }

        client = createWhatsAppClient();
        return res.json({status: 'Reinicio iniciado'});

    } catch (error) {
        console.error('❌ Error en /reset-clean:', error);
        return res.status(500).json({error: 'No se pudo reiniciar sesión'});
    }
});

// === Endpoint: Obtener QR ===
app.get('/qr', async (_req, res) => {
    if (!lastQR) return res.json({qr: null});

    try {
        const dataUrl = await qrcode.toDataURL(lastQR);
        return res.json({qr: dataUrl});
    } catch (error) {
        console.error('❌ Error generando QR base64:', error);
        return res.status(500).json({error: 'No se pudo generar el QR'});
    }
});

// === Endpoint: Obtener estado ===
app.get('/status', (_req, res) => {
    return res.json(clientStatus);
});

// === Iniciar Servidor ===
const PORT = 3000;
app.listen(PORT, () => {
    console.log(`🚀 Microservicio WhatsApp corriendo en http://localhost:${PORT}`);
});
