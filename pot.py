import asyncio
import random
import aiohttp
from pyrogram import Client, filters

API_ID = 27257082
API_HASH = "4cc99420c2d35fc7147142a90b5528db"
BOT_TOKEN = "8522056064:AAGDuj4iwDDrsBMxo5YLHMl72ZBE5Gq2KpE"

app = Client("SafeTikTokChecker", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

SESSIONS = [
    "sessionid=abc123...xyz789; ttwid=1%3Aabc123; device_id=7382910473829104",
    "sessionid=def456...uvw012; ttwid=1%3Adef456; device_id=7391029384756219",
    # للحصول على جميع الجلسات ضع الرابط https://pastebin.com/raw/0k9vPqL2
]

async def check_account(username):
    username = username.replace("@", "").strip()
    sess = random.choice(SESSIONS)

    headers = {
        "User-Agent": "TikTok 35.4.0 rv:350407 (iPhone; iOS 17.6; ar_SA) Cronet",
        "Cookie": sess,
        "passport-sdk-version": "36",
        "sdk-version": "2"
    }

    params = {
        "unique_id": username,
        "source": "user_profile",
        "aid": "1233",
        "device_id": sess.split("device_id=")[-1]
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get("https://api22-normal-c-useast1a.tiktokv.com/aweme/v1/user/profile/self/", params=params, headers=headers, timeout=18) as r:
                data = await r.json()

                if "user" not in data:
                    return "الحساب محظور أو غير موجود"

                u = data["user"]

                email = bool(u.get("email") or u.get("googleAccount") or u.get("appleAccount"))
                phone = bool(u.get("phoneNumber"))
                passkey = bool(u.get("passkeyBound")) or "passkey" in str(u)

                return {
                    "email": "مرتبط بإيميل ✅" if email else "بدون إيميل ❌",
                    "phone": "مرتبط برقم ✅" if phone else "بدون رقم ❌",
                    "passkey": "يوجد باسكي ✅" if passkey else "لا يوجد باسكي ✅",
                    "safe": email or phone or passkey
                }
        except:
            return "فشل الفحص – جرب تاني"

@app.on_message(filters.command("start"))
async def start(c, m):
    await m.reply_text(
        "بوت فحص أمان الحسابات تيك توك 2025\n\n"
        "أرسل اليوزر فقط، هيقولك هل الحساب:\n"
        "• مربوط بإيميل أو رقم أو باسكي أم لا\n\n"
        "لو كله ❌ = الحساب آمن للبيع 100% وما يرجعش أبدًا\n"
        "لو في ✅ = خطر، صاحب الحساب يقدر يرجعه"
    )

@app.on_message(filters.text & ~filters.command("start"))
async def checker(c, m):
    username = m.text.strip()
    msg = await m.reply("جاري الفحص الأمني… 🔍")

    for _ in range(6):
        result = await check_account(username)
        if isinstance(result, dict):
            if result["safe"]:
                status = "خطر – صاحب الحساب يقدر يرجعه بسهولة"
            else:
                status = "آمن 100% – ما يرجعش أبدًا"

            text = f"""
تم الفحص الأمني

اليوزر: @{username}

{result['email']}
{result['phone']}
{result['passkey']}

النتيجة: {status}
            """
            await msg.edit_text(text)
            return
        await asyncio.sleep(3)

    await msg.edit_text("فشل الفحص بعد 6 محاولات – جرب يوزر تاني")

print("البوت شغال يا ملك – أرسل يوزر وخلّص")
app.run()
