import asyncio, hashlib, hmac, json, os, sqlite3
from datetime import datetime, timedelta
from urllib.parse import parse_qsl
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (Message, InlineKeyboardMarkup, InlineKeyboardButton,
                           WebAppInfo, MenuButtonWebApp)
from aiohttp import web

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL")
PORT = int(os.getenv("PORT", 8080))
DB_PATH = "/tmp/bot.db" if os.path.exists("/tmp") else "bot.db"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

HTML = r"""<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,user-scalable=no,viewport-fit=cover">
<title>App</title><script src="https://telegram.org/js/telegram-web-app.js"></script>
<style>
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent;margin:0;padding:0}
:root{--bg:#0a0a12;--c:rgba(255,255,255,.045);--b:rgba(255,255,255,.08);--t:#eaeaf2;--m:#8a8aa3;--a1:#7c5cff;--a2:#4a9eff}
body{font-family:-apple-system,system-ui,sans-serif;background:var(--bg);color:var(--t);padding-bottom:calc(84px + env(safe-area-inset-bottom));min-height:100vh}
body::before{content:"";position:fixed;inset:0;z-index:-1;background:radial-gradient(600px 400px at 10% -5%,rgba(124,92,255,.35),transparent 60%),radial-gradient(500px 400px at 100% 15%,rgba(74,158,255,.28),transparent 60%),linear-gradient(180deg,#0a0a12,#0d0d18)}
.h{padding:calc(20px + env(safe-area-inset-top)) 20px 12px}
.u{display:flex;align-items:center;gap:12px}
.av{width:48px;height:48px;border-radius:16px;display:grid;place-items:center;font-size:20px;font-weight:700;color:#fff;background:linear-gradient(135deg,var(--a1),var(--a2))}
.ni{flex:1;min-width:0}.nn{font-size:16px;font-weight:600}.ns{font-size:13px;color:var(--m)}
.bp{padding:8px 14px;border-radius:14px;font-weight:600;font-size:14px;background:linear-gradient(135deg,rgba(124,92,255,.25),rgba(74,158,255,.25));border:1px solid rgba(124,92,255,.4)}
main{padding:8px 20px 20px}
.st{font-size:22px;font-weight:700;margin:16px 0 12px}
.ss{color:var(--m);font-size:14px;margin-top:-8px;margin-bottom:16px}
.cd{background:var(--c);border:1px solid var(--b);border-radius:20px;padding:18px;margin-bottom:12px}
.hero{background:linear-gradient(135deg,rgba(124,92,255,.22),rgba(74,158,255,.18));border:1px solid rgba(124,92,255,.35);border-radius:24px;padding:22px}
.hl{font-size:13px;color:rgba(255,255,255,.7);text-transform:uppercase;letter-spacing:1px;font-weight:600}
.hv{font-size:28px;font-weight:800;margin-top:6px}
.hm{margin-top:8px;font-size:14px;color:rgba(255,255,255,.75)}
.sts{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:12px}
.stt{background:var(--c);border:1px solid var(--b);border-radius:18px;padding:16px}
.si{font-size:22px;margin-bottom:8px}.sl{font-size:12px;color:var(--m);text-transform:uppercase}
.sv{font-size:22px;font-weight:700;margin-top:4px}
.pl{position:relative;background:var(--c);border:1px solid var(--b);border-radius:20px;padding:18px;margin-bottom:12px}
.pl.hit{border-color:rgba(124,92,255,.6)}
.pl.hit::before{content:"ТОП";position:absolute;top:12px;right:12px;font-size:10px;font-weight:700;padding:4px 8px;border-radius:8px;background:linear-gradient(135deg,var(--a1),var(--a2));color:#fff}
.pt{font-size:16px;font-weight:600}.pp{font-size:26px;font-weight:800;margin-top:6px}
.pp small{font-size:14px;color:var(--m);margin-left:6px}
.po{font-size:13px;color:var(--m);text-decoration:line-through;margin-left:8px}
.btn{width:100%;margin-top:14px;padding:14px;border:none;border-radius:14px;font-size:15px;font-weight:600;color:#fff;background:linear-gradient(135deg,var(--a1),var(--a2));font-family:inherit}
.btn.g{background:var(--c);border:1px solid var(--b)}
.tx{display:flex;align-items:center;gap:14px;padding:14px 0;border-bottom:1px solid rgba(255,255,255,.05)}
.tx:last-child{border:none}
.ti{width:42px;height:42px;border-radius:14px;display:grid;place-items:center;font-size:18px;background:linear-gradient(135deg,rgba(124,92,255,.25),rgba(74,158,255,.25))}
.tt{font-size:14px;font-weight:600}.td{font-size:12px;color:var(--m);margin-top:2px}
.ta{font-size:15px;font-weight:700;color:#ff5c7a;margin-left:auto}
.rl{display:flex;gap:10px;align-items:center;margin-top:12px;background:rgba(0,0,0,.25);border:1px solid var(--b);border-radius:14px;padding:12px 14px}
.rl span{flex:1;font-size:13px;color:var(--m);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.rl button{background:linear-gradient(135deg,var(--a1),var(--a2));color:#fff;border:none;padding:8px 14px;border-radius:10px;font-size:13px;font-weight:600}
.empty{text-align:center;padding:40px 20px;color:var(--m)}
.nav{position:fixed;left:12px;right:12px;bottom:calc(12px + env(safe-area-inset-bottom));display:grid;grid-template-columns:repeat(4,1fr);background:rgba(20,20,32,.75);border:1px solid var(--b);backdrop-filter:blur(24px);border-radius:22px;padding:8px}
.nb{display:flex;flex-direction:column;align-items:center;gap:3px;background:none;border:none;color:var(--m);padding:8px 4px;border-radius:14px;font-size:10px;font-weight:600;font-family:inherit}
.nb .ico{font-size:20px;line-height:1}
.nb.active{color:#fff;background:linear-gradient(135deg,rgba(124,92,255,.3),rgba(74,158,255,.2))}
.toast{position:fixed;left:50%;bottom:110px;transform:translateX(-50%);background:rgba(30,30,45,.95);border:1px solid var(--b);padding:12px 18px;border-radius:14px;font-size:14px;opacity:0;transition:.3s;z-index:200}
.toast.show{opacity:1}
</style></head><body>
<header class="h"><div class="u">
<div class="av" id="av">·</div>
<div class="ni"><div class="nn" id="un">Загрузка…</div><div class="ns" id="us">@…</div></div>
<div class="bp" id="bp">0 ₽</div></div></header>
<main id="content"></main>
<nav class="nav">
<button class="nb active" data-tab="home"><span class="ico">🏠</span>Главная</button>
<button class="nb" data-tab="extend"><span class="ico">⚡</span>Продлить</button>
<button class="nb" data-tab="history"><span class="ico">📜</span>История</button>
<button class="nb" data-tab="refs"><span class="ico">👥</span>Рефералы</button>
</nav><div class="toast" id="toast"></div>
<script>
const tg=window.Telegram?.WebApp;tg?.ready();tg?.expand();
const ID=tg?.initData||"",C=document.getElementById("content");let me=null,plans=[],hist=[];
function toast(m){const t=document.getElementById("toast");t.textContent=m;t.classList.add("show");setTimeout(()=>t.classList.remove("show"),2000)}
async function api(p,o={}){const r=await fetch(p,{...o,headers:{"Content-Type":"application/json","X-Init-Data":ID,...(o.headers||{})}});if(!r.ok)throw new Error("HTTP "+r.status);return r.json()}
const fd=i=>i?new Date(i).toLocaleDateString("ru-RU",{day:"2-digit",month:"short",year:"numeric"}):"—";
const ini=n=>n?n.trim()[0].toUpperCase():"?";
function home(){const a=me.subscription_until&&new Date(me.subscription_until)>new Date();
C.innerHTML=`<div class="st">Привет, ${me.first_name||"друг"} 👋</div>
<div class="hero"><div class="hl">Статус подписки</div><div class="hv">${a?"Активна":"Не активна"}</div>
<div class="hm">${a?"до "+fd(me.subscription_until):"Оформи подписку"}</div></div>
<div class="sts"><div class="stt"><div class="si">💰</div><div class="sl">Баланс</div><div class="sv">${me.balance} ₽</div></div>
<div class="stt"><div class="si">👥</div><div class="sl">Рефералы</div><div class="sv">${me.referrals_count}</div></div></div>
<div class="st" style="font-size:17px;margin-top:20px">Быстрые действия</div>
<button class="btn" onclick="tab('extend')">⚡ Продлить подписку</button>
<button class="btn g" style="margin-top:10px" onclick="tab('refs')">👥 Пригласить друга</button>`}
function ext(){C.innerHTML=`<div class="st">Продлить подписку</div><div class="ss">Выбери тариф</div>
${plans.map(p=>`<div class="pl ${p.hit?"hit":""}"><div class="pt">${p.title}</div>
<div class="pp">${p.price} ₽<small>/ ${p.title}</small><span class="po">${p.old} ₽</span></div>
<button class="btn" onclick="buy('${p.id}')">Оплатить ${p.price} ₽</button></div>`).join("")}`}
function histr(){if(!hist.length){C.innerHTML=`<div class="st">История покупок</div><div class="empty">📭<br>Покупок пока нет</div>`;return}
C.innerHTML=`<div class="st">История покупок</div><div class="cd" style="padding:6px 18px">
${hist.map(h=>`<div class="tx"><div class="ti">⚡</div><div><div class="tt">${h.title}</div><div class="td">${fd(h.created_at)}</div></div><div class="ta">−${h.amount} ₽</div></div>`).join("")}</div>`}
function refs(){C.innerHTML=`<div class="st">Реферальная программа</div><div class="ss">Приглашай друзей — 50 ₽ за каждого</div>
<div class="cd"><div class="sl">Твоя ссылка</div><div class="rl"><span id="rl">${me.ref_link}</span><button onclick="cp()">Копировать</button></div>
<div class="sts" style="margin-top:16px"><div class="stt"><div class="si">👥</div><div class="sl">Приглашено</div><div class="sv">${me.referrals_count}</div></div>
<div class="stt"><div class="si">💎</div><div class="sl">Заработано</div><div class="sv">${me.referrals_earned} ₽</div></div></div></div>
<button class="btn" onclick="sh()">📤 Поделиться</button>`}
async function buy(id){try{tg?.HapticFeedback?.impactOccurred("medium");
const r=await api("/api/buy",{method:"POST",body:JSON.stringify({plan_id:id})});
if(!r.ok||!r.link){toast("Ошибка");return}
tg.openInvoice(r.link,async(s)=>{if(s==="paid"){toast("Оплачено ✅");
tg?.HapticFeedback?.notificationOccurred("success");await rl();tab("home")}
else if(s==="cancelled"){toast("Отменено")}else{toast("Ошибка оплаты")}})
}catch(e){toast("Ошибка: "+e.message)}}
function cp(){navigator.clipboard.writeText(document.getElementById("rl").textContent);toast("Скопировано")}
function sh(){tg?.openTelegramLink?.(`https://t.me/share/url?url=${encodeURIComponent(me.ref_link)}&text=Залетай!`)}
function tab(t){document.querySelectorAll(".nb").forEach(b=>b.classList.toggle("active",b.dataset.tab===t));
if(t==="home")home();if(t==="extend")ext();if(t==="history")histr();if(t==="refs")refs()}
async function rl(){me=await api("/api/me");hist=await api("/api/history");
document.getElementById("av").textContent=ini(me.first_name);
document.getElementById("un").textContent=me.first_name||"Пользователь";
document.getElementById("us").textContent=me.username?"@"+me.username:"ID "+me.user_id;
document.getElementById("bp").textContent=me.balance+" ₽"}
(async()=>{try{plans=await api("/api/plans");await rl();tab("home")}catch(e){C.innerHTML=`<div class="empty">Ошибка: ${e.message}</div>`}})();
document.querySelectorAll(".nb").forEach(b=>b.onclick=()=>tab(b.dataset.tab));
</script></body></html>"""

