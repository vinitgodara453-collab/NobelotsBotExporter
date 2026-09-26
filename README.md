# 🤖 Nobelots Acc Store Telegram Bot - Complete Setup & Panel Guide

Ye bot complete **Digital Accounts Store, SMS/OTP Virtual Numbers aur SMM Social Media Services** ko ek hi Telegram Bot me seamlessly connect karta hai.

---

## 🔌 Isme Konsa Panel Connect Hota Hai? (Connected Panels Breakdown)

Is bot ke andar 4 tarah ke main panels connect hote hain:

### 1. SMM Reseller Panel (Social Media Growth)
* **Standard:** SMM v2 Standard API
* **Supported Panels:** IndianSmartPanel, JustAnotherPanel, SMMKings, Peakerr, TopSMM ya koi bhi SmartPanel / PerfectPanel based website.
* **API Details:**
  * Endpoint: `POST https://your-panel.com/api/v2`
  * Parameters: `key`, `action=services`, `action=add`, `action=status`, `action=balance`
* **Function:** Jab user followers, Telegram members ya views buy karta hai, bot automatically backend se API call karke order place karta hai aur user ko tracking link deta hai.

### 2. SMS / OTP Virtual Number Panel (Temporary Numbers)
* **Supported Providers:** 
  * **SMS-Activate.org / .io** (Most Popular)
  * **5SIM.net**
  * **SMSPVA / Vak-SMS**
* **API Details:**
  * Endpoint: `https://api.sms-activate.org/stubs/handler_api.php?api_key=...&action=getNumber&service=tg&country=0`
* **Function:** Indian (+91), USA (+1), Russia (+7) temporary numbers provide karta hai Telegram/WhatsApp verification ke liye aur real-time SMS code deliver karta hai.

### 3. Digital Accounts Stock Panel (Auto-Delivery Database)
* **In-built Panel:** `store_database.json` / SQLite database
* **Products:** Netflix 4K UHD, Amazon Prime, Aged Telegram Accounts (Session + Tdata), Aged Instagram (2015-2020), Gmail with 2FA, BGMI/FreeFire IDs.
* **Function:** Auto-stock popping. User balance se pay karta hai -> Bot 1 second me `email:password` ya download link user ko private chat me de deta hai.

### 4. Payment Gateway Panel (UPI QR / Crypto)
* **UPI Auto / Manual QR:** Dynamic `upi://pay?pa=...&am=...&cu=INR` QR Code generate karta hai.
* **UTR Verification:** User payment karke 12-digit UTR enter karta hai. Admin panel se 1-click approve hota hai ya Auto-Gateway se verify hoke user ke wallet me instant credit ho jata hai.

---

## 🚀 How to Run the Bot (Step-by-Step Tutorial)

### Step 1: Create Telegram Bot Token
1. Telegram open karein aur **@BotFather** search karein.
2. `/newbot` command bhejein.
3. Bot ka Name (e.g. `Nobelots Acc Store`) aur Username (e.g. `MyNobelotsStoreBot`) enter karein.
4. BotFather aapko ek **HTTP API TOKEN** dega. Ise copy kar lein.

### Step 2: VPS ya Computer Setup (Ubuntu / Linux / Windows)
```bash
# 1. Repository clone ya files folder me jayein
mkdir nobelots-bot && cd nobelots-bot

# 2. Node.js dependencies install karein
npm install

# 3. .env file create karein
cp .env.example .env
nano .env   # (Apna BOT_TOKEN, ADMIN_ID, SMM_API_KEY enter karein)

# 4. Bot start karein
node bot.js
```

### 24/7 Hosting with PM2 (Background Runner)
```bash
npm install -g pm2
pm2 start bot.js --name "nobelots-bot"
pm2 startup
pm2 save
```

---

## 👑 Admin Commands
* `/admin` - View store stats & dashboard
* `/addstock <prod_id> <data>` - Add new credentials in bulk
* `/addbal <telegram_id> <amount>` - Add funds to user wallet
* `/broadcast <message>` - Send promo broadcast to all users
