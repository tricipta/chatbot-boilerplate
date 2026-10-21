const { default: makeWASocket, useMultiFileAuthState } = require('@whiskeysockets/baileys')
const axios = require('axios')

async function startBot(botName, portApi) {
    const { state, saveCreds } = await useMultiFileAuthState(`auth_${botName}`)
    const sock = makeWASocket({ 
        auth: state,
        printQRInTerminal: false
    })

    // MINTA PAIRING CODE KALO BELUM LOGIN
    if (!sock.authState.creds.registered) {
        const phoneNumber = "62881022758184"
        setTimeout(async () => {
            const code = await sock.requestPairingCode(phoneNumber)
            console.log(`\n🔥 KODE PAIRING UNTUK ${botName}: ${code} 🔥`)
            console.log(`Buka WA Business -> Setelan -> Perangkat Tertaut -> Tautkan dengan nomor telepon -> Masukin kode ini\n`)
        }, 3000)
    }

    sock.ev.on('creds.update', saveCreds)

    sock.ev.on('connection.update', async (update) => {
        const { connection, lastDisconnect } = update
        if (connection === 'close') {
            const shouldReconnect = lastDisconnect?.error?.output?.statusCode !== 401
            if (shouldReconnect) startBot(botName, portApi)
        }
        if (connection === 'open') {
            console.log(`✅ ${botName} CONNECTED!`)
        }
    })

    sock.ev.on('messages.upsert', async ({ messages }) => {
        const msg = messages[0]
        if (!msg.message || msg.key.fromMe) return
        const text = msg.message.conversation || msg.message.extendedTextMessage?.text
        const sender = msg.key.remoteJid
        if (!text) return
        try {
            const res = await axios.post(`http://127.0.0.1:${portApi}/chat`, { message: text })
            await sock.sendMessage(sender, { text: res.data.answer || "Error" })
        } catch (e) { console.error(e.message) }
    })
}

startBot('sekolah', 8000)