def db():
    c=sqlite3.connect(DB_PATH); c.row_factory=sqlite3.Row; return c

def init_db():
    with db() as c:
        c.executescript("""CREATE TABLE IF NOT EXISTS users(user_id INTEGER PRIMARY KEY,username TEXT,first_name TEXT,balance INTEGER DEFAULT 0,subscription_until TEXT,referred_by INTEGER,created_at TEXT);
        CREATE TABLE IF NOT EXISTS purchases(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER,title TEXT,amount INTEGER,status TEXT,created_at TEXT);""")

def gu(uid,username="",first_name="",ref=None):
    with db() as c:
        r=c.execute("SELECT * FROM users WHERE user_id=?",(uid,)).fetchone()
        if r: return dict(r)
        c.execute("INSERT INTO users(user_id,username,first_name,referred_by,created_at) VALUES(?,?,?,?,?)",(uid,username or "",first_name or "",ref,datetime.utcnow().isoformat()))
        return dict(c.execute("SELECT * FROM users WHERE user_id=?",(uid,)).fetchone())

def valid(init):
    try:
        p=dict(parse_qsl(init,keep_blank_values=True)); h=p.pop("hash",None)
        if not h: return None
        ck="\n".join(f"{k}={v}" for k,v in sorted(p.items()))
        s=hmac.new(b"WebAppData",BOT_TOKEN.encode(),hashlib.sha256).digest()
        if not hmac.compare_digest(hmac.new(s,ck.encode(),hashlib.sha256).hexdigest(),h): return None
        return json.loads(p["user"]) if "user" in p else None
    except: return None

