import random

ROLLAR = [
    "Mafiya",
    "Mafiya Bossu",
    "Polis",
    "Doktor",
    "Sakin",
    "Aşiqlər",
    # "Serial Killer",
    # "Psixopat",
    # "Caduçu"
]

ROLE_EMOJILAR = {
    "Mafiya": "🕴️",
    "Mafiya Bossu": "💼",
    "Polis": "👮",
    "Doktor": "🩺",
    "Sakin": "👤",
    "Aşiqlər": "❤️",
    "Serial Killer": "🔪",
    "Psixopat": "😈",
    "Caduçu": "🔮"
}

ROLE_TESVIR = {
    "Mafiya": "Gecə birini öldürmək üçün digər mafiya üzvləri ilə qərar ver.",
    "Mafiya Bossu": "Əsas mafiyadır. Mafiyanın gecə öldürmə qərarını verir.",
    "Polis": "Gecə bir oyunçunun mafiya olub olmadığını yoxlaya bilər.",
    "Doktor": "Gecə bir oyunçunu ölümdən qoruya bilər.",
    "Sakin": "Heç bir xüsusi qabiliyyətin yoxdur.",
    "Aşiqlər": "İki nəfər bir-birinə aşiq olur. Biri ölsə, digəri də ölür.",
    "Serial Killer": "Hər gecə birini öldürə bilər. Tək işləyir.",
    "Psixopat": "Gecə birini qorxuda bilər. Səsverməni poza bilər.",
    "Caduçu": "Gizli sehrlərlə oyunu dəyişdirə bilər."
}

def rolu_gore_emoji(rol):
    return ROLE_EMOJILAR.get(rol, "❓")

def assign_roles(players):
    roles = []
    n = len(players)
    # Minimum rollar: Mafiya (1), Polis(1), Doktor(1), Sakin(qalan)
    maf_count = max(1, n // 5)
    roles.extend(["Mafiya"] * (maf_count-1))
    roles.append("Mafiya Bossu")
    roles.append("Polis")
    roles.append("Doktor")
    rest = n - len(roles)
    roles.extend(["Sakin"] * rest)

    random.shuffle(roles)

    assigned = {}
    for player, role in zip(players, roles):
        assigned[player.id] = role

    # Aşiqlər tənzimlənməsi (iki oyunçu seçilir)
    if n >= 6:
        players_ids = list(assigned.keys())
        lovers = random.sample(players_ids, 2)
        assigned["aşiqlər"] = lovers

    return assigned
    
