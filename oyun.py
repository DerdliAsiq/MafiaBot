import asyncio
from aiogram import types
from roles import assign_roles, rolu_gore_emoji, ROLE_TESVIR
from collections import defaultdict

MIN_OYUNCU = 5
MAX_OYUNCU = 25

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
        self.lovers = []
        self.heal_target = None
        self.kill_targets = []
        self.investigate_targets = []
        self.psychopath_target = None
        self.curse_target = None

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
        if len(self.players) >= MAX_OYUNCU:
            await msg.answer("❌ Maksimum oyunçu sayına çatılıb.")
            return
        self.players[user.id] = user
        await msg.answer(f"👤 {user.full_name} oyuna qoşuldu. ({len(self.players)} nəfər)")

    async def start_game(self, msg: types.Message):
        if self.state != "waiting":
            await msg.answer("❌ Oyun artıq başlayıb.")
            return
        if len(self.players) < MIN_OYUNCU:
            await msg.answer("🚫 Oyun başlatmaq üçün minimum 5 nəfər lazımdır.")
            return
        self.state = "started"
        self.roles = assign_roles(list(self.players.values()))
        self.lovers = self.roles.get("aşiqlər", [])
        await msg.answer("🕹️ Oyun başladı! Rollar göndərilir...")

        for uid, role in self.roles.items():
            if uid == "aşiqlər":
                continue
            desc = ROLE_TESVIR.get(role, "")
            emoji = rolu_gore_emoji(role)
            try:
                await self.bot.send_message(uid, f"🎭 Sənin rolun: *{role}* {emoji}\n\n{desc}", parse_mode="Markdown")
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
        if self.day_task:
            self.day_task.cancel()
        self.day_task = asyncio.create_task(self.day_timer())

    async def day_timer(self):
        await asyncio.sleep(60)  # 60 saniyə gündüz davam edir
        await self.end_day()

    async def end_day(self):
        if not self.votes:
            await self.broadcast("Heç kimə səs verilmədi.")
        else:
            max_votes = max(len(v) for v in self.votes.values())
            candidates = [uid for uid, v in self.votes.items() if len(v) == max_votes]
            if len(candidates) == 1:
                killed_id = candidates[0]
                if killed_id not in self.killed:
                    self.killed.add(killed_id)
                    name = self.players[killed_id].full_name
                    await self.broadcast(f"☠️ {name} edam edildi.")
                    await self.check_lovers(killed_id)
            else:
                await self.broadcast("Səsvermədə bərabərlik oldu. Heç kim öldürülmədi.")
        await asyncio.sleep(2)
        await self.start_night()

    async def start_night(self):
        self.state = "night"
        self.kill_targets = []
        self.heal_target = None
        self.investigate_targets = []
        self.psychopath_target = None
        self.curse_target = None
        await self.broadcast("🌚 *Gecə başladı!*\nRollar öz fəaliyyətlərini yerinə yetirə bilər.")
        if self.night_task:
            self.night_task.cancel()
        self.night_task = asyncio.create_task(self.night_timer())

    async def night_timer(self):
        await asyncio.sleep(45)  # 45 saniyə gecə davam edir
        await self.end_night()

    async def end_night(self):
        # Mafiya və Serial Killer öldürmə əməliyyatları
        killed = None
        # Əgər mafiyanın məqsədi varsa, öldür
        if self.kill_targets:
            target = self.kill_targets[0]  # Yalnız bir hədəf qəbul olunur
            if target != self.heal_target and target not in self.killed:
                self.killed.add(target)
                name = self.players[target].full_name
                killed = name
                await self.broadcast(f"☠️ {name} gecə öldürüldü.")

        # Serial Killer öldürmə - əgər varsa
        # Bu nümunədə serial killer hədəfi ikinci sıradadır (daha sonra düzəldilə bilər)
        # Sağaltma yoxlanılır, serial killer öldürmə imkanı
        # (sadəcə nümunə kimi buraxıldı)

        # Polisin yoxlaması (oyuncunun rolu mafia olub-olmaması)
        for target in self.investigate_targets:
            if target in self.roles:
                rol = self.roles[target]
                msg = f"🔍 {self.players[target].full_name} rolü: {'Mafiya' if 'Mafiya' in rol else 'Sivil'}"
                try:
                    # Polisin id-si tapılmalıdır (bir nəfər polis var)
                    polis_id = [uid for uid, r in self.roles.items() if r == "Polis"]
                    if polis_id:
                        await self.bot.send_message(polis_id[0], msg)
                except:
                    pass

        # Aşiqlər - əgər biri ölsə digəri də ölər
        for lover in self.lovers:
            if lover in self.killed:
                other = self.lovers[1] if lover == self.lovers[0] else self.lovers[0]
                if other not in self.killed:
                    self.killed.add(other)
                    await self.broadcast(f"❤️ Aşiqlərdən biri öldü, digəri də öldü.")

        await self.broadcast("🌞 Gündüz başladı!")
        await self.start_day()

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
        emoji = rolu_gore_emoji(role)
        desc = ROLE_TESVIR.get(role, "")
        await msg.answer(f"🎭 Rolunuz: *{role}* {emoji}\n\n{desc}", parse_mode="Markdown")

    async def show_players(self, msg: types.Message):
        text = "👥 Oyunçular:\n"
        for uid, user in self.players.items():
            status = "☠️" if uid in self.killed else "✅"
            text += f"{status} {user.full_name}\n"
        await msg.answer(text)

    async def cancel_game(self, msg: types.Message):
        self.players.clear()
        self.killed.clear()
        self.roles.clear()
        self.state = "waiting"
        if self.day_task:
            self.day_task.cancel()
        if self.night_task:
            self.night_task.cancel()
        await msg.answer("❌ Oyun ləğv edildi.")

    async def check_lovers(self, killed_id):
        if killed_id in self.lovers:
            other = self.lovers[1] if self.lovers[0] == killed_id else self.lovers[0]
            if other not in self.killed:
                self.killed.add(other)
                name = self.players[other].full_name
                await self.broadcast(f"❤️ Aşiqlərdən biri öldü, digəri də öldü.")

    async def broadcast(self, text):
        for uid in self.players:
            try:
                await self.bot.send_message(uid, text, parse_mode="Markdown")
            except:
                pass