def auth(req): return valid(req.headers.get("X-Init-Data",""))

async def a_me(req):
    u=auth(req)
    if not u: return web.json_response({"error":"unauth"},status=401)
    uid=u["id"]; row=gu(uid,u.get("username"),u.get("first_name"))
    with db() as c: cnt=c.execute("SELECT COUNT(*) c FROM users WHERE referred_by=?",(uid,)).fetchone()["c"]
    bi=await bot.me()
    return web.json_response({"user_id":uid,"first_name":row["first_name"],"username":row["username"],"balance":row["balance"],"subscription_until":row["subscription_until"],"referrals_count":cnt,"referrals_earned":cnt*50,"ref_link":f"https://t.me/{bi.username}?start=ref_{uid}"})
async def a_plans(req): return web.json_response([{"id":"1m","title":"1 месяц","price":299,"old":399,"days":30,"hit":False},{"id":"3m","title":"3 месяца","price":749,"old":1197,"days":90,"hit":True},{"id":"12m","title":"12 месяцев","price":2490,"old":4788,"days":365,"hit":False}])
async def a_invoice(req):
    u = auth(req)
    if not u: return web.json_response({"error":"unauth"}, status=401)
    b = await req.json()
    plan = b.get("plan_id")
    if plan not in PRICES: return web.json_response({"error":"bad"}, status=400)
    stars, days = PRICES[plan]
    payload = json.dumps({"u": u["id"], "d": days})
    link = await bot.create_invoice_link(
        title="Подписка SARVPN",
        description=f"VPN на {days} дней",
        payload=payload,
        currency="XTR",
        prices=[LabeledPrice(label=f"VPN {days} дн.", amount=stars)])
    return web.json_response({"ok": True, "link": link})

