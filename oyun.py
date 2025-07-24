import asyncio
from aiogram import types
from roles import assign_roles, role_descriptions
from collections import defaultdict

class MafiaGame:
    def __init__(self, bot):
        self.bot = bot
        self.players = {}  # user_id -> User objesi
        self.state = "waiting"  # waiting, started, day, night
        self.votes = defaultdict(list)
        self.roles = {}  # user_id -> role adı
        self.killed = set()
        self.day_task = None
        self.night_task = None

    async def new_game(self, msg: types.Message):
        if self.state != "waiting":
            await msg.answer("⚠️ Hazırda bir oyun davam edir.")
            return
        self.players = {}
        self.killed = set()
        self.roles = {}
        self.state = "waiting"
        await msg.answer("🎲 Yeni oyun yaradıldı! Qoşulmaq üçün /qosul yazın.")

    async def join(self, msg: types.Message):
        user = msg.from_user
        if self.state != "waiting":
            await msg.answer("❌ Oyun artıq başladı, qoşula bilməzsən.")
            return
        if user.id in self.players:
            await msg.answer("✅ Zaten qoşulmusan.")
            return
        self.players[user.id] = user
        await msg.answer(f"👤 {user.full_name} oyuna qoşuldu. ({len(self.players)} nəfər)")

    async def start_game(self, msg: types.Message):
        if self.state != "waiting":
            await msg.answer("❌ Oyun artıq başlayıb.")
            return
        if len(self.players) < 5:
            await msg.answer("🚫 Oyun başlatmaq üçün minimum 5 nəfər lazımdır.")
            return
        self.state = "started"
        self.roles = assign_roles(list(self.players.values()))
        await msg.answer("🕹️ Oyun başladı! Rollar göndərilir...")

        for uid, role in self.roles.items():
            desc = role_descriptions.get(role, "")
            try:
                await self.bot.send_message(uid, f"🎭 Sənin rolun: *{role}*\n\n{desc}", parse_mode="Markdown")
            except:
                pass

        await asyncio.sleep(3)
        await self.start_day()

    async def start_day(self):
        self.state = "day"
        self.votes = defaultdict(list)
        alive = [u.full_name for uid, u in self.players.items() if uid not in self.killed]
        text = "🌞 *Gündüz başladı!*\nYaşayanlar:\n" + "\n".join(alive)
        await self.broadcast(text)
        # Gündüz müddəti (timer) avtomatik olaraq 60 saniyə olsun
        if self.day_task:
            self.day_task.cancel()
        self.day_task = asyncio.create_task(self.day_timer())

    async def day_timer(self):
        await asyncio.sleep(60)  # 60 saniyə gündüz davam edir
        await self.end_day()

    async def end_day(self):
        # Səsverməni yoxla
        if not self.votes:
            await self.broadcast("Heç kimə səs verilmədi.")
        else:
            # Ən çox səs alan oyunçu öldürülür
            max_votes = max(len(v) for v in self.votes.values())
            candidates = [uid for uid, v in self.votes.items() if len(v) == max_votes]
            if len(candidates) == 1:
                killed_id = candidates[0]
                if killed_id not in self.killed:
                    self.killed.add(killed_id)
                    name = self.players[killed_id].full_name
                    await self.broadcast(f"☠️ {name} öldürüldü.")
            else:
                await self.broadcast("Səsvermədə bərabərlik oldu. Heç kim öldürülmədi.")
        # Gecə başlayır
        await asyncio.sleep(2)
        await self.start_night()

    async def start_night(self):
        self.state = "night"
        await self.broadcast("🌚 *Gecə başladı!*\nRollar öz fəaliyyətlərini yerinə yetirə bilər.")
        if self.night_task:
            self.night_task.cancel()
        self.night_task = asyncio.create_task(self.night_timer())

    async def night_timer(self):
        await asyncio.sleep(30)  # 30 saniyə gecə davam edir
        await self.end_night()

    async def end_night(self):
        # Burada gecə fəaliyyəti icra olunur (kill, heal, investigate və s.)
        # Hal-hazırda sadə nümunə:
        await self.broadcast("🌞 Gündüz başlayır!")
        await self.start_day()

    async def broadcast(self, text):
        for uid in self.players:
            if uid not in self.killed:
                try:
                    await self.bot.send_message(uid, text, parse_mode="Markdown")
                except:
                    pass

    async def vote(self, msg: types.Message):
        if self.state != "day":
            await msg.answer("❌ Səsvermə yalnız gündüz keçirilir.")
            return
        voter = msg.from_user.id
        if voter in self.killed:
            await msg.answer("☠️ Ölü oyunçular səs verə bilməz.")
            return
        if not msg.reply_to_message:
            await msg.answer("🔁 Səs vermək üçün mesajı cavablandır.")
            return
        target = msg.reply_to_message.from_user.id
        if target not in self.players or target in self.killed:
            await msg.answer("❌ Bu oyunçu mövcud deyil ya da ölüdür.")
            return
        # Səs ver
        self.votes[target].append(voter)
        await msg.answer("✅ Səsiniz qeydə alındı.")

    async def show_role(self, msg: types.Message):
        uid = msg.from_user.id
        if uid not in self.roles:
            await msg.answer("❌ Oyunda deyilsiniz.")
            return
        role = self.roles[uid]
        desc = role_descriptions.get(role, "")
        await msg.answer(f"🎭 Rolunuz: *{role}*\n\n{desc}", parse_mode="Markdown")

    async def show_players(self, msg: types.Message):
        text = "👥 Oyunçular:\n"
        for uid, user in self.players.items():
            status = "☠️" if uid in self.killed else "✅"
            text += f"{status} {user.full_name}\n"
        await msg.answer(text)

    async def show_roles(self, msg: types.Message):
        if self.state != "waiting":
            await msg.answer("❌ Oyun zamanı rollar açıqlanmır.")
            return
        await msg.answer("🎭 Mövcud rollar:\n" + "\n".join(role_descriptions.keys()))
