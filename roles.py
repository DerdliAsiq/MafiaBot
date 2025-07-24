import random

available_roles = [
    "Mafiya",
    "Mafiya Bossu",
    "Polis",
    "Doktor",
    "Sakin",
    "Aşiqlər",
    "Serial Killer",
    "Psixopat",
    "Caduçu"
]

role_descriptions = {
    "Mafiya": "Gecə birini öldürmək üçün digər mafiya üzvləri ilə qərar ver.",
    "Mafiya Bossu": "Əsas mafiyadır. Əsas qərarları verir.",
    "Polis": "Gecə bir oyunçunun mafiya olub olmadığını yoxlaya bilərsən.",
    "Doktor": "Gecə bir oyunçunu ölümdən qoruya bilərsən.",
    "Sakin": "Heç bir xüsusi qabiliyyətin yoxdur.",
    "Aşiqlər": "İki nəfər bir-birinə aşiq olur. Biri ölsə, digəri də ölür.",
    "Serial Killer": "Hər gecə birini öldürə bilərsən. Tək işləyirsən.",
    "Psixopat": "Gecə birini qorxuda bilərsən. Səsverməni poza bilər.",
    "Caduçu": "Gizli sehrlərlə oyunu dəyişdirə bilər."
}

def assign_roles(players):
    roles = {}
    shuffled = players[:]
    random.shuffle(shuffled)

    base_roles = ["Mafiya", "Polis", "Doktor", "Sakin"]
    extended = base_roles + [r for r in available_roles if r not in base_roles]

    for i, player in enumerate(shuffled):
        role = extended[i % len(extended)]
        roles[player.id] = role

    return roles