async def a_buy(req):
    u=auth(req)
    if not u: return web.json_response({"error":"unauth"},status=401)
    b=await req.json(); pl={"1m":{"title":"1 месяц","price":299,"days":30},"3m":{"title":"3 месяца","price":749,"days":90},"12m":{"title":"12 месяцев","price":2490,"days":365}}
    p=pl.get(b.get("plan_id"))
    if not p: return web.json_response({"error":"bad"},status=400)
    uid=u["id"]; now=datetime.utcnow()
    with db() as c:
        r=c.execute("SELECT subscription_until FROM users WHERE user_id=?",(uid,)).fetchone(); base=now
        if r and r["subscription_until"]:
            try: base=max(datetime.fromisoformat(r["subscription_until"]),now)
            except: pass
        until=(base+timedelta(days=p["days"])).isoformat()
        c.execute("UPDATE users SET subscription_until=? WHERE user_id=?",(until,uid))
        c.execute("INSERT INTO purchases(user_id,title,amount,status,created_at) VALUES(?,?,?,?,?)",(uid,p["title"],p["price"],"success",now.isoformat()))
    return web.json_response({"ok":True,"subscription_until":until})

async def a_hist(req):
    u=auth(req)
    if not u: return web.json_response({"error":"unauth"},status=401)
    with db() as c: rows=c.execute("SELECT title,amount,status,created_at FROM purchases WHERE user_id=? ORDER BY id DESC LIMIT 50",(u["id"],)).fetchall()
    return web.json_response([dict(r) for r in rows])

