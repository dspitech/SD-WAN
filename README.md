# Meridian Lab : TP SD-WAN réel, multisite et multi-transport

**E5 CCSN / SD-WAN - Édition étudiant - Atelier pratique, octobre 2026**

> Comprendre. Construire. Capturer. Diagnostiquer.

| Information | Détail |
|---|---|
| Durée | 4 heures exactement (240 minutes) |
| Niveau | Bac+5 |
| Environnement | Ubuntu Server 22.04 ou 24.04 LTS (accès SSH ou console, sans interface graphique) |
| Format | Binôme, autonome |
| Méthode | 100 % ligne de commande : `docker compose`, `tcpdump`, `tshark`, tout s'exécute dans des conteneurs Linux |
| Livrable | Fichiers PCAP, preuves en sortie de commande, diagnostics, HLD/LLD |
| Correction | Non incluse |

Travail encadré sur machines locales, sans cloud payant ni licence constructeur. Aucun port n'est publié sur l'hôte et aucun réseau du laboratoire n'a d'accès à l'Internet réel.

---

## Sommaire

1. [Présentation](#1-présentation)
2. [Contenu du kit et corrections de la version 1.1](#2-contenu-du-kit-et-corrections-de-la-version-11)
3. [Prérequis et installation (Ubuntu Server)](#3-prérequis-et-installation-ubuntu-server)
4. [Conventions de travail en ligne de commande](#4-conventions-de-travail-en-ligne-de-commande)
5. [Étape 1 : démarrer le laboratoire (00:00 - 00:35)](#5-étape-1--démarrer-le-laboratoire-0000---0035)
6. [Étape 2 : topologie, adressage et capture de l'underlay (00:35 - 01:15)](#6-étape-2--topologie-adressage-et-capture-de-lunderlay-0035---0115)
7. [Étape 3 : l'overlay chiffré (01:15 - 01:55)](#7-étape-3--loverlay-chiffré-0115---0155)
8. [Pause (01:55 - 02:05)](#8-pause-0155---0205)
9. [Étape 4 : SLA, QoS et basculement (02:05 - 02:45)](#9-étape-4--sla-qos-et-basculement-0205---0245)
10. [Étape 5 : plan de contrôle, ZTP et haute disponibilité (02:45 - 03:15)](#10-étape-5--plan-de-contrôle-ztp-et-haute-disponibilité-0245---0315)
11. [Étape 6 : segmentation, breakout local et sécurité (03:15 - 03:40)](#11-étape-6--segmentation-breakout-local-et-sécurité-0315---0340)
12. [Étape 7 : conception HLD/LLD et restitution (03:40 - 04:00)](#12-étape-7--conception-hldlld-et-restitution-0340---0400)
13. [Dossier de preuves, barème et remise](#13-dossier-de-preuves-barème-et-remise)
14. [Aide rapide : diagnostic et reprise](#14-aide-rapide--diagnostic-et-reprise)
15. [Sources de référence](#15-sources-de-référence)

---

## 1. Présentation

### 1.1 Le mandat

Vous intervenez pour **Meridian Technologies**, groupe européen présent à Paris et Berlin. Les utilisateurs se plaignent de lenteurs applicatives et d'interruptions. Votre mission consiste à :

- monter un laboratoire à deux transports ;
- capturer le trafic réel ;
- analyser une encapsulation chiffrée ;
- provoquer des pannes ;
- proposer des politiques SD-WAN argumentées.

Le cours de référence comporte sept modules : WAN traditionnel et cloud, principes SD-WAN, composants (underlay, overlay et plans), traffic engineering, sécurité, fournisseurs, conception d'entreprise. Ce TP vise une mise en pratique intégrée, pas la reproduction d'une plateforme constructeur complète en quatre heures.

Un seul objectif : savoir expliquer, preuves à l'appui, ce qui circule sur les liens, comment les politiques décident des chemins et ce qui continue à fonctionner en cas de panne.

### 1.2 Compétences mesurées

- Identifier chemins underlay, overlay et flux utilisateurs par adresses IP, interfaces et ports.
- Mettre en relation mesures SLA, flux applicatifs, politiques et basculement.
- Distinguer trafic de données et de gestion, analyser l'autonomie en panne de contrôle.
- Capturer et filtrer des paquets, produire des preuves reproductibles.
- Discuter chiffrement, segmentation, breakout local, haute disponibilité et limites opérationnelles.

### 1.3 Ce qui est réel, ce qui est simulé

| Composant | Réellement observé | Limite pédagogique |
|---|---|---|
| Underlay | Réseaux IP Docker distincts, trames IP/UDP, pertes mesurées | Le réseau « MPLS » n'utilise pas de labels MPLS |
| Overlay | Messages applicatifs encapsulés dans UDP, chiffrés en AES-256-GCM | Ce n'est pas un tunnel L3 IPsec/IKEv2 ni du WireGuard |
| Choix de chemin | Sondes RTT/perte, règles, préférence, secours, télémétrie | Moteur simplifié, pas de reconnaissance DPI ni de BFD constructeur |
| Contrôle / gestion | Manager HTTP central, politique JSON actualisable, cache local | API de laboratoire, pas de protocole OMP constructeur |
| Sécurité | Chiffrement authentifié, refus HTTP de flux invités | Pas de VRF, NGFW, segmentation matérielle ou SASE réel |
| Capture | `tcpdump` produit de vrais fichiers PCAP, `tshark` les décode | Trame interne applicative protégée, pas d'ESP IPsec |

### 1.4 Cadre et sécurité

- L'environnement est volontairement isolé : aucun port publié sur l'hôte, réseaux Docker en mode `internal`.
- La clé AES de démonstration se trouve dans les fichiers du TP (`compose.yaml`) et n'est pas secrète.
- Aucune fonction de ce kit n'est destinée à la production.
- N'utilisez pas de vrais identifiants, données clients ou interfaces réseau d'établissement dans ce laboratoire.

### 1.5 Règle pédagogique

Un résultat inattendu n'est pas un échec s'il est correctement capturé, expliqué et accompagné d'une hypothèse de diagnostic. La rigueur vaut davantage qu'un chiffre parfait.

### 1.6 Déroulé des 240 minutes

| Temps | Durée | Séquence | Section |
|---|---|---|---|
| 00:00 - 00:35 | 35 min | Installer, démarrer Docker, vérifier les sept conteneurs | [Étape 1](#5-étape-1--démarrer-le-laboratoire-0000---0035) |
| 00:35 - 01:15 | 40 min | Découvrir le WAN, les transports, l'adressage, premières captures | [Étape 2](#6-étape-2--topologie-adressage-et-capture-de-lunderlay-0035---0115) |
| 01:15 - 01:55 | 40 min | Explorer l'overlay chiffré : TCP interne, UDP externe, analyse `tshark` | [Étape 3](#7-étape-3--loverlay-chiffré-0115---0155) |
| 01:55 - 02:05 | 10 min | Pause | |
| 02:05 - 02:45 | 40 min | Injecter perte et latence, vérifier politiques, SLA et failover | [Étape 4](#9-étape-4--sla-qos-et-basculement-0205---0245) |
| 02:45 - 03:15 | 30 min | Panne des contrôleurs, mise à jour des politiques, ZTP et architecture | [Étape 5](#10-étape-5--plan-de-contrôle-ztp-et-haute-disponibilité-0245---0315) |
| 03:15 - 03:40 | 25 min | Segmentation, accès SaaS local, sécurité et limites | [Étape 6](#11-étape-6--segmentation-breakout-local-et-sécurité-0315---0340) |
| 03:40 - 04:00 | 20 min | HLD/LLD, restitution, remise des artefacts | [Étape 7](#12-étape-7--conception-hldlld-et-restitution-0340---0400) |

### 1.7 Vue d'ensemble du parcours

| Étape | Thème | Missions | Preuves |
|---|---|---|---|
| 1 | Préparation et démarrage | Installation, sept nœuds | A |
| 2 | Transport et underlay | Missions 1 et 2 | B, capture 01 |
| 3 | Encapsulation | Mission 3 | C, capture 02 |
| 4 | SLA | Missions 4, 5, 6, mode avancé `netem`, dimensionnement | D |
| 5 | Contrôle | Missions 7 et 8, ZTP et HA | E |
| 6 | Sécurité | Missions 9 et 10, mini-audit | F |
| 7 | Conception | Mission 11, rendu | HLD, LLD, diagnostic final |

---

## 2. Contenu du kit et corrections de la version 1.1

### 2.1 Arborescence du dossier `lab`

```text
lab/
  compose.yaml            machines, réseaux IP, interfaces virtuelles
  Dockerfile              image commune (Python, tcpdump, tshark, outils réseau)
  edge.py                 encapsulation UDP, AES-GCM, sondes, sélection du chemin
  controller.py           distribution centrale des politiques JSON
  app.py                  serveurs ERP et SaaS répondant en HTTP
  policy/
    policy.json           politique active (préférences et limites SLA)
    policy.original.json  copie de référence pour la remise à zéro
  scripts/                outils embarqués dans l'image (voir 2.2)
  captures/               fichiers PCAP et preuves (partagé avec l'hôte)
    preuves/              sorties de commandes horodatées (preuves A à F)
  README.md               ce document
```

### 2.2 Outils embarqués dans les conteneurs

Ces commandes sont installées dans tous les conteneurs. Elles s'exécutent avec `docker compose exec <service> <outil>`.

| Outil | Rôle | Exemple |
|---|---|---|
| `ifmap` | Associe chaque interface au réseau logique (internet, mpls, control...) | `docker compose exec paris-edge ifmap` |
| `ifmap <réseau>` | Affiche uniquement le nom de l'interface | `docker compose exec paris-edge ifmap mpls` |
| `labwait` | Attend que les deux transports soient mesurés « up » | `docker compose exec employee labwait` |
| `sla` | Résumé : état des transports et chemin choisi par application | `docker compose exec employee sla` |
| `watchpath` | Relevé chaque seconde du chemin et des mesures (temps de réaction) | `docker compose exec employee watchpath erp 30` |
| `proof` | Exécute une commande et enregistre la sortie horodatée dans `captures/preuves/` | `docker compose exec employee proof A_status curl -s http://10.10.0.1:8080/status` |
| `decrypt-overlay` | Déchiffre les trames `E5A1` d'un PCAP avec la clé de démonstration | `docker compose exec paris-edge decrypt-overlay /captures/02_overlay.pcap` |

### 2.3 Corrections apportées au kit initial

Cette version corrige le plan réseau, qui prêtait à confusion entre les liens parallèles (Internet, « MPLS », contrôle) et les LAN.

| N° | Problème constaté | Correction |
|---|---|---|
| 1 | Les Edges utilisaient l'adresse `.1` des LAN, que Docker réserve par défaut à sa passerelle : risque de conflit d'adresse au démarrage | Passerelle Docker déplacée en `.254` sur les six sous-réseaux, `.1` reste aux Edges |
| 2 | Les réseaux avaient une sortie vers l'hôte (NAT Docker), contredisant l'énoncé « environnement isolé » | Les six réseaux sont `internal: true` : pas de route par défaut, pas d'Internet réel |
| 3 | Le proxy HTTP de l'Edge Paris écoutait sur `0.0.0.0:8080` : accessible aussi depuis les underlays et le contrôle, y compris `/lab/impair` | Écoute limitée à `10.10.0.1` (employés) et `10.11.0.1` (invités). ERP, SaaS et manager n'écoutent plus que sur leur adresse |
| 4 | Les noms d'interfaces (`eth0`, `eth1`...) ne correspondent pas à un réseau fixe : confusion entre transports parallèles | Outil `ifmap` : table interface / adresse / réseau, utilisable dans les captures |
| 5 | Un invité pouvait lire `/status` et appeler `/lab/impair` (modifier les chemins de l'entreprise) | Routes d'administration refusées au segment invité (HTTP 403) |
| 6 | `policy.json` monté comme fichier unique : un éditeur qui remplace le fichier laissait le conteneur sur l'ancienne version | Montage du dossier `policy/`, lecture tolérant le BOM UTF-8 ajouté par certains éditeurs |
| 7 | `tcpdump -w` peut échouer sur `Permission denied` dans un conteneur (abandon des privilèges) ; pas d'analyse des PCAP sans Wireshark | Option `-Z root` dans toutes les commandes, `tshark` ajouté à l'image, dossier `captures` monté aussi sur `employee` et `guest` |
| 8 | Arrêt lent des conteneurs, démarrage sans signal de disponibilité, 7 constructions d'image | `init: true`, contrôles de santé (`healthcheck`), image unique partagée |
| 9 | Un transport pouvait apparaître « up » dans la première seconde après démarrage de la machine | Initialisation de la dernière réponse à une valeur très ancienne |

### 2.4 Comportements à connaître

- Le proxy de l'Edge est un **proxy applicatif**, pas un routeur : il ne transfère aucun paquet IP. Les conteneurs `employee` et `guest` n'ont donc **pas de route par défaut**, seulement la route de leur LAN. C'est voulu.
- La fenêtre de mesure est de 12 échantillons, une sonde par seconde et par transport : une mesure met environ 12 secondes à refléter un changement complet.
- Une panne franche (blackout) est détectée après environ 3,5 secondes sans réponse. Une requête émise pendant cette fenêtre peut recevoir `504 overlay-timeout` avant le basculement.

---

## 3. Prérequis et installation (Ubuntu Server)

### 3.1 Ressources nécessaires

- Ubuntu Server 22.04 LTS ou 24.04 LTS, architecture `amd64` ou `arm64`, avec un accès `sudo`.
- 4 Go de RAM libres et environ 3 Go d'espace disque.
- Un accès réseau sortant pendant l'installation et le premier `docker compose up --build` (téléchargement de paquets et de l'image Python). Une fois le laboratoire construit, il fonctionne hors ligne.
- Aucune interface graphique : toutes les captures et analyses se font avec `tcpdump` et `tshark`, présents dans les conteneurs. Wireshark n'est pas installé sur le serveur.

> **Préparation conseillée avant la séance.** Installer Docker Engine et copier l'archive du TP sur le serveur. Compter environ 10 minutes pour l'installation de Docker et le premier `--build`.

### 3.2 Vérifier l'hôte avant d'installer

```bash
lsb_release -ds
uname -m
free -h
df -h ~
ip -br -4 addr
```

Contrôler que **aucune interface ou route de l'hôte n'utilise les plages du laboratoire** : `10.10.0.0/24`, `10.11.0.0/24`, `10.20.0.0/24`, `172.28.10.0/24`, `172.28.20.0/24`, `172.28.30.0/24`. Un serveur Ubuntu sur un réseau d'entreprise en `10.x` peut entrer en conflit (erreur `Pool overlaps with other one on this address space` au démarrage).

### 3.3 Installer Docker Engine et le plugin Compose

Procédure du dépôt officiel Docker pour Ubuntu (ne pas ajouter de dépôt non maîtrisé) :

```bash
sudo apt update
sudo apt install -y ca-certificates curl unzip
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo ${UBUNTU_CODENAME:-$VERSION_CODENAME}) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable --now docker
```

Vérification :

```bash
sudo docker --version
sudo docker compose version
sudo docker info --format '{{.OSType}} / {{.Architecture}}'
```

Résultat attendu : `linux / x86_64` (ou `linux / aarch64` sur serveur ARM).

### 3.4 Utiliser Docker sans `sudo` (recommandé, à faire avant la séance)

Toutes les commandes de ce document sont écrites **sans `sudo`**. Deux possibilités :

```bash
# Option 1 : autoriser votre compte (à faire une seule fois, avant la séance)
sudo usermod -aG docker $USER
newgrp docker
docker info --format '{{.OSType}}'
```

Option 2 : conserver le groupe système inchangé et préfixer chaque commande par `sudo` (`sudo docker compose ...`). Dans ce cas, les fichiers de `captures/` appartiennent à `root` : voir la section 3.7.

> Le groupe `docker` donne un accès équivalent à `root` sur l'hôte. Sur une machine partagée, préférer l'option 2.

### 3.5 Récupérer et ouvrir le kit

Copier l'archive sur le serveur (depuis votre poste : `scp lab-corrige.zip utilisateur@serveur:~/`), puis :

```bash
cd ~
unzip lab-corrige.zip
cd lab
ls
```

Résultat attendu : `Dockerfile  README.md  app.py  captures  compose.yaml  controller.py  edge.py  policy  scripts`.

### 3.6 Module noyau `netem` (mode avancé uniquement)

Le mode avancé de l'étape 4 utilise `tc netem`, qui dépend du noyau **de l'hôte** (les conteneurs partagent le noyau d'Ubuntu). À vérifier :

```bash
sudo modprobe sch_netem && echo "netem disponible"
lsmod | grep sch_netem
```

Si le module est absent (noyau « cloud » minimal), il est fourni par le paquet suivant :

```bash
sudo apt install -y linux-modules-extra-$(uname -r)
sudo modprobe sch_netem
```

Si l'installation n'est pas possible, rester sur l'émulation applicative de la mission 5, suffisante pour la validation.

### 3.7 Lire les fichiers de `captures/` depuis l'hôte

Les PCAP sont écrits par `root` dans les conteneurs. Pour les lire, les copier ou les ouvrir avec votre compte :

```bash
sudo chown -R $USER:$USER captures
ls -l captures
```

À refaire après chaque nouvelle capture si vous utilisez l'option `sudo`. Pour récupérer les fichiers sur votre poste et les ouvrir avec Wireshark graphique (facultatif) :

```bash
scp -r utilisateur@serveur:~/lab/captures ./captures
```

### 3.8 Checklist de prévol (à valider avant la minute 35)

- [ ] `docker info` répond sans `sudo` (ou `sudo docker info` si option 2), `OSType=linux`
- [ ] `docker compose version` affiche une version
- [ ] 4 Go de RAM libres et environ 3 Go d'espace disque disponibles
- [ ] Aucune adresse de l'hôte ne chevauche les plages du laboratoire (section 3.2)
- [ ] Les fichiers `compose.yaml`, `Dockerfile`, `edge.py`, `controller.py`, `app.py` sont présents, ainsi que les dossiers `policy/`, `scripts/` et `captures/`
- [ ] Le terminal est dans le dossier `lab` : `docker compose config --quiet` ne renvoie aucune erreur
- [ ] Facultatif : `sch_netem` disponible (section 3.6)

---

## 4. Conventions de travail en ligne de commande

1. **Dossier de travail.** Toutes les commandes se lancent depuis le dossier `lab`, dans un terminal bash (SSH ou console).
2. **Forme générale.** `docker compose exec <service> <commande>` exécute une commande dans un des sept conteneurs : `controller`, `paris-edge`, `berlin-edge`, `employee`, `guest`, `erp`, `saas`.
3. **`sudo`.** Les commandes sont écrites sans `sudo` (voir 3.4). Avec l'option 2, préfixer chaque `docker` par `sudo`.
4. **Guillemets simples.** Les commandes utilisent des guillemets simples pour que les caractères `&`, `[`, `$(...)` et les espaces soient transmis tels quels au conteneur. Ne pas les remplacer par des guillemets doubles : l'interpréteur de l'hôte évaluerait alors `$(ifmap ...)` sur le serveur au lieu du conteneur.
5. **Attendre.** `sleep N` suspend le terminal de N secondes.
6. **Captures en arrière-plan.** `docker compose exec -d` lance une commande détachée : la capture tourne pendant que vous générez le trafic dans le même terminal. Un seul terminal suffit.
7. **Durée des captures.** `timeout N tcpdump ...` arrête proprement la capture au bout de N secondes. Un code de sortie 124 est normal.
8. **Avertissement `tshark`.** Le message `Running as user "root"... This could be dangerous` est normal dans le conteneur : il est sans effet sur le TP.
9. **Preuves.** Utiliser `proof NOM commande` pour conserver la sortie dans `captures/preuves/NOM.txt`. Pour une commande de l'hôte (`docker compose ps`), utiliser `| tee captures/preuves/NOM.txt`.
10. **Options `tcpdump` utilisées partout.** `-nn` (pas de résolution de noms), `-s 0` (paquet entier), `-U` (écriture immédiate, PCAP exploitable même interrompu), `-Z root` (évite `Permission denied` dans les conteneurs).
11. **Chemins.** Les commandes `tshark` et `tcpdump` lisent et écrivent dans `/captures/...` **côté conteneur**, qui correspond à `captures/...` côté hôte.

### Correspondance filtres Wireshark et `tshark`

Les filtres d'affichage Wireshark s'utilisent tels quels avec `tshark -Y` :

| Filtre | Usage |
|---|---|
| `icmp` | Echo Request / Echo Reply (underlay) |
| `tcp.port == 8080` | Requête HTTP employé vers l'Edge Paris LAN |
| `udp.port == 45900` | Sondes et flux applicatifs du tunnel pédagogique chiffré |
| `ip.src == 172.28.10.10` | Paquets provenant de l'Edge sur le transport Internet |
| `ip.addr == 172.28.20.20` | Paquets du transport dit « MPLS simulé » |
| `tcp.port == 9000` | Gestion entre Edge et Manager, si la capture englobe le lien de contrôle |
| `udp.payload[0:4] == 45:35:41:31` | Trames portant le marqueur `E5A1` du laboratoire |

Modèle de commande :

```bash
docker compose exec paris-edge tshark -r /captures/FICHIER.pcap -Y 'FILTRE' -T fields -e frame.number -e ip.src -e ip.dst
```

---

## 5. Étape 1 : démarrer le laboratoire (00:00 - 00:35)

### 5.1 Construire et lancer les sept nœuds

Depuis le dossier `lab` :

```bash
docker compose up -d --build --wait
docker compose ps
```

- `--build` construit l'image commune (premier démarrage : téléchargement de l'image Python, installation des utilitaires Linux, de `tshark` et du module de chiffrement Python, quelques minutes).
- `--wait` rend la main quand les services sont démarrés et sains. Si votre version de Compose ne le connaît pas, retirer l'option et utiliser `labwait` ci-dessous.

Résultat attendu : sept services `Up`, les services avec contrôle de santé (`controller`, `paris-edge`, `erp`, `saas`) en `healthy`.

### 5.2 Attendre la stabilisation des sondes

```bash
docker compose exec employee labwait
```

Résultat attendu : `pret : internet et mpls mesures up apres Ns`. Cela évite l'erreur `503 no-underlay-available` des premières secondes.

### 5.3 Premières requêtes

```bash
docker compose exec employee curl -s http://10.10.0.1:8080/status
docker compose exec employee curl -s http://10.10.0.1:8080/erp
docker compose exec employee curl -s http://10.10.0.1:8080/teams
```

Exemple de sortie de `/status` (valeurs variables) :

```json
{
  "role": "paris",
  "generation": "2026-10-meridian-v1",
  "controller_reachable": true,
  "http_listen": ["10.10.0.1:8080", "10.11.0.1:8080"],
  "paths": {
    "internet": {"up": true, "rtt_ms": 0.9, "loss_pct": 0.0, "observations": 12},
    "mpls": {"up": true, "rtt_ms": 0.8, "loss_pct": 0.0, "observations": 12}
  },
  "impairment_training_only": {
    "internet": {"loss": 0.0, "delay_ms": 0},
    "mpls": {"loss": 0.0, "delay_ms": 0}
  }
}
```

Exemple de sortie de `/erp` :

```json
{
  "selected_path": "mpls",
  "policy_reason": "preferred-and-within-sla",
  "request_id": "f329792b145c490d8b1d98c5e6281775",
  "remote": "{\"application\": \"erp\", \"path\": \"/erp?request=f329...\", ...}"
}
```

Vue synthétique avec l'outil `sla` :

```bash
docker compose exec employee sla
```

### 5.4 Preuve A

```bash
docker compose ps | tee captures/preuves/A_compose_ps.txt
docker compose exec employee proof A_status curl -s http://10.10.0.1:8080/status
docker compose exec employee proof A_erp curl -s http://10.10.0.1:8080/erp
```

**Preuve A.** Les trois fichiers `A_compose_ps.txt`, `A_status.txt` et `A_erp.txt`, plus une phrase décrivant la différence entre `selected_path` et `policy_reason`.

### 5.5 Lecture minimale de la structure fournie

| Fichier | Rôle |
|---|---|
| `compose.yaml` | Machines, réseaux IP et interfaces virtuelles |
| `edge.py` | Encapsulation UDP, chiffrement AES-GCM, sondes, sélection du chemin |
| `controller.py` | Distribution centrale des politiques JSON |
| `policy/policy.json` | Préférences et limites SLA des applications |
| `app.py` | Serveurs ERP et SaaS répondant en HTTP |

Lecture conseillée en ligne de commande :

```bash
docker compose config
docker compose exec controller cat /lab/policy/policy.json
```

### 5.6 Dépannage du démarrage

| Symptôme | Action |
|---|---|
| `Cannot connect to the Docker daemon` | `sudo systemctl start docker`, puis `systemctl status docker` |
| `permission denied ... docker.sock` | Compte absent du groupe `docker` : `sudo usermod -aG docker $USER` puis `newgrp docker`, ou préfixer par `sudo` |
| `port already allocated` | Aucun port hôte n'est exposé : vérifier un autre projet Docker conflictuel |
| `Pool overlaps with other one on this address space` | Un autre réseau Docker utilise 10.10.x, 10.11.x, 10.20.x ou 172.28.x : `docker network ls`, arrêter l'autre projet |
| `no space left on device` | Libérer de l'espace disque, ne pas exécuter de commande Docker globale destructrice |
| Un conteneur quitte | `docker compose logs <service>`, vérifier l'image et la syntaxe des fichiers |
| `503 no-underlay-available` juste après le démarrage | Lancer `docker compose exec employee labwait` ou attendre 5 secondes |

---

## 6. Étape 2 : topologie, adressage et capture de l'underlay (00:35 - 01:15)

### 6.1 Lire un vrai réseau multisite

```text
 LAN Paris 10.10.0.0/24                                       LAN Berlin 10.20.0.0/24
 employee 10.10.0.10 ---+                                       +--- erp 10.20.0.20
                        |                                       |
                  [ EDGE PARIS ]                         [ EDGE BERLIN ]
                   LAN   10.10.0.1                        LAN   10.20.0.1
                   invité 10.11.0.1
                        |
 guest 10.11.0.10 ------+
 LAN invité 10.11.0.0/24

 Entre les deux Edges, trois réseaux IP en parallèle :

 EDGE PARIS  172.28.10.10 --- INTERNET 172.28.10.0/24 ------------ 172.28.10.20  EDGE BERLIN
                                       |
                                 saas 172.28.10.40

 EDGE PARIS  172.28.20.10 --- MPLS SIMULE 172.28.20.0/24 -------- 172.28.20.20  EDGE BERLIN

 EDGE PARIS  172.28.30.11 --- CONTROLE 172.28.30.0/24 ----------- 172.28.30.12  EDGE BERLIN
                                       |
                              controller 172.28.30.10
```

Lecture : les deux transports (Internet et « MPLS ») sont **deux réseaux IP distincts en parallèle** entre les mêmes deux Edges. Chaque Edge a donc une adresse différente sur chacun. Le SaaS est raccordé au seul réseau Internet.

### 6.2 Plan d'adressage complet

| Nœud | LAN Paris | LAN invité | LAN Berlin | Internet | « MPLS » | Contrôle |
|---|---|---|---|---|---|---|
| `employee` | 10.10.0.10 | | | | | |
| `guest` | | 10.11.0.10 | | | | |
| `paris-edge` | 10.10.0.1 | 10.11.0.1 | | 172.28.10.10 | 172.28.20.10 | 172.28.30.11 |
| `berlin-edge` | | | 10.20.0.1 | 172.28.10.20 | 172.28.20.20 | 172.28.30.12 |
| `erp` | | | 10.20.0.20 | | | |
| `saas` | | | | 172.28.10.40 | | |
| `controller` | | | | | | 172.28.30.10 |

| Réseau | CIDR | Passerelle Docker réservée (hôte, non utilisée) | Fonction exacte |
|---|---|---|---|
| Paris LAN | 10.10.0.0/24 | 10.10.0.254 | Client métier vers Edge Paris |
| Guest LAN | 10.11.0.0/24 | 10.11.0.254 | Réseau invité séparé, politique applicative |
| Berlin LAN | 10.20.0.0/24 | 10.20.0.254 | Edge Berlin vers serveur ERP |
| Internet | 172.28.10.0/24 | 172.28.10.254 | Transport IP simulé pour overlay et sortie SaaS |
| « MPLS » | 172.28.20.0/24 | 172.28.20.254 | Deuxième transport IP simulé, aucune étiquette MPLS |
| Control | 172.28.30.0/24 | 172.28.30.254 | Synchronisation centrale des politiques |

Ports applicatifs :

| Port | Protocole | Où | Rôle |
|---|---|---|---|
| 8080 | TCP | Edge Paris, adresses LAN uniquement | Proxy applicatif HTTP pour employés et invités |
| 45900 | UDP | Edges, sur chaque underlay | Overlay chiffré : sondes et flux applicatifs |
| 9000 | TCP | Manager, réseau de contrôle | Distribution de la politique |
| 8000 | TCP | `erp` et `saas` | Services applicatifs |

### 6.3 Mission 1 : cartographier les interfaces (10 min)

```bash
docker compose exec paris-edge ifmap
docker compose exec berlin-edge ifmap
docker compose exec paris-edge ip -br -4 addr
docker compose exec berlin-edge ip -br -4 addr
docker compose exec employee ip route
docker compose exec paris-edge ip route
```

`ifmap` affiche la table `INTERFACE / ADRESSE / RESEAU`. Les noms (`eth0`, `eth1`...) **varient d'une machine à l'autre : ne jamais supposer qu'`eth0` est Internet.** Utiliser `ifmap` pour retrouver le nom réel.

Conservation des preuves :

```bash
docker compose exec paris-edge proof M1_paris_ifmap ifmap
docker compose exec berlin-edge proof M1_berlin_ifmap ifmap
docker compose exec paris-edge proof M1_paris_route ip route
docker compose exec employee proof M1_employee_route ip route
```

**Travail demandé :**

- Noter les adresses exactes de Paris sur chaque underlay, les IP distantes correspondantes et les adresses des endpoints applicatifs.
- Faire un schéma avec les interfaces effectives (leurs noms peuvent varier).
- Compléter ce tableau pour l'Edge Paris :

| Interface (nom réel) | Réseau | Adresse | Plan fonctionnel (données, contrôle, gestion) |
|---|---|---|---|
| | | | |

### 6.4 Mission 2 : observer ICMP, HTTP et UDP (20 min)

#### 6.4.1 Tester séparément chaque transport

L'option `-I` force l'adresse source choisie, donc le transport utilisé.

```bash
docker compose exec paris-edge ping -c 4 -I 172.28.10.10 172.28.10.20
docker compose exec paris-edge ping -c 4 -I 172.28.20.10 172.28.20.20
docker compose exec employee curl -v http://10.10.0.1:8080/erp
```

Noter, pour chaque lien, le RTT moyen et la perte de paquets. Attention : les RTT du laboratoire local ne modélisent pas les distances Paris-Berlin.

#### 6.4.2 Capture durable sur l'Edge Paris (fichier `01_all_traffic.pcap`)

Démarrer une capture de 40 secondes sur toutes les interfaces du conteneur, en arrière-plan, puis générer le trafic :

```bash
docker compose exec -d paris-edge sh -c 'timeout 40 tcpdump -i any -nn -s 0 -U -Z root -w /captures/01_all_traffic.pcap'
sleep 2
docker compose exec employee curl -s http://10.10.0.1:8080/erp
docker compose exec employee curl -s http://10.10.0.1:8080/teams
docker compose exec paris-edge ping -c 3 172.28.20.20
sleep 40
docker compose exec paris-edge ls -l /captures
```

Le fichier `captures/01_all_traffic.pcap` doit apparaître dans le dossier `captures` du serveur (voir 3.7 pour en devenir propriétaire). Comme `-i any` capte toutes les interfaces, chaque paquet porte un en-tête Linux « cooked » (SLL) à la place de l'en-tête Ethernet. Pour voir les adresses MAC d'un transport précis, capturer une seule interface :

```bash
docker compose exec -d paris-edge sh -c 'timeout 15 tcpdump -i $(ifmap mpls) -nn -s 0 -U -Z root -w /captures/01b_mpls_only.pcap'
```

#### 6.4.3 Analyser la capture avec `tshark`

Hiérarchie des protocoles et conversations :

```bash
docker compose exec paris-edge tshark -r /captures/01_all_traffic.pcap -q -z io,phs
docker compose exec paris-edge tshark -r /captures/01_all_traffic.pcap -q -z conv,ip
docker compose exec paris-edge tshark -r /captures/01_all_traffic.pcap -q -z conv,udp
```

Paquets ICMP (underlay) :

```bash
docker compose exec paris-edge tshark -r /captures/01_all_traffic.pcap -Y icmp -T fields -e frame.number -e frame.time_relative -e ip.src -e ip.dst -e icmp.type
```

Requêtes HTTP sur le LAN et sur le contrôle :

```bash
docker compose exec paris-edge tshark -r /captures/01_all_traffic.pcap -Y 'http.request' -T fields -e frame.number -e ip.src -e ip.dst -e tcp.dstport -e http.request.uri
```

Sondes et flux du tunnel chiffré :

```bash
docker compose exec paris-edge sh -c 'tshark -r /captures/01_all_traffic.pcap -Y udp.port==45900 -T fields -e frame.number -e ip.src -e ip.dst -e udp.srcport -e udp.dstport -e udp.length 2>/dev/null | head -n 12'
```

Trafic d'un transport précis :

```bash
docker compose exec paris-edge tshark -r /captures/01_all_traffic.pcap -Y 'ip.addr==172.28.20.20'
docker compose exec paris-edge tshark -r /captures/01_all_traffic.pcap -Y 'ip.src==172.28.10.10'
```

Plan de contrôle (interrogation périodique de la politique) :

```bash
docker compose exec paris-edge tshark -r /captures/01_all_traffic.pcap -Y 'tcp.port==9000 && http' -T fields -e frame.time_relative -e ip.src -e ip.dst -e http.request.uri -e http.response.code
```

#### 6.4.4 Preuve B

```bash
docker compose exec paris-edge proof B_icmp tshark -r /captures/01_all_traffic.pcap -Y icmp -T fields -e frame.number -e ip.src -e ip.dst -e ip.proto -e icmp.type
docker compose exec paris-edge proof B_udp45900 sh -c 'tshark -r /captures/01_all_traffic.pcap -Y udp.port==45900 -T fields -e frame.number -e ip.src -e ip.dst -e ip.proto -e udp.srcport -e udp.dstport 2>/dev/null | head -n 10'
```

**Preuve B.** Les fichiers `B_icmp.txt` et `B_udp45900.txt`, avec ce tableau complété pour un paquet ICMP et un paquet UDP/45900 :

| Paquet | IP source | IP destination | Protocole | Port | Réseau sous-jacent |
|---|---|---|---|---|---|
| ICMP | | | | sans objet | |
| UDP | | | | | |

Expliquer pourquoi le transport « MPLS simulé » n'est pas du MPLS natif.

#### 6.4.5 Questions de recherche

1. Combien d'interfaces IP l'Edge Paris possède-t-il ? À quel plan fonctionnel associeriez-vous chaque trafic ?
2. Quelle différence observez-vous entre une capture côté `employee` et côté `paris-edge` ?
3. Un simple `ping` réussi garantit-il l'accessibilité de l'ERP ? Proposer deux contre-exemples.

Pistes d'expérimentation (sans correction) :

- Question 1 : `ifmap` sur `paris-edge`, puis les captures de la section 6.4.3 pour rattacher chaque flux à une interface.
- Question 2 : capturer simultanément les deux nœuds, puis comparer les conversations.

```bash
docker compose exec -d employee sh -c 'timeout 15 tcpdump -i any -nn -s 0 -U -Z root -w /captures/03_employee.pcap'
docker compose exec -d paris-edge sh -c 'timeout 15 tcpdump -i any -nn -s 0 -U -Z root -w /captures/03_paris_edge.pcap'
sleep 2
docker compose exec employee curl -s http://10.10.0.1:8080/erp
sleep 15
docker compose exec employee tshark -r /captures/03_employee.pcap -q -z conv,ip
docker compose exec paris-edge tshark -r /captures/03_paris_edge.pcap -q -z conv,ip
```

- Question 3 : comparer un `ping` underlay avec la réponse de `/erp` après avoir arrêté l'ERP, puis après avoir injecté de la perte sur un transport (Étape 4). Restaurer ensuite :

```bash
docker compose stop erp
docker compose exec paris-edge ping -c 2 -I 172.28.10.10 172.28.10.20
docker compose exec employee curl -s http://10.10.0.1:8080/erp
docker compose start erp
```

---

## 7. Étape 3 : l'overlay chiffré (01:15 - 01:55)

### 7.1 Mission 3 : du HTTP interne au datagramme chiffré (25 min)

Le client `employee` appelle un endpoint HTTP de l'Edge Paris. L'Edge termine cette session HTTP, choisit le transport et crée un nouveau message applicatif encapsulé dans UDP, protégé en AES-GCM. L'Edge Berlin déchiffre puis contacte l'ERP par une autre connexion HTTP.

Ce n'est pas le transport transparent d'un paquet IP d'origine dans IPsec : vous devez identifier précisément la différence.

```text
employee            EDGE PARIS                     EDGE BERLIN              erp
10.10.0.10          10.10.0.1                      10.20.0.1                10.20.0.20
   |  HTTP/TCP 8080     |                               |                      |
   |------------------->|  session HTTP terminée        |                      |
   |                    |  choix du transport (SLA)     |                      |
   |                    |==== UDP 45900 chiffré ======>|  déchiffrement       |
   |                    |   (message "req")            |  HTTP/TCP 8000       |
   |                    |                               |--------------------->|
   |                    |                               |<---------------------|
   |                    |<=== UDP 45900 chiffré =======|  (message "resp")    |
   |<-------------------|  réponse JSON                 |                      |
```

```bash
docker compose exec employee curl -s http://10.10.0.1:8080/erp
docker compose exec employee curl -s http://10.10.0.1:8080/teams
docker compose exec employee curl -s http://10.10.0.1:8080/status
```

**Observation guidée.** Pour `/erp`, la politique préfère le chemin `mpls`. Pour `/teams`, elle préfère `internet`. Ces préférences ne s'appliquent que si les seuils configurés sont satisfaits. Le service répond en JSON et indique le chemin sélectionné.

### 7.2 Capturer l'overlay, sans confondre avec IPsec (fichier `02_overlay.pcap`)

```bash
docker compose exec -d paris-edge sh -c 'timeout 35 tcpdump -i any -nn -s 0 -U -Z root -w /captures/02_overlay.pcap udp port 45900'
sleep 2
docker compose exec employee sh -c 'for i in $(seq 1 10); do curl -s http://10.10.0.1:8080/erp > /dev/null; done'
sleep 35
docker compose exec paris-edge ls -l /captures
```

### 7.3 Analyser le datagramme chiffré en ligne de commande

Liste des datagrammes (en-tête IP externe et en-tête UDP) :

```bash
docker compose exec paris-edge sh -c 'tshark -r /captures/02_overlay.pcap -T fields -e frame.number -e frame.time_relative -e ip.src -e ip.dst -e udp.srcport -e udp.dstport -e udp.length 2>/dev/null | head -n 15'
```

Comptage des trames portant le marqueur `E5A1` (hexadécimal `45 35 41 31`) :

```bash
docker compose exec paris-edge sh -c 'tshark -r /captures/02_overlay.pcap -Y udp.port==45900 2>/dev/null | wc -l'
docker compose exec paris-edge sh -c 'tshark -r /captures/02_overlay.pcap -Y udp.payload[0:4]==45:35:41:31 2>/dev/null | wc -l'
```

Octets du payload d'un paquet (hexadécimal et ASCII) :

```bash
docker compose exec paris-edge tshark -r /captures/02_overlay.pcap -Y frame.number==1 -x
```

Structure d'une trame de l'overlay :

| Octets | Contenu | Remarque |
|---|---|---|
| 0 à 3 | Marqueur `E5A1` (`45 35 41 31`) | Identifie le format du laboratoire |
| 4 à 15 | Nonce de 12 octets | Aléatoire, différent à chaque trame |
| 16 à fin | Texte chiffré AES-256-GCM, suivi de l'étiquette d'authentification de 16 octets | Contient le message JSON (`probe`, `pong`, `req`, `resp`) |
| non transmis | Donnée associée authentifiée `MERIDIAN-LAB` | Connue des deux Edges, absente du paquet |

Le contenu situé après le marqueur est composé d'un nonce et d'un texte chiffré authentifié.

### 7.4 Aller plus loin : lire le message avec la clé de démonstration

La clé AES de ce laboratoire est publique. L'outil `decrypt-overlay` montre ce que lirait un tiers qui posséderait la clé :

```bash
docker compose exec paris-edge decrypt-overlay /captures/02_overlay.pcap --kind req,resp
docker compose exec paris-edge decrypt-overlay /captures/02_overlay.pcap --kind probe,pong
```

Exemple de sortie :

```text
#  22 t=   0.665s  172.28.20.10 -> 172.28.20.20  len= 100 kind=req   id=f329792b route=erp
#  35 t=   0.721s  172.28.20.20 -> 172.28.20.10  len= 316 kind=resp  id=f329792b code=200 path=mpls body=...
```

Un routeur intermédiaire, lui, ne voit que l'en-tête IP, l'en-tête UDP et des octets illisibles.

### 7.5 Pile protocolaire constatée

| Sur le LAN employé | Sur le transport WAN simulé |
|---|---|
| Client HTTP vers Edge Paris | Edge Paris vers Edge Berlin |
| IP privée / TCP / HTTP en clair dans le LAN pédagogique | IP underlay / UDP 45900 / message de labo chiffré AES-GCM |

### 7.6 Preuve C

```bash
docker compose exec paris-edge proof C_http_lan tshark -r /captures/01_all_traffic.pcap -Y 'tcp.dstport==8080 && http.request' -O http
docker compose exec paris-edge proof C_udp_hex tshark -r /captures/02_overlay.pcap -Y frame.number==1 -x
docker compose exec paris-edge proof C_decrypt decrypt-overlay /captures/02_overlay.pcap --kind req,resp
```

**Preuve C.** Fournir deux preuves : (1) la requête HTTP côté LAN (`C_http_lan.txt`), (2) un paquet UDP chiffré côté WAN (`C_udp_hex.txt`). Légender la pile protocolaire et répondre :

- Les routeurs intermédiaires peuvent-ils lire la requête métier ?
- Le chiffrement protège-t-il les adresses IP externes ?

### 7.7 Question d'ingénierie

En production, un tunnel IPsec ESP en mode tunnel protège un paquet IP d'origine (IKEv2 peut négocier les associations de sécurité). Ici, un proxy applicatif crée deux sessions HTTP distinctes et un canal UDP chiffré. Comparer ces deux architectures :

| Critère | IPsec ESP en mode tunnel avec IKEv2 | Overlay du laboratoire |
|---|---|---|
| Transparence IP | | |
| Ports utilisés | | |
| Performances | | |
| Confidentialité | | |
| Possibilités de capture | | |

---

## 8. Pause (01:55 - 02:05)

Avant la pause, vérifier que les deux fichiers `01_all_traffic.pcap` et `02_overlay.pcap` sont bien présents dans `captures/` et non vides :

```bash
docker compose exec paris-edge ls -l /captures
docker compose exec paris-edge capinfos /captures/01_all_traffic.pcap
```



---

## 9. Étape 4 : SLA, QoS et basculement (02:05 - 02:45)

Principe de décision de l'Edge Paris (voir `choose()` dans `edge.py`) :

1. Si le transport préféré par la politique est « up » et respecte `max_rtt_ms` et `max_loss_pct` : il est choisi (`preferred-and-within-sla`).
2. Sinon, un autre transport conforme au SLA est choisi (`alternate-within-sla`).
3. Sinon, un transport encore « up » est utilisé malgré tout (`degraded-no-path-meets-sla`).
4. Sinon : `503 no-underlay-available`.

Un transport est « up » s'il a répondu à une sonde dans les 3,5 dernières secondes. RTT et perte sont calculés sur une fenêtre glissante de 12 échantillons (une sonde par seconde et par transport). **Une mesure isolée n'est pas une preuve de disponibilité.**

### 9.1 Mission 4 : créer une baseline (10 min)

Récupérer la télémétrie et les chemins des applications à l'état nominal :

```bash
docker compose exec employee curl -s http://10.10.0.1:8080/status
docker compose exec employee curl -s http://10.10.0.1:8080/teams
docker compose exec employee curl -s http://10.10.0.1:8080/erp
docker compose exec employee proof D_nominal_sla sla
```

Noter le RTT moyen, la perte observée et le chemin choisi pour la ligne « Nominal » de la matrice (section 9.6).

### 9.2 Mission 5 : simuler un brownout (12 min)

Injecter 220 ms de délai sur les transmissions du transport Internet via le mécanisme pédagogique intégré. Il s'agit d'une émulation applicative reproductible, non d'un changement du réseau Docker lui-même.

```bash
docker compose exec employee curl -s 'http://10.10.0.1:8080/lab/impair?path=internet&loss=0&delay_ms=220'
sleep 15
docker compose exec employee proof D_brownout_sla sla
docker compose exec employee curl -s http://10.10.0.1:8080/status
docker compose exec employee curl -s http://10.10.0.1:8080/teams
```

Exemple de résultat observé :

```text
internet   up=true   rtt_ms=221.0   loss_pct=0.0   obs=12
mpls       up=true   rtt_ms=0.4     loss_pct=0.0   obs=12
erp        path=mpls       reason=preferred-and-within-sla
teams      path=mpls       reason=alternate-within-sla
```

Le RTT du transport dégradé doit augmenter : comparez-le au seuil de la politique Teams. Identifier le nouveau transport choisi et la justification `policy_reason`.

Note : la latence configurée est un délai d'émission unidirectionnel appliqué par l'Edge Paris. Le RTT dépend du comportement réel des requêtes et sondes.

**Mesurer le temps de réaction.** Lancer l'injection 5 secondes après le début du relevé, puis lire le moment où le chemin change :

```bash
docker compose exec -d employee sh -c 'sleep 5; curl -s http://10.10.0.1:8080/lab/impair?path=internet\&loss=0\&delay_ms=220 > /dev/null'
docker compose exec employee proof D_brownout_watch watchpath teams 30
```

Temps de réaction approximatif = heure du premier changement de chemin moins heure de l'injection (début du relevé plus 5 secondes).

### 9.3 Mission 6 : provoquer un blackout (10 min)

**Étape 1, retour à un état nominal mesuré.** Réinitialiser la latence puis **attendre 15 secondes** : la fenêtre de 12 échantillons doit se vider des mesures à 220 ms.

```bash
docker compose exec employee curl -s 'http://10.10.0.1:8080/lab/impair?path=internet&loss=0&delay_ms=0'
sleep 15
docker compose exec employee sla
```

Vérifier que `internet` affiche un RTT très faible. Si vous enchaînez le blackout sans cette attente, l'Edge verra encore un RTT Internet moyen élevé et affichera `degraded-no-path-meets-sla` au lieu de `alternate-within-sla` : un résultat à expliquer, pas une erreur.

**Étape 2, blackout du lien « MPLS simulé ».** Rendre 100 % des messages sortants de ce lien inaccessibles :

```bash
docker compose exec employee curl -s 'http://10.10.0.1:8080/lab/impair?path=mpls&loss=100&delay_ms=0'
sleep 6
docker compose exec employee proof D_blackout_sla sla
docker compose exec employee proof D_blackout_status curl -s http://10.10.0.1:8080/status
docker compose exec employee proof D_blackout_erp curl -s http://10.10.0.1:8080/erp
docker compose exec employee ip -br -4 addr
```

Vérifier qu'un chemin alternatif est sélectionné et que les adresses LAN restent inchangées (l'URL `10.10.0.1:8080` utilisée par le client n'a pas changé).

**Étape 3, mesurer la réaction.** Rétablir d'abord le lien, attendre 15 secondes, puis rejouer le blackout avec relevé :

```bash
docker compose exec employee curl -s 'http://10.10.0.1:8080/lab/impair?path=mpls&loss=0&delay_ms=0'
sleep 15
docker compose exec -d employee sh -c 'sleep 5; curl -s http://10.10.0.1:8080/lab/impair?path=mpls\&loss=100\&delay_ms=0 > /dev/null'
docker compose exec employee proof D_blackout_watch watchpath erp 20
```

Exemple de relevé (extrait) :

```text
21:39:41  erp  mpls preferred-and-within-sla | internet[up=true rtt=0.7 loss=0.0] mpls[up=true rtt=0.6 loss=0.0]
21:39:47  erp  mpls overlay-timeout         | internet[up=true rtt=0.7 loss=0.0] mpls[up=false rtt=0.6 loss=16.7]
21:39:48  erp  internet alternate-within-sla| internet[up=true rtt=0.7 loss=0.0] mpls[up=false rtt=0.6 loss=25.0]
```

La requête émise pendant la fenêtre de détection (transport encore considéré « up ») attend 5 secondes puis reçoit `504 overlay-timeout` : c'est le coût de la détection. Ensuite le trafic bascule.

**Vérification côté paquets (facultatif).** L'impairment est appliqué avant l'envoi : aucun paquet ne doit sortir sur le lien coupé. À vérifier avec une capture :

```bash
docker compose exec -d paris-edge sh -c 'timeout 15 tcpdump -i $(ifmap mpls) -nn -s 0 -U -Z root -w /captures/06_blackout_mpls.pcap udp port 45900'
sleep 2
docker compose exec employee curl -s 'http://10.10.0.1:8080/lab/impair?path=mpls&loss=100&delay_ms=0'
sleep 14
docker compose exec paris-edge tshark -r /captures/06_blackout_mpls.pcap -T fields -e frame.time_relative -e ip.src -e ip.dst
```

**Restaurer :**

```bash
docker compose exec employee curl -s 'http://10.10.0.1:8080/lab/impair?path=mpls&loss=0&delay_ms=0'
sleep 15
docker compose exec employee proof D_return_sla sla
```

### 9.4 Preuve D

**Preuve D.** Les fichiers `D_nominal_sla`, `D_brownout_sla`, `D_blackout_sla`, `D_return_sla`, `D_brownout_watch`, `D_blackout_watch`, et un tableau avant / après :

| Événement | Application | RTT (ms) | Perte (%) | Chemin choisi | `policy_reason` | Temps de réaction approximatif |
|---|---|---|---|---|---|---|
| Avant brownout | Teams | | | | | |
| Après brownout Internet | Teams | | | | | |
| Avant blackout | ERP | | | | | |
| Après blackout MPLS | ERP | | | | | |

Justifier pourquoi un brownout et un blackout ne doivent pas être diagnostiqués de la même manière.

### 9.5 Mode avancé optionnel : l'outil Linux `tc netem` (8 min)

Pour les groupes à l'aise avec les interfaces Linux, il est possible d'injecter du délai et de la perte au niveau du noyau sur l'interface Internet. Cette opération exige que le noyau Docker autorise `NET_ADMIN` (accordé dans `compose.yaml`) et le module `netem`. Si ce n'est pas disponible, rester sur la mission 5, suffisante pour la validation.

L'interface Internet est retrouvée avec `ifmap`, sans la présumer :

```bash
docker compose exec paris-edge ifmap internet
docker compose exec paris-edge sh -c 'tc qdisc replace dev $(ifmap internet) root netem delay 100ms loss 15%'
docker compose exec paris-edge sh -c 'tc -s qdisc show dev $(ifmap internet)'
sleep 15
docker compose exec employee sla
docker compose exec paris-edge sh -c 'tc qdisc del dev $(ifmap internet) root'
```

- Attendre environ 15 secondes entre injection et lecture de la télémétrie.
- **Ne jamais appliquer `netem` sur l'interface du réseau de contrôle.**
- L'absence du module noyau `sch_netem` n'est pas éliminatoire : documenter l'erreur et rester sur l'émulation applicative intégrée.
- Penser à supprimer la règle (dernière commande) avant de continuer.

### 9.6 Matrice de relevé obligatoire

| Test | Chemin initial | RTT | Perte | Résultat applicatif |
|---|---|---|---|---|
| Nominal / ERP | | | | |
| Nominal / Teams | | | | |
| Brownout Internet | | | | |
| Blackout MPLS | | | | |
| Retour nominal | | | | |

> **Point pédagogique.** L'outil est un proxy applicatif orienté politique. Il ne réalise pas de per-packet load balancing ni de duplication de paquets voix. En véritable SD-WAN, la mise en oeuvre précise du basculement dépend des constructeurs, des sondes, des sessions et de la configuration.

### 9.7 Questions de dimensionnement (sans correction fournie)

1. Une application voix utilise 64 kbit/s de payload, avant overhead. Quel trafic généreraient 100 appels simultanés, en ignorant puis en intégrant un overhead de 25 % ? Présenter les hypothèses.
2. Un lien à 100 Mbit/s transporte 92 Mbit/s en continu. Quel est le taux d'occupation et quelles conséquences attendre sur les files et la gigue ?
3. Pourquoi une bascule trop rapide peut-elle créer du flapping ? Proposer une temporisation de maintien et un seuil de retour distinct du seuil de départ.
4. Comment distinguer panne physique, perte sur un seul underlay, application lente et contrôleur indisponible ? Proposer un ordre de diagnostic.

---

## 10. Étape 5 : plan de contrôle, ZTP et haute disponibilité (02:45 - 03:15)

### 10.1 Mission 7 : coupure du contrôleur (12 min)

Le contrôleur distribue la politique, mais les Edges conservent leur dernier état. Faire d'abord une requête afin de connaître la génération de politique en cours, puis arrêter le contrôleur :

```bash
docker compose exec employee proof E_before_status curl -s http://10.10.0.1:8080/status
docker compose stop controller
```

Attendre au moins 8 secondes (l'Edge interroge le manager toutes les 3 secondes avec un délai de 1,5 seconde), puis relancer :

```bash
sleep 8
docker compose exec employee proof E_stopped_status curl -s http://10.10.0.1:8080/status
docker compose exec employee proof E_stopped_erp curl -s http://10.10.0.1:8080/erp
```

Observer `controller_reachable` (passé à `false`) et `generation` (inchangée). Décrire ce qui continue de fonctionner et les fonctions de gestion désormais impossibles.

**Observation côté paquets (facultatif).** Capturer le lien de contrôle avant, pendant et après l'arrêt :

```bash
docker compose exec -d paris-edge sh -c 'timeout 25 tcpdump -i $(ifmap control) -nn -s 0 -U -Z root -w /captures/07_control.pcap tcp port 9000'
sleep 8
docker compose stop controller
sleep 10
docker compose start controller
sleep 10
docker compose exec paris-edge tshark -r /captures/07_control.pcap -T fields -e frame.time_relative -e ip.src -e ip.dst -e tcp.flags.str
```

Restaurer le contrôleur et vérifier :

```bash
docker compose start controller
sleep 5
docker compose exec employee curl -s http://10.10.0.1:8080/status
```

### 10.2 Mission 8 : modifier une politique centrale (10 min)

Le contrôleur relit le JSON à chaque demande : aucune reconstruction n'est nécessaire.

**1. Noter la génération actuelle :**

```bash
docker compose exec employee proof E_policy_before curl -s http://10.10.0.1:8080/status
docker compose exec employee curl -s http://10.10.0.1:8080/erp
```

**2. Modifier `policy/policy.json`** dans un éditeur : changer uniquement la préférence de l'application `erp` de `mpls` vers `internet`, et mettre à jour le champ `generation` avec un nouveau libellé. Ne pas supprimer les accolades ni les virgules indispensables.

Avant :

```json
"generation": "2026-10-meridian-v1",
"erp": {"preferred": "mpls", "max_rtt_ms": 100, "max_loss_pct": 20},
```

Après :

```json
"generation": "2026-10-meridian-v2",
"erp": {"preferred": "internet", "max_rtt_ms": 100, "max_loss_pct": 20},
```

Variante en ligne de commande (Ubuntu) :

```bash
sed -i 's/"erp": {"preferred": "mpls"/"erp": {"preferred": "internet"/; s/meridian-v1/meridian-v2/' policy/policy.json
grep -n 'generation\|"erp"' policy/policy.json
```

Ou avec un éditeur (`nano policy/policy.json`, `vim policy/policy.json`) : le dossier `policy/` étant monté, un éditeur qui remplace le fichier est pris en compte.

**3. Valider le JSON puis attendre la propagation :**

```bash
docker compose exec controller python -m json.tool /lab/policy/policy.json
sleep 5
docker compose exec employee proof E_policy_after curl -s http://10.10.0.1:8080/status
docker compose exec employee proof E_policy_after_erp curl -s http://10.10.0.1:8080/erp
```

Comparer la politique et le chemin choisi. Si le JSON est invalide, le manager répond une erreur et l'Edge **conserve la dernière politique valide** : c'est un comportement à observer dans `controller_reachable` et `generation`.

**4. Revenir à la préférence initiale `mpls` avant la fin du TP :**

```bash
cp policy/policy.original.json policy/policy.json
```

```bash
sleep 5
docker compose exec employee sla
```

### 10.3 Preuve E

**Preuve E.** Les fichiers `E_before_status`, `E_stopped_status`, `E_stopped_erp`, `E_policy_before`, `E_policy_after`, `E_policy_after_erp`. Montrer :

- la génération de politique avant / après ;
- `controller_reachable` pendant l'arrêt ;
- la persistance d'une requête ERP pendant l'arrêt.

Expliquer la différence entre configuration centrale et transfert de données distribué.

### 10.4 ZTP, authentification et haute disponibilité

Le kit ne met pas en oeuvre un véritable enregistrement automatisé de nouvel Edge. Sur votre schéma d'architecture, décrire les six étapes de provisionnement Zero Touch :

| N° | Étape | À décrire : qui parle à qui, avec quelle identité, sur quel port |
|---|---|---|
| 1 | Mise sous tension | |
| 2 | Accès initial | |
| 3 | Découverte du manager | |
| 4 | Identité et certificat | |
| 5 | Récupération de politique | |
| 6 | Création du tunnel | |

Puis proposer :

- une stratégie de haute disponibilité des contrôleurs ;
- l'effet d'une perte prolongée des associations de sécurité en production.

---

## 11. Étape 6 : segmentation, breakout local et sécurité (03:15 - 03:40)

### 11.1 Mission 9 : le réseau invité (10 min)

Deux réseaux de clients sont isolés comme sous-réseaux Docker distincts. Le proxy de l'Edge applique une politique applicative sur les connexions invitées. Cette règle n'est ni un VRF, ni une isolation L3 complète.

```bash
docker compose exec employee curl -i http://10.10.0.1:8080/erp
docker compose exec guest curl -i http://10.11.0.1:8080/erp
docker compose exec guest curl -i http://10.11.0.1:8080/guest
```

Comparer les statuts HTTP, les adresses source et la décision de politique.

**Preuves réseau.** Capturer le LAN invité et lire la source et la décision :

```bash
docker compose exec -d paris-edge sh -c 'timeout 15 tcpdump -i $(ifmap guest_lan) -nn -s 0 -U -Z root -w /captures/04_guest_lan.pcap'
sleep 2
docker compose exec guest curl -s http://10.11.0.1:8080/erp
docker compose exec guest curl -s http://10.11.0.1:8080/guest
sleep 15
docker compose exec paris-edge tshark -r /captures/04_guest_lan.pcap -Y http -T fields -e frame.number -e ip.src -e ip.dst -e http.request.uri -e http.response.code
```

**Contrôles complémentaires de segmentation :**

```bash
docker compose exec guest curl -s -o /dev/null -w '%{http_code}\n' http://10.11.0.1:8080/status
docker compose exec berlin-edge curl -s -m 3 -o /dev/null -w '%{http_code}\n' http://172.28.10.10:8080/status
```

- La première commande montre que les routes d'administration sont refusées à l'invité (403).
- La seconde montre que le proxy HTTP de l'Edge Paris n'est pas joignable depuis l'underlay (code `000`, connexion refusée).

**Question.** Quelles mesures faudrait-il ajouter pour garantir une isolation réseau de bout en bout (VLAN/VRF, ACL, firewall stateful, identité) ?

### 11.2 Mission 10 : Local Internet breakout (8 min)

Le service SaaS de démonstration est raccordé au sous-réseau « Internet » virtuel. L'Edge Paris accède localement au SaaS et répond au client, sans passer par Berlin :

```bash
docker compose exec employee curl -s http://10.10.0.1:8080/saas
docker compose exec paris-edge curl -s http://172.28.10.40:8000/office
```

Tracer le chemin IP réel du proxy vers le SaaS :

```bash
docker compose exec paris-edge ip route get 172.28.10.40
docker compose exec paris-edge traceroute -n -m 3 172.28.10.40
docker compose exec -d paris-edge sh -c 'timeout 15 tcpdump -i $(ifmap internet) -nn -s 0 -U -Z root -w /captures/05_saas_breakout.pcap host 172.28.10.40'
sleep 2
docker compose exec employee curl -s http://10.10.0.1:8080/saas
sleep 15
docker compose exec paris-edge tshark -r /captures/05_saas_breakout.pcap -T fields -e frame.number -e ip.src -e ip.dst -e tcp.dstport -e http.request.uri
```

Constater l'absence de datagrammes UDP/45900 vers Berlin pour cette requête. Indiquer pourquoi ce test illustre seulement le principe de breakout local : il ne vérifie pas un NGFW, un service SSE/SASE, l'inspection TLS ni un accès Internet public.

### 11.3 Mini-audit : sécurité de production

1. Comparer AES-GCM pédagogique et IPsec ESP/IKEv2 : gestion des clés, rekeying, identité, replay et contrôle d'accès.
2. Identifier trois défauts de sécurité volontaires de ce kit. Pour chacun, proposer une correction déployable en entreprise.
3. Proposer les événements à journaliser dans un SIEM : changements de politique, état des tunnels, authentification ZTP, passages de chemin, refus de segmentation.
4. Expliquer où se situent SD-WAN, NGFW, SSE, SASE et Zero Trust dans une architecture cible.

Questions de lecture de code pour la question 2 :

- Où la clé de chiffrement est-elle définie et qui peut la lire ?
- Le canal entre Edge et manager est-il chiffré, authentifié ?
- Que se passe-t-il si une trame chiffrée valide est rejouée ?
- Qui peut appeler `/lab/impair` depuis le LAN employés ?
- Comment l'Edge décide-t-il qu'un client est « invité » ?

```bash
docker compose exec paris-edge grep -n 'seal\|unseal\|impair\|is_guest' /lab/edge.py
docker compose exec controller cat /lab/controller.py
```

### 11.4 Preuve F

```bash
docker compose exec employee proof F_erp_allowed curl -i http://10.10.0.1:8080/erp
docker compose exec guest proof F_erp_denied curl -i http://10.11.0.1:8080/erp
docker compose exec employee proof F_saas_local curl -s http://10.10.0.1:8080/saas
```

**Preuve F.** Les fichiers `F_erp_allowed`, `F_erp_denied`, `F_saas_local` et un court tableau :

| Risque | Preuve | Contre-mesure |
|---|---|---|
| | | |
| | | |
| | | |

---

## 12. Étape 7 : conception HLD/LLD et restitution (03:40 - 04:00)

### 12.1 Mission 11 : produire une proposition d'architecture (20 min)

Vous avez diagnostiqué les transporteurs du laboratoire. L'entreprise souhaite étendre cette architecture à **Paris, Londres, Berlin, deux data centers et un accès SaaS**. Votre proposition doit s'appuyer sur les principes des modules 6 et 7 du cours : conception, sécurité, fournisseurs, TCO et SLA.

| Livrable | Attendus |
|---|---|
| HLD, une page | Sites, clouds, hubs, underlays indépendants, overlay, sorties SaaS locales, contrôleurs redondés, segmentation métier/invité |
| LLD, une page | Sous-réseaux, interfaces, ports, politique par application, seuils SLA, temporisations, sondes et logs |
| Exploitation | Plan de surveillance : RTT, perte, disponibilité, état de politique, certificats, changements, alarmes |
| Sécurité | Chiffrement natif IPsec/IKEv2 ou équivalent fournisseur, PKI, NGFW/SSE, moindre privilège, audit |
| Comparaison fournisseurs | Comparer deux approches étudiées dans le cours sur cinq critères (gestion, overlay, sécurité, HA, coût), sans inventer de prix |
| Coût | Construire un mini-modèle CAPEX + 36 mois d'OPEX. Distinguer coûts récurrents et investissements |

### 12.2 Gabarits à compléter

**Politique par application (LLD)** : ERP, Teams, sauvegarde, invité.

| Application | Chemin préféré | Chemin de secours | RTT max (ms) | Perte max (%) | Temporisation de maintien | Seuil de retour | Sonde | Journalisation |
|---|---|---|---|---|---|---|---|---|
| ERP | | | | | | | | |
| Teams | | | | | | | | |
| Sauvegarde | | | | | | | | |
| Invité | | | | | | | | |

**Comparaison fournisseurs** (deux approches choisies dans le cours) :

| Critère | Approche 1 | Approche 2 |
|---|---|---|
| Gestion | | |
| Overlay | | |
| Sécurité | | |
| Haute disponibilité | | |
| Coût | | |

**Modèle de coût** : `TCO sur 36 mois = CAPEX + 36 x OPEX mensuel`. Poser vos hypothèses explicitement, sans inventer de prix constructeur.

| Poste | Type (CAPEX ou OPEX) | Hypothèse | Montant |
|---|---|---|---|
| | | | |

---

## 13. Dossier de preuves, barème et remise

### 13.1 Dossier de preuves à rendre

1. `01_all_traffic.pcap` et `02_overlay.pcap`, tous deux ouvrables dans Wireshark et lisibles avec `tshark`.
2. Six preuves A à F sous forme de **sorties de commandes horodatées** (`captures/preuves/*.txt`), chacune légendée dans le rapport. Ne pas déposer une suite de fichiers sans explication. Une capture d'écran du terminal reste acceptable en complément.
3. Tableau des chemins avant/après panne, y compris RTT, perte et contexte.
4. Schémas HLD et LLD annotés, politique justifiée pour ERP, Teams, sauvegarde et invité.
5. Diagnostic final : cause, preuve, conséquence, remédiation, en une page.

### 13.2 Fichiers attendus dans `captures/`

| Fichier | Étape | Statut |
|---|---|---|
| `01_all_traffic.pcap` | 2 | Obligatoire |
| `02_overlay.pcap` | 3 | Obligatoire |
| `preuves/A_*.txt` | 1 | Obligatoire |
| `preuves/B_*.txt` | 2 | Obligatoire |
| `preuves/C_*.txt` | 3 | Obligatoire |
| `preuves/D_*.txt` | 4 | Obligatoire |
| `preuves/E_*.txt` | 5 | Obligatoire |
| `preuves/F_*.txt` | 6 | Obligatoire |
| `01b_mpls_only.pcap`, `03_employee.pcap`, `03_paris_edge.pcap`, `04_guest_lan.pcap`, `05_saas_breakout.pcap`, `06_blackout_mpls.pcap`, `07_control.pcap` | 2 à 6 | Facultatifs, valorisés s'ils sont analysés |

Vérifier la liste depuis l'hôte :

```bash
docker compose exec paris-edge ls -l /captures /captures/preuves
```

### 13.3 Récapitulatif des preuves

| Preuve | Contenu attendu |
|---|---|
| A | `docker compose ps`, sortie `/status`, sortie `/erp`, différence entre `selected_path` et `policy_reason` |
| B | ICMP et UDP/45900 analysés, tableau IP/protocole/port/réseau, explication du « MPLS simulé » |
| C | Requête HTTP côté LAN et paquet UDP chiffré côté WAN, pile protocolaire légendée |
| D | Tableau avant/après : RTT, perte, application, chemin, raison, temps de réaction |
| E | Génération de politique avant/après, `controller_reachable`, persistance ERP |
| F | Accès ERP autorisé et refusé, SaaS local, tableau risque / preuve / contre-mesure |

### 13.4 Barème sur 20 points

| Critère | Points |
|---|---|
| Installation reproductible et découverte de la topologie | 3 |
| Captures PCAP, filtres et analyse protocolaire correcte | 5 |
| Mesures SLA, pannes, changement de chemin et preuves | 5 |
| Contrôle central, segmentation, sécurité et limites | 4 |
| HLD/LLD, argumentation et qualité du rapport | 3 |
| **Total** | **20** |

> **Enseignant.** Le sujet est volontairement sans correction. Évaluer d'abord les preuves (PCAP, état des conteneurs, observations mesurées), puis le raisonnement et le vocabulaire. Un étudiant qui décrit correctement une limite de l'émulateur doit être valorisé.

### 13.5 Remise à zéro

Avant de rendre la machine ou de repartir d'un état propre :

```bash
docker compose exec employee curl -s 'http://10.10.0.1:8080/lab/impair?path=internet&loss=0&delay_ms=0'
docker compose exec employee curl -s 'http://10.10.0.1:8080/lab/impair?path=mpls&loss=0&delay_ms=0'
docker compose exec paris-edge sh -c 'tc qdisc del dev $(ifmap internet) root'
```

La dernière commande échoue simplement si aucune règle `tc` n'avait été ajoutée : l'erreur est sans conséquence. Si la politique a été modifiée, la remettre dans son état d'origine :

```bash
cp policy/policy.original.json policy/policy.json
```

Puis arrêter uniquement ce laboratoire :

```bash
docker compose down
```

**Ne pas supprimer le dossier `captures`** : il contient les preuves PCAP. `docker compose down` ne le supprime pas.

---

## 14. Aide rapide : diagnostic et reprise

### 14.1 Commandes de santé

```bash
docker compose ps
docker compose logs --tail=35 paris-edge
docker compose logs --tail=35 berlin-edge
docker compose logs --tail=35 controller
docker compose exec paris-edge ifmap
docker compose exec paris-edge ip -br -4 addr
docker compose exec employee curl -s http://10.10.0.1:8080/status
docker compose exec employee sla
```

### 14.2 Tableau de diagnostic

| Symptôme | Procédure de diagnostic |
|---|---|
| Docker inaccessible | `systemctl status docker`, permissions sur le socket ou `sudo` |
| Un conteneur quitte | `docker compose logs <service>`, vérifier image et syntaxe des fichiers |
| Premier `/erp` échoue | `docker compose exec employee labwait`, contrôler les deux Edges et leurs journaux |
| Toujours `503` | Vérifier `/status`, pertes injectées (`impairment_training_only`), IP WAN, conteneur Berlin démarré |
| `504 overlay-timeout` | Route choisie disponible selon les sondes mais réponse applicative absente ou perdue : vérifier l'ERP (`docker compose ps`) et le chemin. Attendu pendant les 3 à 4 premières secondes d'un blackout |
| `degraded-no-path-meets-sla` | Aucun transport ne respecte le SLA sur la fenêtre de 12 mesures : attendre 15 secondes après une remise à zéro |
| PCAP vide | Vérifier que `tcpdump` est encore actif et que le trafic est généré pendant la capture |
| `tcpdump: ... Permission denied` | Vérifier que `-Z root` est bien présent dans la commande |
| PCAP illisible ou non modifiable sur l'hôte | Fichier créé par `root` : `sudo chown -R $USER:$USER captures` |
| `tshark: The file ... doesn't exist` | Le chemin est celui **du conteneur** : `/captures/nom.pcap` |
| `the input device is not a TTY` | Commande lancée sans terminal (script, `cron`) : ajouter `-T`, par exemple `docker compose exec -T ...` |
| `exec: "xxx": executable file not found` | Mauvais nom de service : `docker compose ps` |
| Politique non actualisée | `docker compose exec controller python -m json.tool /lab/policy/policy.json`, vérifier que le manager est démarré, attendre au moins 5 s |
| `controller_reachable: false` sans arrêt volontaire | `docker compose ps controller`, puis `docker compose logs controller` |
| `tc: Operation not permitted` ou `Specified qdisc kind is unknown` | Module `sch_netem` absent du noyau Ubuntu (section 3.6) ou `NET_ADMIN` refusé : garder la simulation `/lab/impair`, noter la limitation |
| `Pool overlaps with other one` | Un autre réseau Docker utilise les mêmes plages : arrêter l'autre projet |

### 14.3 Repartir d'un état propre

```bash
# Remettre les pertes et délais pédagogiques à zéro
docker compose exec employee curl -s 'http://10.10.0.1:8080/lab/impair?path=internet&loss=0&delay_ms=0'
docker compose exec employee curl -s 'http://10.10.0.1:8080/lab/impair?path=mpls&loss=0&delay_ms=0'

# Arrêter seulement ce laboratoire
docker compose down

# Redémarrer proprement
docker compose up -d --build --wait
docker compose exec employee labwait
```

Si une politique a été modifiée, remettre `policy/policy.json` dans son état original (voir 13.5). Si une règle `tc` a été ajoutée, la supprimer avant la remise.

---

## 15. Sources de référence

- Cours transmis : *SDWAN Architecture*, octobre 2026, 92 pages.
- Installation Docker Engine sur Ubuntu : <https://docs.docker.com/engine/install/ubuntu/>
- Post-installation Docker sous Linux : <https://docs.docker.com/engine/install/linux-postinstall/>
- Wireshark User Guide : <https://www.wireshark.org/docs/wsug_html/>
- Documentation `tshark` : <https://www.wireshark.org/docs/man-pages/tshark.html>
- Documentation `tcpdump` : <https://www.tcpdump.org/manpages/tcpdump.1.html>

> **Avertissement.** Simulateur pédagogique transparent et véritable trafic de paquets sur réseaux Docker séparés. Le chiffrement AES-GCM se fait dans `edge.py`. Ceci n'est **pas** IPsec (aucun IKEv2/ESP), pas du MPLS natif, pas un produit constructeur SD-WAN. Ne jamais utiliser ce code en production. Clé de démonstration publique.