async def a_index(req): return web.Response(text=HTML,content_type="text/html")

dp.pre_checkout_query()
async def on_pre_checkout(q: PreCheckoutQuery):
    await q.answer(ok=True)

@dp.message(F.successful_payment)
async def on_payment(m: Message):
    try:
        p = json.loads(m.successful_payment.invoice_payload)
        uid = p["u"]; days = p["d"]
    except Exception:
        return
    now = datetime.utcnow()
    with db() as c:
        r = c.execute("SELECT subscription_until FROM users WHERE user_id=?", (uid,)).fetchone()
        base = now
        if r and r["subscription_until"]:
            try: base = max(datetime.fromisoformat(r["subscription_until"]), now)
            except: pass
        until = (base + timedelta(days=days)).isoformat()
        c.execute("UPDATE users SET subscription_until=? WHERE user_id=?", (until, uid))
        c.execute("INSERT INTO purchases(user_id,title,amount,status,created_at) VALUES(?,?,?,?,?)",
                  (uid, f"VPN {days} дн.", m.successful_payment.total_amount, "success", now.isoformat()))
    await m.answer(f"✅ Оплата получена! Подписка активна до {until[:10]}")




async def start(m:Message):
    a=m.text.split(maxsplit=1); ref=None
    if len(a)>1 and a[1].startswith("ref_"):
        try: ref=int(a[1][4:])
        except: pass
    gu(m.from_user.id,m.from_user.username,m.from_user.first_name,ref if ref!=m.from_user.id else None)
    kb=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🚀 Открыть приложение",web_app=WebAppInfo(url=WEBAPP_URL))]])
    await m.answer(f"Привет, <b>{m.from_user.first_name}</b>!\n\nОткрой Mini App 👇",reply_markup=kb,parse_mode="HTML")

async def main():
    init_db()
    app=web.Application()
    app.router.add_get("/",a_index)
    app.router.add_get("/api/me",a_me)
    app.router.add_get("/api/plans",a_plans)
    app.router.add_post("/api/buy", a_invoice)
    app.router.add_get("/api/history",a_hist)
    runner=web.AppRunner(app); await runner.setup()
    await web.TCPSite(runner,"0.0.0.0",PORT).start()
    await bot.set_chat_menu_button(menu_button=MenuButtonWebApp(text="Приложение",web_app=WebAppInfo(url=WEBAPP_URL)))
    await dp.start_polling(bot)

if __name__=="__main__":
    asyncio.run(main())
