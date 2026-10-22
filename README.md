# Meridian Lab : TP SD-WAN réel, multisite et multi-transport

**E5 CCSN / SD-WAN - Édition étudiant - Atelier pratique, octobre 2026**

## Membres :
- LO Pape
- Gauyet NGUEFACK-TCHAMI
- Nina-merveille TCHAMBA-NGUETGNIA
- Edy DJIHOUA
- Désiree Madeleine ASSOUMOU-NDO
- Mahmoud-maigari NSANGOU-NJIKAM

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
<img width="1677" height="717" alt="image" src="https://github.com/user-attachments/assets/dfe19bdc-26b8-4e32-b1d2-527c7eb4b84a" />

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

<img width="1377" height="387" alt="image" src="https://github.com/user-attachments/assets/63a8bb68-6888-4411-8c81-0b7d821b3d78" />


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


```bash
git clone https://github.com/dspitech/SD-WAN.git
cd SD-WAN
ls
```

Résultat attendu : `Dockerfile  README.md  app.py  captures  compose.yaml  controller.py  edge.py  policy  scripts`.

<img width="1481" height="307" alt="image" src="https://github.com/user-attachments/assets/01b17a1b-d66d-4559-a027-c14c0c8154af" />


### 3.6 Module noyau `netem` (mode avancé uniquement)

Le mode avancé de l'étape 4 utilise `tc netem`, qui dépend du noyau **de l'hôte** (les conteneurs partagent le noyau d'Ubuntu). À vérifier :

```bash
sudo modprobe sch_netem && echo "netem disponible"
lsmod | grep sch_netem
```

<img width="1861" height="301" alt="image" src="https://github.com/user-attachments/assets/f0d300ff-acd3-4184-a50b-656093d8a066" />


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

<img width="1631" height="327" alt="image" src="https://github.com/user-attachments/assets/0bd83c49-2613-44d2-81b6-cfaca3372ec4" />


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

1. **Dossier de travail.** Toutes les commandes se lancent depuis le dossier `SD-WAN`, dans un terminal bash (SSH ou console).
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

Depuis le dossier `SD-WAN` :

```bash
docker compose up -d --build --wait
docker compose ps
```

<img width="1915" height="983" alt="image" src="https://github.com/user-attachments/assets/8faca30c-87a7-49d4-b3a7-e4ca157f5af4" />

<img width="1916" height="767" alt="image" src="https://github.com/user-attachments/assets/fe8370fa-a76d-47a1-a4e1-04a276631338" />


- `--build` construit l'image commune (premier démarrage : téléchargement de l'image Python, installation des utilitaires Linux, de `tshark` et du module de chiffrement Python, quelques minutes).
- `--wait` rend la main quand les services sont démarrés et sains. Si votre version de Compose ne le connaît pas, retirer l'option et utiliser `labwait` ci-dessous.

Résultat attendu : sept services `Up`, les services avec contrôle de santé (`controller`, `paris-edge`, `erp`, `saas`) en `healthy`.

### 5.2 Attendre la stabilisation des sondes

```bash
docker compose exec employee labwait
```

Résultat attendu : `pret : internet et mpls mesures up apres Ns`. Cela évite l'erreur `503 no-underlay-available` des premières secondes.

<img width="1657" height="340" alt="image" src="https://github.com/user-attachments/assets/289e5ad5-3bd5-4e8c-8387-07c378291f2d" />


### 5.3 Premières requêtes

```bash
docker compose exec employee curl -s http://10.10.0.1:8080/status
docker compose exec employee curl -s http://10.10.0.1:8080/erp
docker compose exec employee curl -s http://10.10.0.1:8080/teams
```

Résultat de sortie de `/status` (valeurs variables) :

```json
{
  "role": "paris",
  "generation": "2026-10-meridian-v1",
  "controller_reachable": true,
  "controller_last_seen": 1792646749.2292633,
  "http_listen": [
    "10.10.0.1:8080",
    "10.11.0.1:8080"
  ],
  "paths": {
    "internet": {
      "up": true,
      "rtt_ms": 2.3,
      "loss_pct": 0.0,
      "observations": 12
    },
    "mpls": {
      "up": true,
      "rtt_ms": 1.8,
      "loss_pct": 0.0,
      "observations": 12
    }
  },
  "impairment_training_only": {
    "internet": {
      "loss": 0.0,
      "delay_ms": 0
    },
    "mpls": {
      "loss": 0.0,
      "delay_ms": 0
    }
  }
}
```

Résultat de sortie de `/erp` :

```json
{
  "selected_path": "mpls",
  "policy_reason": "preferred-and-within-sla",
  "request_id": "eacec81d59084796a16305f1d1055c01",
  "remote": "{\"application\": \"erp\", \"path\": \"/erp?request=eacec81d59084796a16305f1d1055c01\", \"server_time\": 1792646867.514, \"message\": \"Reponse du service local au laboratoire.\"}"
```

Résultat de sortie de `/teams` :

```json
{
  "selected_path": "internet",
  "policy_reason": "preferred-and-within-sla",
  "request_id": "d837475a7887442fb150695192a345e3",
  "remote": "{\"application\": \"erp\", \"path\": \"/teams?request=d837475a7887442fb150695192a345e3\", \"server_time\": 1792646948.835, \"message\": \"Reponse du service local au laboratoire.\"}"
```

Vue synthétique avec l'outil `sla` :

```bash
docker compose exec employee sla
```
<img width="1610" height="477" alt="image" src="https://github.com/user-attachments/assets/55806bec-6e75-4a3e-8e44-d6c7ed4c0938" />


**État des transports (vue Edge Paris)**

| Transport | État | RTT moyen | Perte | Échantillons |
|---|---|---|---|---|
| `internet` | up | 2,6 ms | 0,0 % | 12 |
| `mpls` | up | 2,1 ms | 0,0 % | 12 |

Les deux transports sont mesurés « up » sur une fenêtre complète de 12 échantillons : la mesure est donc stabilisée et exploitable comme baseline. Les RTT sont très faibles (environ 2 ms) et sans perte, car tout s'exécute en local dans Docker. Ces valeurs ne modélisent pas la distance réelle Paris-Berlin, elles servent de référence pour comparer les dégradations qui suivront.

**Plan de contrôle**

`controller_reachable=true` : l'Edge Paris joint le manager et applique la politique de génération `2026-10-meridian-v1`.

**Chemin choisi par application**

| Application | Chemin | Raison | Interprétation |
|---|---|---|---|
| ERP | `mpls` | `preferred-and-within-sla` | Le transport préféré par la politique respecte les seuils (RTT et perte) |
| Teams | `internet` | `preferred-and-within-sla` | Idem, avec `internet` comme transport préféré |
| Sauvegarde | `internet` | `preferred-and-within-sla` | Idem, avec des seuils plus tolérants (350 ms, 60 %) |

Chaque application emprunte son transport préféré : la politique est appliquée telle qu'écrite et aucun basculement n'a lieu. La raison `preferred-and-within-sla` indique que la décision découle de la préférence (premier critère de choix) et non d'un secours. Aucune erreur n'est remontée (`error=-`).

**Résumé**

L'état nominal est sain : deux underlays disponibles, un contrôleur joignable, des applications sur leur chemin préféré. Cette baseline sert de point de comparaison pour le brownout (Teams devrait quitter `internet` si son RTT dépasse 100 ms) et pour le blackout (l'ERP devrait quitter `mpls` s'il devient indisponible).

### 5.4 Preuve A

```bash
docker compose ps | tee captures/preuves/A_compose_ps.txt
docker compose exec employee proof A_status curl -s http://10.10.0.1:8080/status
docker compose exec employee proof A_erp curl -s http://10.10.0.1:8080/erp
```

<img width="1907" height="777" alt="image" src="https://github.com/user-attachments/assets/006f3e6a-9f00-4494-b591-660f74ec36f5" />

<img width="1917" height="981" alt="image" src="https://github.com/user-attachments/assets/5e344147-1fb6-436c-bfda-8784cdaf40bb" />

<img width="1872" height="792" alt="image" src="https://github.com/user-attachments/assets/2c2a9848-810a-4076-98db-faf92ae189d8" />

<img width="1917" height="715" alt="image" src="https://github.com/user-attachments/assets/cb80c894-4251-451e-ae5e-a6902afa9b74" />

<img width="1661" height="302" alt="image" src="https://github.com/user-attachments/assets/7e74d31d-2f57-4600-97f0-15b2fbbafeb7" />


**Preuve A.** Les trois fichiers `A_compose_ps.txt`, `A_status.txt` et `A_erp.txt`, plus une phrase décrivant la différence entre `selected_path` et `policy_reason`.

La différence entre `selected_path` et `policy_reason` :

`selected_path` est le résultat de la décision (le transport réellement utilisé pour la requête, `mpls` ou `internet`), tandis que `policy_reason` en est la justification (la règle de la politique qui a conduit à ce choix, par exemple `preferred-and-within-sla` si le transport préféré respecte le SLA).

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

<img width="1897" height="572" alt="image" src="https://github.com/user-attachments/assets/8373eaa4-7a19-4b82-b0c0-aa0630b0dbf2" />


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

<img width="1796" height="805" alt="image" src="https://github.com/user-attachments/assets/29eb58d1-c0cd-4d55-a47d-c98c2a8d0174" />
<img width="1917" height="602" alt="image" src="https://github.com/user-attachments/assets/b88d4063-3154-4b16-b19d-84607090fc6c" />


`ifmap` affiche la table `INTERFACE / ADRESSE / RESEAU`. Les noms (`eth0`, `eth1`...) **varient d'une machine à l'autre : ne jamais supposer qu'`eth0` est Internet.** Utiliser `ifmap` pour retrouver le nom réel.

Conservation des preuves :

```bash
docker compose exec paris-edge proof M1_paris_ifmap ifmap
docker compose exec berlin-edge proof M1_berlin_ifmap ifmap
docker compose exec paris-edge proof M1_paris_route ip route
docker compose exec employee proof M1_employee_route ip route
```

Résultat : 

```txt
# preuve : M1_paris_ifmap
# date   : 2026-10-22T05:49:41Z
# noeud  : paris-edge
# cmd    : ifmap
INTERFACE  ADRESSE            RESEAU
eth0       10.10.0.1/24       paris_lan
eth1       172.28.30.11/24    control
eth2       10.11.0.1/24       guest_lan
eth3       172.28.10.10/24    internet
eth4       172.28.20.10/24    mpls
# enregistre dans captures/preuves/M1_paris_ifmap.txt

# preuve : M1_berlin_ifmap
# date   : 2026-10-22T05:49:42Z
# noeud  : berlin-edge
# cmd    : ifmap
INTERFACE  ADRESSE            RESEAU
eth0       10.20.0.1/24       berlin_lan
eth1       172.28.30.12/24    control
eth2       172.28.10.20/24    internet
eth3       172.28.20.20/24    mpls
# enregistre dans captures/preuves/M1_berlin_ifmap.txt

# preuve : M1_paris_route
# date   : 2026-10-22T05:49:42Z
# noeud  : paris-edge
# cmd    : ip route
10.10.0.0/24 dev eth0 proto kernel scope link src 10.10.0.1
10.11.0.0/24 dev eth2 proto kernel scope link src 10.11.0.1
172.28.10.0/24 dev eth3 proto kernel scope link src 172.28.10.10
172.28.20.0/24 dev eth4 proto kernel scope link src 172.28.20.10
172.28.30.0/24 dev eth1 proto kernel scope link src 172.28.30.11
# enregistre dans captures/preuves/M1_paris_route.txt

# preuve : M1_employee_route
# date   : 2026-10-22T05:49:43Z
# noeud  : employee
# cmd    : ip route
10.10.0.0/24 dev eth0 proto kernel scope link src 10.10.0.10
# enregistre dans captures/preuves/M1_employee_route.txt
```

**Travail demandé :**

- Noter les adresses exactes de Paris sur chaque underlay, les IP distantes correspondantes et les adresses des endpoints applicatifs.
- Faire un schéma avec les interfaces effectives (leurs noms peuvent varier).
- Compléter ce tableau pour l'Edge Paris :

| Interface (nom réel) | Réseau | Adresse | Plan fonctionnel (données, contrôle, gestion) |
|---|---|---|---|
| `eth0` | `paris_lan` | 10.10.0.1/24 | **Données** : trafic utilisateur des employés (HTTP/TCP 8080 vers le proxy de l'Edge) |
| `eth1` | `control` | 172.28.30.11/24 | **Contrôle et gestion** : interrogation du manager et récupération de la politique JSON (HTTP/TCP 9000) |
| `eth2` | `guest_lan` | 10.11.0.1/24 | **Données** : trafic des invités, filtré par la politique applicative (refus des applications métier) |
| `eth3` | `internet` | 172.28.10.10/24 | **Données** : overlay chiffré (UDP 45900) et breakout SaaS local (TCP 8000), **plus contrôle de chemin** : sondes RTT/perte |
| `eth4` | `mpls` | 172.28.20.10/24 | **Données** : overlay chiffré (UDP 45900), **plus contrôle de chemin** : sondes RTT/perte |

### 6.4 Mission 2 : observer ICMP, HTTP et UDP (20 min)

#### 6.4.1 Tester séparément chaque transport

L'option `-I` force l'adresse source choisie, donc le transport utilisé.

```bash
docker compose exec paris-edge ping -c 4 -I 172.28.10.10 172.28.10.20
docker compose exec paris-edge ping -c 4 -I 172.28.20.10 172.28.20.20
docker compose exec employee curl -v http://10.10.0.1:8080/erp
```
<img width="1902" height="460" alt="image" src="https://github.com/user-attachments/assets/476d27f6-140e-4bde-85ca-c2b8c546a8ab" />

<img width="1912" height="447" alt="image" src="https://github.com/user-attachments/assets/1917d0bf-88d1-4bd0-9505-b9df6a7a7bb2" />

<img width="1902" height="952" alt="image" src="https://github.com/user-attachments/assets/b24976bb-1d94-40cc-a348-77160d446b2e" />

Noter, pour chaque lien, le RTT moyen et la perte de paquets. Attention : les RTT du laboratoire local ne modélisent pas les distances Paris-Berlin.

### Mission 2 : RTT moyen et perte de paquets par lien

| Lien | Commande | RTT moyen | Perte de paquets |
|---|---|---|---|
| Internet (172.28.10.0/24) | `ping -c 4 -I 172.28.10.10 172.28.10.20` | **0,133 ms** | **0 %** (4 émis, 4 reçus) |
| « MPLS simulé » (172.28.20.0/24) | `ping -c 4 -I 172.28.20.10 172.28.20.20` | **0,122 ms** | **0 %** (4 émis, 4 reçus) |

**Remarque :** les RTT du laboratoire local ne modélisent pas les distances Paris-Berlin. Les deux transports sont des réseaux Docker sur la même machine, donc leurs RTT sont très faibles (environ 0,1 ms) et quasi identiques. Ils servent de référence pour comparer les dégradations injectées plus tard (brownout, blackout), pas à estimer la latence d'un vrai lien WAN.

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

Résultat : 

```txt
{
  "selected_path": "mpls",
  "policy_reason": "preferred-and-within-sla",
  "request_id": "2e6d77759e724dcc886a833c57d8e4fa",
  "remote": "{\"application\": \"erp\", \"path\": \"/erp?request=2e6d77759e724dcc886a833c57d8e4fa\", \"server_time\": 1792648642.494, \"message\": \"Reponse du service local au laboratoire.\"}"
}{
  "selected_path": "internet",
  "policy_reason": "preferred-and-within-sla",
  "request_id": "29fc293c2a9146979fddda68a84f692e",
  "remote": "{\"application\": \"erp\", \"path\": \"/teams?request=29fc293c2a9146979fddda68a84f692e\", \"server_time\": 1792648642.956, \"message\": \"Reponse du service local au laboratoire.\"}"
}PING 172.28.20.20 (172.28.20.20) 56(84) bytes of data.
64 bytes from 172.28.20.20: icmp_seq=1 ttl=64 time=0.112 ms
64 bytes from 172.28.20.20: icmp_seq=2 ttl=64 time=0.111 ms
64 bytes from 172.28.20.20: icmp_seq=3 ttl=64 time=0.136 ms

--- 172.28.20.20 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2046ms
rtt min/avg/max/mdev = 0.111/0.119/0.136/0.011 ms
total 76
-rw-r--r-- 1 root root 67087 Oct 22 05:58 01_all_traffic.pcap
drwxrwxr-x 2 1000 1000  4096 Oct 22 05:49 preuves
```

Le fichier `captures/01_all_traffic.pcap` doit apparaître dans le dossier `captures` du serveur. Comme `-i any` capte toutes les interfaces, chaque paquet porte un en-tête Linux « cooked » (SLL) à la place de l'en-tête Ethernet. Pour voir les adresses MAC d'un transport précis, capturer une seule interface :

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

<img width="1911" height="862" alt="image" src="https://github.com/user-attachments/assets/3cc79b5f-ab16-48ce-ba0a-6586cd70c425" />

<img width="1917" height="912" alt="image" src="https://github.com/user-attachments/assets/f704792d-3971-43f9-b645-d99ea0c0024c" />

<img width="1905" height="700" alt="image" src="https://github.com/user-attachments/assets/9205d768-8982-4187-90a7-8c4822b68568" />


Paquets ICMP (underlay) :

```bash
docker compose exec paris-edge tshark -r /captures/01_all_traffic.pcap -Y icmp -T fields -e frame.number -e frame.time_relative -e ip.src -e ip.dst -e icmp.type
```

<img width="1884" height="520" alt="image" src="https://github.com/user-attachments/assets/73635eb1-43b1-4d3c-9120-64211ade3535" />


Requêtes HTTP sur le LAN et sur le contrôle :

```bash
docker compose exec paris-edge tshark -r /captures/01_all_traffic.pcap -Y 'http.request' -T fields -e frame.number -e ip.src -e ip.dst -e tcp.dstport -e http.request.uri
```

<img width="1917" height="975" alt="image" src="https://github.com/user-attachments/assets/d4b39d5e-8e1c-4cdb-96dc-98b03fa83674" />


Sondes et flux du tunnel chiffré :

```bash
docker compose exec paris-edge sh -c 'tshark -r /captures/01_all_traffic.pcap -Y udp.port==45900 -T fields -e frame.number -e ip.src -e ip.dst -e udp.srcport -e udp.dstport -e udp.length 2>/dev/null | head -n 12'
```

<img width="1912" height="685" alt="image" src="https://github.com/user-attachments/assets/ab5db8e3-90fa-4bb9-b3e0-d00d6c187432" />


Trafic d'un transport précis :

```bash
docker compose exec paris-edge tshark -r /captures/01_all_traffic.pcap -Y 'ip.addr==172.28.20.20'
docker compose exec paris-edge tshark -r /captures/01_all_traffic.pcap -Y 'ip.src==172.28.10.10'
```

<img width="1917" height="975" alt="image" src="https://github.com/user-attachments/assets/67bdcb84-ea09-4055-9426-8ca239c9aef7" />

<img width="1915" height="961" alt="image" src="https://github.com/user-attachments/assets/8bff7c53-5bf2-4193-94de-4786771f15f2" />


Plan de contrôle (interrogation périodique de la politique) :

```bash
docker compose exec paris-edge tshark -r /captures/01_all_traffic.pcap -Y 'tcp.port==9000 && http' -T fields -e frame.time_relative -e ip.src -e ip.dst -e http.request.uri -e http.response.code
```

<img width="1907" height="970" alt="image" src="https://github.com/user-attachments/assets/f5dba22e-db23-4108-a019-d586a54770fe" />

#### 6.4.4 Preuve B

```bash
docker compose exec paris-edge proof B_icmp tshark -r /captures/01_all_traffic.pcap -Y icmp -T fields -e frame.number -e ip.src -e ip.dst -e ip.proto -e icmp.type
docker compose exec paris-edge proof B_udp45900 sh -c 'tshark -r /captures/01_all_traffic.pcap -Y udp.port==45900 -T fields -e frame.number -e ip.src -e ip.dst -e ip.proto -e udp.srcport -e udp.dstport 2>/dev/null | head -n 10'
```

<img width="1915" height="817" alt="image" src="https://github.com/user-attachments/assets/8c5eae09-e79d-4034-840d-39dd3edbe541" />

<img width="1907" height="907" alt="image" src="https://github.com/user-attachments/assets/f37416bd-62d2-441d-9005-86351dd3d2d0" />

<img width="1336" height="322" alt="image" src="https://github.com/user-attachments/assets/bf906339-8c11-41b3-945d-94779a33fd0e" />


**Preuve B.** Les fichiers `B_icmp.txt` et `B_udp45900.txt`, avec ce tableau complété pour un paquet ICMP et un paquet UDP/45900 :

### Preuve B : paquets ICMP et UDP/45900 analysés

| Paquet | IP source | IP destination | Protocole | Port | Réseau sous-jacent |
|---|---|---|---|---|---|
| ICMP (trame 69, Echo Request, type 8) | 172.28.20.10 (Edge Paris) | 172.28.20.20 (Edge Berlin) | ICMP (numéro de protocole IP 1) | sans objet | « MPLS simulé » 172.28.20.0/24 |
| UDP (trame 1, sonde ou flux de l'overlay) | 172.28.10.10 (Edge Paris) | 172.28.10.20 (Edge Berlin) | UDP (numéro de protocole IP 17) | 45900 vers 45900 | Internet 172.28.10.0/24 |

**Lecture.** L'ICMP provient du `ping -c 3 172.28.20.20` lancé pendant la capture : chaque Echo Request (type 8) est suivi de son Echo Reply (type 0), ce qui donne trois paires. Les datagrammes UDP/45900 sont envoyés en continu sur les deux transports à la fois (trames 1 à 8 : Internet et MPLS, dans les deux sens). Cela correspond aux sondes de mesure RTT et perte de l'Edge, ainsi qu'aux messages applicatifs chiffrés.

### Pourquoi le transport « MPLS simulé » n'est pas du MPLS natif

Le MPLS natif repose sur des **étiquettes** (labels) de 32 bits insérées entre l'en-tête de couche 2 et l'en-tête IP (EtherType `0x8847`). Les routeurs du cœur de réseau (LSR) commutent les paquets en lisant uniquement ce label, qu'ils échangent à chaque saut sur un chemin établi à l'avance (LSP, signalé par LDP ou RSVP-TE). Il sert aussi à porter des VPN de couche 3 (VRF) et des classes de service (champ TC).

Ici, le « MPLS » n'est qu'un **second réseau IP ordinaire** (172.28.20.0/24) :

- les trames sont de l'IPv4 classique (`Ethernet / IP / UDP`), sans aucun label MPLS ;
- aucun LSR, LDP, LSP ou VRF n'existe : la commutation se fait par adresse IP de destination sur un seul segment ;
- il joue seulement le rôle de **deuxième transport indépendant**, pour étudier le choix de chemin selon le SLA.

On peut le vérifier sur la capture d'une seule interface, qui contient les en-têtes Ethernet :

```bash
    docker compose exec paris-edge sh -c 'tshark -r /captures/01b_mpls_only.pcap -Y mpls 2>/dev/null | wc -l'
    docker compose exec paris-edge tshark -r /captures/01b_mpls_only.pcap -T fields -e eth.type -e ip.src -e ip.dst
```

<img width="1926" height="972" alt="image" src="https://github.com/user-attachments/assets/7edbc428-a524-4701-bc9b-01305d41ca14" />

Le premier compte doit valoir **0** (aucun paquet MPLS). Le champ `eth.type` doit valoir `0x0800` (IPv4), jamais `0x8847` (MPLS).

#### 6.4.5 Questions de recherche

1. Combien d'interfaces IP l'Edge Paris possède-t-il ? À quel plan fonctionnel associeriez-vous chaque trafic ?

```bash
docker compose exec paris-edge ifmap
docker compose exec paris-edge sh -c 'ip -o -4 addr show scope global | wc -l'
```
<img width="1814" height="520" alt="image" src="https://github.com/user-attachments/assets/e5fcae24-3121-4057-bd46-e3809602445c" />

L'Edge Paris possède **5 interfaces IP** (hors loopback), une par réseau.

| Interface | Réseau | Trafic observé | Plan fonctionnel |
|---|---|---|---|
| `eth0` | `paris_lan` | TCP 8080, HTTP des employés vers le proxy | Données (accès utilisateur) |
| `eth2` | `guest_lan` | TCP 8080, HTTP des invités, filtré par la politique | Données (accès invité) |
| `eth3` | `internet` | UDP 45900 (overlay chiffré, sondes), TCP 8000 vers le SaaS | Données (transport) et contrôle de chemin (sondes SLA) |
| `eth4` | `mpls` | UDP 45900 (overlay chiffré, sondes) | Données (transport) et contrôle de chemin (sondes SLA) |
| `eth1` | `control` | TCP 9000, interrogation de la politique JSON | Contrôle et gestion |

2. Quelle différence observez-vous entre une capture côté `employee` et côté `paris-edge` ?

```bash
docker compose exec -d employee sh -c 'timeout 15 tcpdump -i any -nn -s 0 -U -Z root -w /captures/03_employee.pcap'
docker compose exec -d paris-edge sh -c 'timeout 15 tcpdump -i any -nn -s 0 -U -Z root -w /captures/03_paris_edge.pcap'
sleep 2
docker compose exec employee curl -s http://10.10.0.1:8080/erp
sleep 15
docker compose exec employee tshark -r /captures/03_employee.pcap -q -z conv,ip
docker compose exec paris-edge tshark -r /captures/03_paris_edge.pcap -q -z conv,ip
```

<img width="1901" height="761" alt="image" src="https://github.com/user-attachments/assets/f8c79129-d9de-475e-93c9-751dd98e2979" />

<img width="1917" height="976" alt="image" src="https://github.com/user-attachments/assets/91fc4851-10ed-4399-8876-54228732ff71" />

### Différence entre une capture côté `employee` et côté `paris-edge`

| Critère | Capture `employee` | Capture `paris-edge` |
|---|---|---|
| Conversations IPv4 | 1 seule | 5 |
| Adresses vues | 10.10.0.10 et 10.10.0.1 uniquement | Aussi 172.28.10.x, 172.28.20.x et 172.28.30.x |
| Session HTTP/TCP 8080 | Oui, 12 trames, 1445 octets | Oui, la même session (12 trames, 1445 octets) |
| Overlay UDP 45900 | Absent | Présent sur Internet (30 trames) et MPLS (32 trames) |
| Plan de contrôle TCP 9000 | Absent | Présent (48 trames, une interrogation toutes les 3 s) |
| Trafic de fond | Aucun | Sondes SLA permanentes, même sans requête utilisateur |

**Observation.** Le client ne voit qu'une session HTTP vers l'Edge : il ignore le transport
choisi, le chiffrement et l'overlay. L'Edge voit la même session HTTP, mais aussi les
datagrammes UDP/45900 chiffrés échangés avec Berlin sur les deux underlays et
l'interrogation périodique du manager. La requête `/erp` apparaît côté WAN comme 2 trames
supplémentaires sur le transport MPLS (32 trames contre 30 sur Internet), ce qui confirme
`selected_path: mpls`.

**Interprétation.** L'Edge termine la session HTTP du LAN et en crée une nouvelle côté WAN :
c'est un proxy applicatif, pas un routeur. Un tunnel IPsec ESP transporterait au contraire le
paquet IP d'origine, et le client et le WAN partageraient alors un même flux. Côté Edge, on
distingue aussi trois plans : données (HTTP et UDP 45900), contrôle de chemin (sondes) et
gestion (TCP 9000), alors que le client n'a accès qu'au plan de données.

  
3. Un simple `ping` réussi garantit-il l'accessibilité de l'ERP ? Proposer deux contre-exemples.

Un `ping` ne teste que la couche IP (ICMP). L'ERP dépend de la chaîne complète : transport UDP 45900, Edge Berlin, puis le serveur `erp`. Il suffit de casser un maillon au-dessus d'ICMP et de montrer que le `ping` continue de répondre.

### Contre-exemple 1 : le serveur ERP est arrêté

```bash
docker compose stop erp
docker compose exec paris-edge ping -c 3 -I 172.28.20.10 172.28.20.20
docker compose exec employee proof Q3_erp_arrete curl -s -m 10 -w '\nHTTP %{http_code}\n' http://10.10.0.1:8080/erp
docker compose exec employee sla
docker compose start erp
```

<img width="1807" height="920" alt="image" src="https://github.com/user-attachments/assets/c281c23c-09f5-4c16-8939-d65adb77eb60" />


**À observer :**

- Le `ping` vers l'Edge Berlin répond toujours : l'underlay est sain.
- `/erp` renvoie une erreur HTTP 502 après quelques secondes : l'Edge Berlin n'a pas pu joindre le serveur.
- `sla` montre toujours les deux transports `up` : les sondes de l'Edge testent le chemin, pas l'application. Aucun basculement ne résoudrait cette panne.
- Teams et la sauvegarde échouent aussi, car dans ce laboratoire tous les flux métier aboutissent au même serveur de Berlin.

### Contre-exemple 2 : l'overlay est coupé alors que l'IP fonctionne

Avec l'émulation applicative du TP :

```bash
docker compose exec employee curl -s 'http://10.10.0.1:8080/lab/impair?path=mpls&loss=100&delay_ms=0'
docker compose exec paris-edge ping -c 3 -I 172.28.20.10 172.28.20.20
docker compose exec employee proof Q3_overlay_coupe curl -s -m 10 -w '\nHTTP %{http_code}\n' http://10.10.0.1:8080/erp
docker compose exec employee curl -s 'http://10.10.0.1:8080/lab/impair?path=mpls&loss=0&delay_ms=0'
```

<img width="1917" height="945" alt="image" src="https://github.com/user-attachments/assets/ba130d84-7895-4bdb-9dd6-8179fb456906" />


Le `ping` répond, car l'émulation ne touche que les messages de l'overlay. Pendant les premières secondes, `/erp` donne `504 overlay-timeout`, puis la politique bascule sur `internet`.

### Variante plus réaliste (facultative) : filtrage du port UDP 45900

C'est l'équivalent d'un pare-feu qui laisse passer ICMP mais bloque l'application. Le module netfilter de l'hôte doit être disponible, sinon la commande échoue sans conséquence.

```bash
docker compose exec berlin-edge iptables -A INPUT -p udp --dport 45900 -j DROP
docker compose exec paris-edge ping -c 3 -I 172.28.10.10 172.28.10.20
sleep 6
docker compose exec employee curl -s -m 10 -w '\nHTTP %{http_code}\n' http://10.10.0.1:8080/erp
docker compose exec berlin-edge iptables -D INPUT -p udp --dport 45900 -j DROP
```

<img width="1846" height="647" alt="image" src="https://github.com/user-attachments/assets/c6bc25ad-4f2e-4f03-9882-0f05edafaa5c" />


Les sondes utilisent aussi UDP 45900, donc les deux transports passent `down`. On doit obtenir `503 no-underlay-available` alors que le `ping` fonctionne. **Supprimer la règle** (dernière commande) avant de continuer, puis `sleep 15` et `sla` pour vérifier le retour à l'état nominal.

### Réponse

**Non.** Un `ping` teste seulement l'accessibilité IP (ICMP) d'un lien. L'ERP dépend en plus du transport UDP 45900, de l'Edge Berlin et du serveur applicatif.

| Contre-exemple | Manipulation | `ping` underlay | Résultat de `/erp` |
|---|---|---|---|
| Serveur ERP arrêté | `docker compose stop erp` | Réussi, 0 % de perte | Erreur HTTP 502, alors que les deux transports restent `up` dans `sla` |
| Overlay coupé sur un transport | `loss=100` sur `mpls` | Réussi, 0 % de perte | `504 overlay-timeout` pendant la détection, puis bascule sur `internet` |
| Port UDP 45900 filtré (facultatif) | Règle `iptables` sur `berlin-edge` | Réussi | `503 no-underlay-available` |

**Résumé.** Il faut superviser chaque couche : lien IP, sondes SLA du chemin, port applicatif et service final. Les sondes de l'Edge ne détectent pas une panne de l'application, qui exige une supervision applicative (health check HTTP) en plus de la surveillance du lien.
Pistes d'expérimentation (sans correction) :

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

Résultat :

```json
{
  "selected_path": "mpls",
  "policy_reason": "preferred-and-within-sla",
  "request_id": "822b4a2cbe77432d9c54b331604e75fe",
  "remote": "{\"application\": \"erp\", \"path\": \"/erp?request=822b4a2cbe77432d9c54b331604e75fe\", \"server_time\": 1792650638.171, \"message\": \"Reponse du service local au laboratoire.\"}"
}{
  "selected_path": "internet",
  "policy_reason": "preferred-and-within-sla",
  "request_id": "7bc793b6431a4e6b9b3583d95b7c81cc",
  "remote": "{\"application\": \"erp\", \"path\": \"/teams?request=7bc793b6431a4e6b9b3583d95b7c81cc\", \"server_time\": 1792650638.53, \"message\": \"Reponse du service local au laboratoire.\"}"
}{
  "role": "paris",
  "generation": "2026-10-meridian-v1",
  "controller_reachable": true,
  "controller_last_seen": 1792650637.057963,
  "http_listen": [
    "10.10.0.1:8080",
    "10.11.0.1:8080"
  ],
  "paths": {
    "internet": {
      "up": true,
      "rtt_ms": 2.3,
      "loss_pct": 0.0,
      "observations": 12
    },
    "mpls": {
      "up": true,
      "rtt_ms": 1.8,
      "loss_pct": 0.0,
      "observations": 12
    }
  },
  "impairment_training_only": {
    "internet": {
      "loss": 0.0,
      "delay_ms": 0
    },
    "mpls": {
      "loss": 0.0,
      "delay_ms": 0
    }
  }
}
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

<img width="1917" height="686" alt="image" src="https://github.com/user-attachments/assets/90be09d7-c604-4b3b-94c1-9158016decb2" />

### 7.3 Analyser le datagramme chiffré en ligne de commande

Liste des datagrammes (en-tête IP externe et en-tête UDP) :

```bash
docker compose exec paris-edge sh -c 'tshark -r /captures/02_overlay.pcap -T fields -e frame.number -e frame.time_relative -e ip.src -e ip.dst -e udp.srcport -e udp.dstport -e udp.length 2>/dev/null | head -n 15'
```

<img width="1902" height="802" alt="image" src="https://github.com/user-attachments/assets/7deabcc7-de2d-4e61-afc4-2173c1790ae8" />


Comptage des trames portant le marqueur `E5A1` (hexadécimal `45 35 41 31`) :

```bash
docker compose exec paris-edge sh -c 'tshark -r /captures/02_overlay.pcap -Y udp.port==45900 2>/dev/null | wc -l'
docker compose exec paris-edge sh -c 'tshark -r /captures/02_overlay.pcap -Y udp.payload[0:4]==45:35:41:31 2>/dev/null | wc -l'
```

<img width="1917" height="496" alt="image" src="https://github.com/user-attachments/assets/160ceb96-a434-4af5-89d8-1a325064d4f6" />


Octets du payload d'un paquet (hexadécimal et ASCII) :

```bash
docker compose exec paris-edge tshark -r /captures/02_overlay.pcap -Y frame.number==1 -x
```

<img width="1917" height="610" alt="image" src="https://github.com/user-attachments/assets/e56f7e37-c984-4e4f-b495-f971fe811f1e" />


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

<img width="1917" height="976" alt="image" src="https://github.com/user-attachments/assets/bd9716a6-5e7b-4e5b-84dc-fd38c8fe7526" />

<img width="1915" height="977" alt="image" src="https://github.com/user-attachments/assets/2d56ccf1-813c-43a5-9d4a-4621ac8452d5" />

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

Résultat : 
```txt
# preuve : C_http_lan
# date   : 2026-10-22T06:40:09Z
# noeud  : paris-edge
# cmd    : tshark -r /captures/01_all_traffic.pcap -Y tcp.dstport==8080 && http.request -O http

Running as user "root" and group "root". This could be dangerous.
Frame 28: 153 bytes on wire (1224 bits), 153 bytes captured (1224 bits)
Linux cooked capture v2
Internet Protocol Version 4, Src: 10.10.0.10, Dst: 10.10.0.1
Transmission Control Protocol, Src Port: 46276, Dst Port: 8080, Seq: 1, Ack: 1, Len: 81
Hypertext Transfer Protocol
    GET /erp HTTP/1.1\r\n
        Request Method: GET
        Request URI: /erp
        Request Version: HTTP/1.1
    Host: 10.10.0.1:8080\r\n
    User-Agent: curl/8.14.1\r\n
    Accept: */*\r\n
    \r\n
    [Full request URI: http://10.10.0.1:8080/erp]

Frame 42: 156 bytes on wire (1248 bits), 156 bytes captured (1248 bits)
Linux cooked capture v2
Internet Protocol Version 4, Src: 10.10.0.1, Dst: 10.10.0.1
Transmission Control Protocol, Src Port: 55816, Dst Port: 8080, Seq: 1, Ack: 1, Len: 84
Hypertext Transfer Protocol
    GET /status HTTP/1.1\r\n
        Request Method: GET
        Request URI: /status
        Request Version: HTTP/1.1
    Host: 10.10.0.1:8080\r\n
    User-Agent: curl/8.14.1\r\n
    Accept: */*\r\n
    \r\n
    [Full request URI: http://10.10.0.1:8080/status]

Frame 54: 155 bytes on wire (1240 bits), 155 bytes captured (1240 bits)
Linux cooked capture v2
Internet Protocol Version 4, Src: 10.10.0.10, Dst: 10.10.0.1
Transmission Control Protocol, Src Port: 48502, Dst Port: 8080, Seq: 1, Ack: 1, Len: 83
Hypertext Transfer Protocol
    GET /teams HTTP/1.1\r\n
        Request Method: GET
        Request URI: /teams
        Request Version: HTTP/1.1
    Host: 10.10.0.1:8080\r\n
    User-Agent: curl/8.14.1\r\n
    Accept: */*\r\n
    \r\n
    [Full request URI: http://10.10.0.1:8080/teams]

Frame 110: 156 bytes on wire (1248 bits), 156 bytes captured (1248 bits)
Linux cooked capture v2
Internet Protocol Version 4, Src: 10.10.0.1, Dst: 10.10.0.1
Transmission Control Protocol, Src Port: 55826, Dst Port: 8080, Seq: 1, Ack: 1, Len: 84
Hypertext Transfer Protocol
    GET /status HTTP/1.1\r\n
        Request Method: GET
        Request URI: /status
        Request Version: HTTP/1.1
    Host: 10.10.0.1:8080\r\n
    User-Agent: curl/8.14.1\r\n
    Accept: */*\r\n
    \r\n
    [Full request URI: http://10.10.0.1:8080/status]

Frame 166: 156 bytes on wire (1248 bits), 156 bytes captured (1248 bits)
Linux cooked capture v2
Internet Protocol Version 4, Src: 10.10.0.1, Dst: 10.10.0.1
Transmission Control Protocol, Src Port: 33400, Dst Port: 8080, Seq: 1, Ack: 1, Len: 84
Hypertext Transfer Protocol
    GET /status HTTP/1.1\r\n
        Request Method: GET
        Request URI: /status
        Request Version: HTTP/1.1
    Host: 10.10.0.1:8080\r\n
    User-Agent: curl/8.14.1\r\n
    Accept: */*\r\n
    \r\n
    [Full request URI: http://10.10.0.1:8080/status]

Frame 230: 156 bytes on wire (1248 bits), 156 bytes captured (1248 bits)
Linux cooked capture v2
Internet Protocol Version 4, Src: 10.10.0.1, Dst: 10.10.0.1
Transmission Control Protocol, Src Port: 33404, Dst Port: 8080, Seq: 1, Ack: 1, Len: 84
Hypertext Transfer Protocol
    GET /status HTTP/1.1\r\n
        Request Method: GET
        Request URI: /status
        Request Version: HTTP/1.1
    Host: 10.10.0.1:8080\r\n
    User-Agent: curl/8.14.1\r\n
    Accept: */*\r\n
    \r\n
    [Full request URI: http://10.10.0.1:8080/status]

Frame 286: 156 bytes on wire (1248 bits), 156 bytes captured (1248 bits)
Linux cooked capture v2
Internet Protocol Version 4, Src: 10.10.0.1, Dst: 10.10.0.1
Transmission Control Protocol, Src Port: 60252, Dst Port: 8080, Seq: 1, Ack: 1, Len: 84
Hypertext Transfer Protocol
    GET /status HTTP/1.1\r\n
        Request Method: GET
        Request URI: /status
        Request Version: HTTP/1.1
    Host: 10.10.0.1:8080\r\n
    User-Agent: curl/8.14.1\r\n
    Accept: */*\r\n
    \r\n
    [Full request URI: http://10.10.0.1:8080/status]

Frame 330: 156 bytes on wire (1248 bits), 156 bytes captured (1248 bits)
Linux cooked capture v2
Internet Protocol Version 4, Src: 10.10.0.1, Dst: 10.10.0.1
Transmission Control Protocol, Src Port: 60256, Dst Port: 8080, Seq: 1, Ack: 1, Len: 84
Hypertext Transfer Protocol
    GET /status HTTP/1.1\r\n
        Request Method: GET
        Request URI: /status
        Request Version: HTTP/1.1
    Host: 10.10.0.1:8080\r\n
    User-Agent: curl/8.14.1\r\n
    Accept: */*\r\n
    \r\n
    [Full request URI: http://10.10.0.1:8080/status]

Frame 389: 156 bytes on wire (1248 bits), 156 bytes captured (1248 bits)
Linux cooked capture v2
Internet Protocol Version 4, Src: 10.10.0.1, Dst: 10.10.0.1
Transmission Control Protocol, Src Port: 58298, Dst Port: 8080, Seq: 1, Ack: 1, Len: 84
Hypertext Transfer Protocol
    GET /status HTTP/1.1\r\n
        Request Method: GET
        Request URI: /status
        Request Version: HTTP/1.1
    Host: 10.10.0.1:8080\r\n
    User-Agent: curl/8.14.1\r\n
    Accept: */*\r\n
    \r\n
    [Full request URI: http://10.10.0.1:8080/status]

Frame 445: 156 bytes on wire (1248 bits), 156 bytes captured (1248 bits)
Linux cooked capture v2
Internet Protocol Version 4, Src: 10.10.0.1, Dst: 10.10.0.1
Transmission Control Protocol, Src Port: 58302, Dst Port: 8080, Seq: 1, Ack: 1, Len: 84
Hypertext Transfer Protocol
    GET /status HTTP/1.1\r\n
        Request Method: GET
        Request URI: /status
        Request Version: HTTP/1.1
    Host: 10.10.0.1:8080\r\n
    User-Agent: curl/8.14.1\r\n
    Accept: */*\r\n
    \r\n
    [Full request URI: http://10.10.0.1:8080/status]

# enregistre dans captures/preuves/C_http_lan.txt
# preuve : C_udp_hex
# date   : 2026-10-22T06:40:10Z
# noeud  : paris-edge
# cmd    : tshark -r /captures/02_overlay.pcap -Y frame.number==1 -x

Running as user "root" and group "root". This could be dangerous.
0000  08 00 00 00 00 00 00 05 00 01 04 06 a2 53 b7 4d   .............S.M
0010  32 ff 00 00 45 00 00 74 84 ef 40 00 40 11 49 33   2...E..t..@.@.I3
0020  ac 1c 0a 0a ac 1c 0a 14 b3 4c b3 4c 00 60 6c c8   .........L.L.`l.
0030  45 35 41 31 2f 0b ac f3 5a 4f 49 38 91 7d 49 3d   E5A1/...ZOI8.}I=
0040  63 57 bc cb f5 91 6d 30 7e 10 d4 67 48 8c 1d d5   cW....m0~..gH...
0050  fc 52 db e5 f7 1c b0 84 7d 32 23 58 8e c2 01 d1   .R......}2#X....
0060  bb 0e a4 40 71 22 de 9a 47 9c 3f d4 26 80 c9 3b   ...@q"..G.?.&..;
0070  3d d7 c5 35 43 cc 4b 25 5d 53 21 70 a4 11 9e 04   =..5C.K%]S!p....
0080  0d 6e b8 c1 02 1e f3 ad                           .n......

# enregistre dans captures/preuves/C_udp_hex.txt
# preuve : C_decrypt
# date   : 2026-10-22T06:40:11Z
# noeud  : paris-edge
# cmd    : decrypt-overlay /captures/02_overlay.pcap --kind req,resp

#   9 t=   2.002s  172.28.20.10 -> 172.28.20.20  len= 100 kind=req   id=ade66342 route=erp
#  14 t=   2.006s  172.28.20.20 -> 172.28.20.10  len= 317 kind=resp  id=ade66342 code=200 path=mpls body={"application": "erp", "path": "/erp?request=ade663422054465a980cb6beb
#  15 t=   2.028s  172.28.20.10 -> 172.28.20.20  len= 100 kind=req   id=db2559b5 route=erp
#  16 t=   2.032s  172.28.20.20 -> 172.28.20.10  len= 317 kind=resp  id=db2559b5 code=200 path=mpls body={"application": "erp", "path": "/erp?request=db2559b579074d859db2888a6
#  17 t=   2.054s  172.28.20.10 -> 172.28.20.20  len= 100 kind=req   id=9dd13f68 route=erp
#  18 t=   2.058s  172.28.20.20 -> 172.28.20.10  len= 317 kind=resp  id=9dd13f68 code=200 path=mpls body={"application": "erp", "path": "/erp?request=9dd13f68b1634e09bb3f8984d
#  19 t=   2.081s  172.28.20.10 -> 172.28.20.20  len= 100 kind=req   id=400ee5e2 route=erp
#  20 t=   2.084s  172.28.20.20 -> 172.28.20.10  len= 317 kind=resp  id=400ee5e2 code=200 path=mpls body={"application": "erp", "path": "/erp?request=400ee5e2749248cba672d7a4d
#  21 t=   2.106s  172.28.20.10 -> 172.28.20.20  len= 100 kind=req   id=7d703509 route=erp
#  22 t=   2.110s  172.28.20.20 -> 172.28.20.10  len= 317 kind=resp  id=7d703509 code=200 path=mpls body={"application": "erp", "path": "/erp?request=7d70350964d3446096e298fe3
#  23 t=   2.132s  172.28.20.10 -> 172.28.20.20  len= 100 kind=req   id=35fddb44 route=erp
#  24 t=   2.135s  172.28.20.20 -> 172.28.20.10  len= 317 kind=resp  id=35fddb44 code=200 path=mpls body={"application": "erp", "path": "/erp?request=35fddb44a7a04e9d872608271
#  25 t=   2.158s  172.28.20.10 -> 172.28.20.20  len= 100 kind=req   id=6f57ed8c route=erp
#  26 t=   2.162s  172.28.20.20 -> 172.28.20.10  len= 317 kind=resp  id=6f57ed8c code=200 path=mpls body={"application": "erp", "path": "/erp?request=6f57ed8cb95c477486b3992df
#  27 t=   2.184s  172.28.20.10 -> 172.28.20.20  len= 100 kind=req   id=38797c3a route=erp
#  28 t=   2.188s  172.28.20.20 -> 172.28.20.10  len= 317 kind=resp  id=38797c3a code=200 path=mpls body={"application": "erp", "path": "/erp?request=38797c3a289f47ffb9e95bab5
#  29 t=   2.210s  172.28.20.10 -> 172.28.20.20  len= 100 kind=req   id=a240de7c route=erp
#  30 t=   2.214s  172.28.20.20 -> 172.28.20.10  len= 317 kind=resp  id=a240de7c code=200 path=mpls body={"application": "erp", "path": "/erp?request=a240de7ca3e94d07b1b65e620
#  31 t=   2.237s  172.28.20.10 -> 172.28.20.20  len= 100 kind=req   id=96fb0d5e route=erp
#  32 t=   2.240s  172.28.20.20 -> 172.28.20.10  len= 317 kind=resp  id=96fb0d5e code=200 path=mpls body={"application": "erp", "path": "/erp?request=96fb0d5e2832482b8de24a169
# 20 message(s) dechiffre(s) depuis /captures/02_overlay.pcap
# enregistre dans captures/preuves/C_decrypt.txt
```

**Preuve C.** Fournir deux preuves : (1) la requête HTTP côté LAN (`C_http_lan.txt`), (2) un paquet UDP chiffré côté WAN (`C_udp_hex.txt`). Légender la pile protocolaire et répondre :

- Les routeurs intermédiaires peuvent-ils lire la requête métier ?
- Le chiffrement protège-t-il les adresses IP externes ?

#### Réponse 

### Preuve C : lisibilité de la requête métier et protection des adresses

**Pile protocolaire constatée**

| Segment | Pile | Lisible par un observateur ? |
|---|---|---|
| LAN employé (10.10.0.10 vers 10.10.0.1) | IP privée / TCP 8080 / HTTP en clair | Oui : méthode `GET`, URI `/erp`, `Host`, `User-Agent` (trame 28 de `01_all_traffic.pcap`) |
| WAN simulé (Edge Paris vers Edge Berlin) | IP underlay / UDP 45900 / message chiffré AES-256-GCM | En-têtes IP et UDP oui, contenu métier non |

#### Les routeurs intermédiaires peuvent-ils lire la requête métier ?

**Non, sur le WAN.** Un routeur ou un observateur placé entre les deux Edges ne voit que l'en-tête IP,
l'en-tête UDP et des octets opaques : le marqueur `E5A1` (4 octets), le nonce (12 octets), puis le texte
chiffré et son étiquette d'authentification de 16 octets. La route `erp` et la réponse de l'application
sont à l'intérieur du texte chiffré. L'étiquette GCM empêche en plus toute modification non détectée.

**Oui, sur le LAN.** La session HTTP entre le client et l'Edge Paris est en clair : toute machine qui
capture ce segment lit la requête.

**Réserves.**
- Le chiffrement ne protège que le contenu, pas les métadonnées : un observateur voit qui parle à qui, quand,
  combien d'octets (requête de 100 octets, réponse de 317 octets, sonde de 88 octets) et sur quel transport.
  La taille et le rythme permettent d'inférer le type d'échange (analyse de trafic).
- La clé AES de ce laboratoire est publique (`compose.yaml`). L'outil `decrypt-overlay` déchiffre les 20 messages
  de la capture (10 requêtes `route=erp`, 10 réponses `code=200 path=mpls`) : la confidentialité repose
  entièrement sur le secret de la clé, qui n'existe pas ici.

#### Le chiffrement protège-t-il les adresses IP externes ?

**Non.** L'en-tête IP externe et l'en-tête UDP sont en clair. Sur la trame 1 de `02_overlay.pcap`, on lit
directement la source `172.28.10.10` (`ac 1c 0a 0a`), la destination `172.28.10.20` (`ac 1c 0a 14`),
le protocole 17 (UDP) et les ports 45900 (`b3 4c`). Les routeurs en ont besoin pour acheminer le paquet :
le chiffrement ne commence qu'après l'en-tête UDP, dans le payload.

**Nuance.** Les adresses LAN (10.10.0.10) n'apparaissent jamais sur le WAN, mais ce n'est pas grâce au
chiffrement : l'Edge termine la session HTTP et en crée une nouvelle, donc l'adresse du client n'est pas
reprise dans le paquet WAN. Avec IPsec ESP en mode tunnel, le paquet IP d'origine, adresses internes comprises,
est chiffré, mais l'en-tête IP externe (adresses des passerelles) reste visible, comme ici.

### 7.7 Question d'ingénierie

En production, un tunnel IPsec ESP en mode tunnel protège un paquet IP d'origine (IKEv2 peut négocier les associations de sécurité). Ici, un proxy applicatif crée deux sessions HTTP distinctes et un canal UDP chiffré. Comparer ces deux architectures :

| Critère | IPsec ESP en mode tunnel avec IKEv2 | Overlay du laboratoire |
|---|---|---|
| **Transparence IP** | **Transparent.** Le paquet IP d'origine est encapsulé tel quel dans un nouvel en-tête IP (adresses des passerelles). Tous les protocoles passent (TCP, UDP, ICMP, applications quelconques) et les adresses de bout en bout sont conservées. Les plans d'adressage ne doivent pas se chevaucher, sinon il faut du NAT. | **Non transparent.** L'Edge termine la session HTTP du LAN et crée un nouveau message JSON (`kind`, `id`, `route`) : le paquet d'origine n'est jamais transporté. Seules les routes prévues (`erp`, `teams`, `backup`, `saas`) passent, pas ICMP ni une autre application. Berlin voit l'adresse de l'Edge, jamais celle du client (10.10.0.10). |
| **Ports utilisés** | Pas de port pour ESP : protocole IP **50**. IKEv2 en **UDP 500**, et **UDP 4500** en présence de NAT (NAT-T, ESP encapsulé dans UDP). | Un seul port pour l'overlay : **UDP 45900**, identique sur les deux transports (sondes et données). Autour : TCP 8080 (client vers Edge, LAN), TCP 8000 (Edge Berlin vers ERP), TCP 9000 (manager). Tous en clair, sauf le payload de l'UDP 45900. |
| **Performances** | Traitement dans le noyau, avec accélération matérielle (AES-NI, offload carte réseau) : débit proche de celui du lien. Surcoût de 50 à 70 octets environ par paquet (IP externe, ESP, IV, bourrage, ICV de 16 octets), à compenser par un ajustement du MTU/MSS. Rekeying négocié sans coupure. | Logiciel en espace utilisateur (Python) : adapté à la démonstration, pas au débit réel. Une requête coûte deux sessions TCP plus un datagramme UDP, sans retransmission : une perte donne un `504` après 5 s. Surcoût mesuré de **32 octets** par message (marqueur 4, nonce 12, étiquette GCM 16) : sonde de 88 octets de payload, requête de 100, réponse de 317. Le RTT des sondes applicatives (environ 2 ms dans `sla`) est supérieur à celui d'un `ping` noyau (environ 0,13 ms) : c'est le coût du traitement logiciel (Python, AES-GCM, JSON). |
| **Confidentialité** | **AES-GCM** (typiquement) sur tout le paquet d'origine : en-tête IP interne, ports et données. Visibles : l'en-tête IP externe, le SPI, la taille et le rythme. IKEv2 apporte l'authentification mutuelle (certificats ou clé pré-partagée), la **PFS** (Diffie-Hellman), le **rekeying** périodique et un **anti-rejeu** par numéro de séquence et fenêtre glissante. | **AES-256-GCM** (confidentialité et intégrité) sur le message applicatif seulement. Visibles : IP externe, UDP, marqueur `E5A1`, nonce, tailles et rythme. Faiblesses voulues : **clé unique statique et publique** (`compose.yaml`), nonce tiré au hasard (`os.urandom(12)`, `edge.py` ligne 35) sans compteur ni mémoire des nonces reçus, donc **aucune protection contre le rejeu** : une trame valide capturée peut être renvoyée. Pas de PFS ni de rekeying, aucune identité par pair (le contrôle porte uniquement sur l'adresse IP source). Les deux sessions HTTP restent **en clair** (LAN, et Edge Berlin vers ERP). |
| **Possibilités de capture** | `tcpdump` ou `tshark` sur le lien WAN ne montre que de l'ESP (protocole 50 ou UDP 4500), opaque sans les clés de l'association de sécurité. Pour lire le trafic, capturer sur l'interface interne (avant chiffrement) ou fournir les clés ESP à Wireshark. | `tshark` voit de l'UDP 45900 avec le marqueur `E5A1`. **Déchiffrable avec `decrypt-overlay`**, puisque la clé est publique : 20 messages lus dans `02_overlay.pcap` (10 requêtes `route=erp`, 10 réponses `code=200 path=mpls`). Capturé au niveau de l'Edge, **tout** est lisible : HTTP du LAN, HTTP vers l'ERP et messages déchiffrables. |

**Synthèse.** IPsec protège le **réseau** : tout paquet, quelle que soit l'application, avec une
identité et des clés gérées par IKEv2. Le laboratoire protège un **message applicatif** avec un
secret partagé : il illustre le principe de l'overlay chiffré et du choix de chemin, mais n'offre ni
transparence IP, ni gestion de clés, ni identité des pairs, ni anti-rejeu. C'est pourquoi une
architecture de production utiliserait IPsec/IKEv2 (ou l'équivalent du constructeur) avec PKI,
plutôt que ce mécanisme.

---

## 8. Pause (01:55 - 02:05)

Avant la pause, vérifier que les deux fichiers `01_all_traffic.pcap` et `02_overlay.pcap` sont bien présents dans `captures/` et non vides :

```bash
docker compose exec paris-edge ls -l /captures
docker compose exec paris-edge capinfos /captures/01_all_traffic.pcap
```


<img width="1913" height="997" alt="image" src="https://github.com/user-attachments/assets/5a394450-e33f-4ac0-9ab6-6e5471c12648" />

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


Résultat : 

```json
{
  "role": "paris",
  "generation": "2026-10-meridian-v1",
  "controller_reachable": true,
  "controller_last_seen": 1792651622.4912884,
  "http_listen": [
    "10.10.0.1:8080",
    "10.11.0.1:8080"
  ],
  "paths": {
    "internet": {
      "up": true,
      "rtt_ms": 2.8,
      "loss_pct": 0.0,
      "observations": 12
    },
    "mpls": {
      "up": true,
      "rtt_ms": 2.0,
      "loss_pct": 0.0,
      "observations": 12
    }
  },
  "impairment_training_only": {
    "internet": {
      "loss": 0.0,
      "delay_ms": 0
    },
    "mpls": {
      "loss": 0.0,
      "delay_ms": 0
    }
  }
}{
  "selected_path": "internet",
  "policy_reason": "preferred-and-within-sla",
  "request_id": "01659863f6a1487caa5f4c3100556afb",
  "remote": "{\"application\": \"erp\", \"path\": \"/teams?request=01659863f6a1487caa5f4c3100556afb\", \"server_time\": 1792651625.507, \"message\": \"Reponse du service local au laboratoire.\"}"
}{
  "selected_path": "mpls",
  "policy_reason": "preferred-and-within-sla",
  "request_id": "9f806863fa3b4a5f846802a731fbdff5",
  "remote": "{\"application\": \"erp\", \"path\": \"/erp?request=9f806863fa3b4a5f846802a731fbdff5\", \"server_time\": 1792651625.893, \"message\": \"Reponse du service local au laboratoire.\"}"
}# preuve : D_nominal_sla
# date   : 2026-10-22T06:47:06Z
# noeud  : employee
# cmd    : sla

# heure 06:47:06
== Transports (vue Edge Paris) ==
generation=2026-10-meridian-v1 controller_reachable=true
internet        up=true rtt_ms=2.7      loss_pct=0.0    obs=12
mpls    up=true rtt_ms=1.9      loss_pct=0.0    obs=12
== Chemin choisi par application ==
erp     path=mpls       reason=preferred-and-within-sla error=-
teams   path=internet   reason=preferred-and-within-sla error=-
backup  path=internet   reason=preferred-and-within-sla error=-
# enregistre dans captures/preuves/D_nominal_sla.txt
```

Noter le RTT moyen, la perte observée et le chemin choisi pour la ligne « Nominal » de la matrice (section 9.6).

**Mesures à l'état nominal** (fenêtre complète de 12 échantillons, `generation=2026-10-meridian-v1`, contrôleur joignable)

| Transport | État | RTT moyen | Perte |
|---|---|---|---|
| `internet` | up | 2,8 ms (2,7 ms dans `D_nominal_sla`) | 0,0 % |
| `mpls` | up | 2,0 ms (1,9 ms dans `D_nominal_sla`) | 0,0 % |

**Lignes « Nominal » de la matrice de relevé (section 9.6)**

| Test | Chemin initial | RTT | Perte | Résultat applicatif |
|---|---|---|---|---|
| Nominal / ERP | `mpls` | 2,0 ms | 0 % | 200, `preferred-and-within-sla` |
| Nominal / Teams | `internet` | 2,8 ms | 0 % | 200, `preferred-and-within-sla` |

Le RTT indiqué pour chaque ligne est celui du transport réellement utilisé par l'application.

**Commentaire**

- Chaque application emprunte son transport préféré par la politique : ERP sur `mpls`, Teams sur `internet`. La raison `preferred-and-within-sla` signifie que le transport préféré respecte les seuils (RTT et perte) : aucun secours n'est sollicité.
- Les deux transports sont très en dessous des seuils de la politique (100 ms et 20 % pour l'ERP et Teams). La marge est donc très large : il faudra une dégradation importante pour provoquer un basculement.
- L'écart entre les deux relevés (2,8 contre 2,7 ms pour `internet`, 2,0 contre 1,9 ms pour `mpls`) vient de la fenêtre glissante : la moyenne évolue d'un échantillon à l'autre, donc une mesure isolée n'a pas de valeur absolue. C'est pourquoi la baseline s'appuie sur 12 échantillons.
- Ces RTT (environ 2 ms) sont mesurés par les sondes applicatives de l'Edge. Ils sont plus élevés que ceux d'un `ping` (environ 0,13 ms), car les sondes traversent Python, le chiffrement AES-GCM et le traitement JSON.
- Le champ `remote` de `/teams` indique `"application": "erp"` : dans ce laboratoire, un seul serveur répond à toutes les routes (`/erp`, `/teams`, `/backup`). Seul le chemin demandé les distingue, ce qui est une limite de la simulation à mentionner.

**Conclusion.** L'état de référence est sain : deux underlays disponibles sans perte, un contrôleur joignable, chaque application sur son chemin préféré. Cette baseline sert de point de comparaison pour le brownout (Teams doit quitter `internet` si son RTT dépasse 100 ms) et pour le blackout (l'ERP doit quitter `mpls` s'il devient indisponible)

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

<img width="1391" height="417" alt="image" src="https://github.com/user-attachments/assets/6c86e90b-55a4-4b63-9440-c5632c399d71" />


Le RTT du transport dégradé doit augmenter : comparez-le au seuil de la politique Teams. Identifier le nouveau transport choisi et la justification `policy_reason`.

<img width="1911" height="352" alt="image" src="https://github.com/user-attachments/assets/8ac8a371-667d-4f0a-8e90-a75e29019c1c" />

### Justification de `policy_reason` : `alternate-within-sla`

**Règle appliquée par l'Edge pour Teams** (politique : transport préféré `internet`, `max_rtt_ms` = 100, `max_loss_pct` = 20) :

1. Si le transport préféré est « up » **et** respecte le RTT et la perte maximums : il est choisi (`preferred-and-within-sla`).
2. Sinon, si un autre transport est « up » **et** respecte les seuils : il est choisi (`alternate-within-sla`).
3. Sinon, un transport encore « up » est utilisé malgré tout (`degraded-no-path-meets-sla`).
4. Sinon : erreur `503 no-underlay-available`.

**Application au brownout**

| Critère | `internet` (préféré) | `mpls` (autre transport) |
|---|---|---|
| Transport « up » (sonde reçue dans les 3,5 dernières secondes) | oui | oui |
| RTT inférieur ou égal à 100 ms | **non** (environ 220 ms) | oui (environ 2 ms) |
| Perte inférieure ou égale à 20 % | oui (0 %) | oui (0 %) |
| Respect du SLA | **non** | **oui** |

- L'étape 1 échoue : `internet` est joignable, mais son RTT dépasse le seuil de 100 ms. La règle « préféré et conforme » ne s'applique donc plus.
- L'étape 2 réussit : `mpls` est « up » et conforme. L'Edge le choisit, d'où `selected_path: mpls`.
- La raison est `alternate-within-sla` : le chemin retenu est **un secours** (pas le préféré), mais il **respecte le SLA**.

**Pourquoi pas les autres raisons ?**

- `preferred-and-within-sla` : exclu, car le transport préféré n'est plus conforme.
- `degraded-no-path-meets-sla` : exclu, car au moins un transport (`mpls`) respecte le SLA. Cette raison n'apparaîtrait que si aucun des deux ne le respectait.
- `503 no-underlay-available` : exclu, car les deux transports répondent aux sondes.

**Conclusion.** La politique n'a pas changé (même génération `2026-10-meridian-v1`). C'est la **mesure** de la latence qui a modifié la décision : le critère de latence a été violé, et le moteur a basculé vers l'autre transport conforme. Le brownout est détecté parce que les mesures sont des moyennes de RTT, pas seulement un test de disponibilité : un transport peut répondre et pourtant ne plus convenir à l'application.

Note : la latence configurée est un délai d'émission unidirectionnel appliqué par l'Edge Paris. Le RTT dépend du comportement réel des requêtes et sondes.

**Mesurer le temps de réaction.** Lancer l'injection 5 secondes après le début du relevé, puis lire le moment où le chemin change :

```bash
docker compose exec -d employee sh -c 'sleep 5; curl -s http://10.10.0.1:8080/lab/impair?path=internet\&loss=0\&delay_ms=220 > /dev/null'
docker compose exec employee proof D_brownout_watch watchpath teams 30
```

Temps de réaction approximatif = heure du premier changement de chemin moins heure de l'injection (début du relevé plus 5 secondes).

<img width="1911" height="966" alt="image" src="https://github.com/user-attachments/assets/cd964e8b-392b-4f02-bc5c-f7e0c7f957bc" />

### 9.3 Mission 6 : provoquer un blackout (10 min)

**Étape 1, retour à un état nominal mesuré.** Réinitialiser la latence puis **attendre 15 secondes** : la fenêtre de 12 échantillons doit se vider des mesures à 220 ms.

```bash
docker compose exec employee curl -s 'http://10.10.0.1:8080/lab/impair?path=internet&loss=0&delay_ms=0'
sleep 15
docker compose exec employee sla
```

<img width="1917" height="986" alt="image" src="https://github.com/user-attachments/assets/04c3b7f8-5466-495b-81b9-59de37fced8d" />


Vérifier que `internet` affiche un RTT très faible. Si vous enchaînez le blackout sans cette attente, l'Edge verra encore un RTT Internet moyen élevé et affichera `degraded-no-path-meets-sla` au lieu de `alternate-within-sla` : un résultat à expliquer, pas une erreur.

<img width="1887" height="977" alt="image" src="https://github.com/user-attachments/assets/31957151-eabb-40ac-9c6d-0885941dbf72" />

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

<img width="1917" height="992" alt="image" src="https://github.com/user-attachments/assets/c3907cec-b9b6-445e-a97d-2de0612597ce" />

<img width="1856" height="946" alt="image" src="https://github.com/user-attachments/assets/faf5ba1b-df46-443a-8413-8c0ae54e0c76" />

**Étape 3, mesurer la réaction.** Rétablir d'abord le lien, attendre 15 secondes, puis rejouer le blackout avec relevé :

```bash
docker compose exec employee curl -s 'http://10.10.0.1:8080/lab/impair?path=mpls&loss=0&delay_ms=0'
sleep 15
docker compose exec -d employee sh -c 'sleep 5; curl -s http://10.10.0.1:8080/lab/impair?path=mpls\&loss=100\&delay_ms=0 > /dev/null'
docker compose exec employee proof D_blackout_watch watchpath erp 20
```

Exemple de relevé (extrait) :

```text
# preuve : D_blackout_watch
# date   : 2026-10-22T07:01:56Z
# noeud  : employee
# cmd    : watchpath erp 20

heure     app   chemin   raison | internet[...] mpls[...]
07:01:56  erp  mpls preferred-and-within-sla | internet[up=true rtt=222.8 loss=0.0] mpls[up=true rtt=1.7 loss=0.0]
07:01:57  erp  mpls preferred-and-within-sla | internet[up=true rtt=222.8 loss=0.0] mpls[up=true rtt=1.7 loss=0.0]
07:01:58  erp  mpls preferred-and-within-sla | internet[up=true rtt=222.8 loss=0.0] mpls[up=true rtt=1.8 loss=0.0]
07:01:59  erp  mpls preferred-and-within-sla | internet[up=true rtt=222.8 loss=0.0] mpls[up=true rtt=1.7 loss=0.0]
07:02:00  erp  mpls preferred-and-within-sla | internet[up=true rtt=222.7 loss=0.0] mpls[up=true rtt=1.7 loss=0.0]
07:02:06  erp  mpls overlay-timeout | internet[up=true rtt=222.6 loss=0.0] mpls[up=false rtt=1.6 loss=25.0]
07:02:07  erp  internet degraded-no-path-meets-sla | internet[up=true rtt=222.6 loss=0.0] mpls[up=false rtt=1.6 loss=33.3]
07:02:09  erp  internet degraded-no-path-meets-sla | internet[up=true rtt=222.6 loss=0.0] mpls[up=false rtt=1.5 loss=41.7]
07:02:10  erp  internet degraded-no-path-meets-sla | internet[up=true rtt=222.6 loss=0.0] mpls[up=false rtt=1.5 loss=58.3]
07:02:11  erp  internet degraded-no-path-meets-sla | internet[up=true rtt=222.7 loss=0.0] mpls[up=false rtt=1.4 loss=66.7]
07:02:13  erp  internet degraded-no-path-meets-sla | internet[up=true rtt=222.7 loss=0.0] mpls[up=false rtt=1.3 loss=75.0]
07:02:14  erp  internet degraded-no-path-meets-sla | internet[up=true rtt=222.7 loss=0.0] mpls[up=false rtt=1.2 loss=83.3]
07:02:15  erp  internet degraded-no-path-meets-sla | internet[up=true rtt=222.7 loss=0.0] mpls[up=false rtt=null loss=100.0]
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

<img width="1933" height="665" alt="image" src="https://github.com/user-attachments/assets/24f883c8-29be-4a3d-b662-5c40a48978e7" />


**Restaurer :**

```bash
docker compose exec employee curl -s 'http://10.10.0.1:8080/lab/impair?path=mpls&loss=0&delay_ms=0'
sleep 15
docker compose exec employee proof D_return_sla sla
```
<img width="1917" height="962" alt="image" src="https://github.com/user-attachments/assets/c7c605f1-6258-4700-b755-da814e112d1b" />

### 9.4 Preuve D

**Preuve D.** Les fichiers `D_nominal_sla`, `D_brownout_sla`, `D_blackout_sla`, `D_return_sla`, `D_brownout_watch`, `D_blackout_watch`, et un tableau avant / après :

```txt
=================== D_nominal_sla
# preuve : D_nominal_sla
# date   : 2026-10-22T06:47:06Z
# noeud  : employee
# cmd    : sla

# heure 06:47:06
== Transports (vue Edge Paris) ==
generation=2026-10-meridian-v1 controller_reachable=true
internet        up=true rtt_ms=2.7      loss_pct=0.0    obs=12
mpls    up=true rtt_ms=1.9      loss_pct=0.0    obs=12
== Chemin choisi par application ==
erp     path=mpls       reason=preferred-and-within-sla error=-
teams   path=internet   reason=preferred-and-within-sla error=-
backup  path=internet   reason=preferred-and-within-sla error=-
=================== D_brownout_sla
# preuve : D_brownout_sla
# date   : 2026-10-22T06:59:19Z
# noeud  : employee
# cmd    : sla

# heure 06:59:19
== Transports (vue Edge Paris) ==
generation=2026-10-meridian-v1 controller_reachable=true
internet        up=true rtt_ms=222.9    loss_pct=0.0    obs=12
mpls    up=true rtt_ms=1.9      loss_pct=0.0    obs=12
== Chemin choisi par application ==
erp     path=mpls       reason=preferred-and-within-sla error=-
teams   path=mpls       reason=alternate-within-sla     error=-
backup  path=internet   reason=preferred-and-within-sla error=-
=================== D_brownout_watch
# preuve : D_brownout_watch
# date   : 2026-10-22T06:55:44Z
# noeud  : employee
# cmd    : watchpath teams 30

heure     app   chemin   raison | internet[...] mpls[...]
06:55:44  teams  mpls alternate-within-sla | internet[up=true rtt=222.8 loss=0.0] mpls[up=true rtt=1.8 loss=0.0]
06:55:45  teams  mpls alternate-within-sla | internet[up=true rtt=222.8 loss=0.0] mpls[up=true rtt=1.8 loss=0.0]
06:55:46  teams  mpls alternate-within-sla | internet[up=true rtt=222.8 loss=0.0] mpls[up=true rtt=1.8 loss=0.0]
06:55:47  teams  mpls alternate-within-sla | internet[up=true rtt=222.8 loss=0.0] mpls[up=true rtt=1.8 loss=0.0]
06:55:48  teams  mpls alternate-within-sla | internet[up=true rtt=222.8 loss=0.0] mpls[up=true rtt=1.8 loss=0.0]
06:55:49  teams  mpls alternate-within-sla | internet[up=true rtt=222.8 loss=0.0] mpls[up=true rtt=1.8 loss=0.0]
06:55:50  teams  mpls alternate-within-sla | internet[up=true rtt=222.7 loss=0.0] mpls[up=true rtt=1.8 loss=0.0]
06:55:51  teams  mpls alternate-within-sla | internet[up=true rtt=222.7 loss=0.0] mpls[up=true rtt=1.8 loss=0.0]
06:55:53  teams  mpls alternate-within-sla | internet[up=true rtt=222.7 loss=0.0] mpls[up=true rtt=1.8 loss=0.0]
06:55:54  teams  mpls alternate-within-sla | internet[up=true rtt=222.7 loss=0.0] mpls[up=true rtt=1.8 loss=0.0]
06:55:55  teams  mpls alternate-within-sla | internet[up=true rtt=222.7 loss=0.0] mpls[up=true rtt=1.8 loss=0.0]
06:55:56  teams  mpls alternate-within-sla | internet[up=true rtt=222.7 loss=0.0] mpls[up=true rtt=1.8 loss=0.0]
06:55:57  teams  mpls alternate-within-sla | internet[up=true rtt=222.7 loss=0.0] mpls[up=true rtt=1.8 loss=0.0]
06:55:58  teams  mpls alternate-within-sla | internet[up=true rtt=222.7 loss=0.0] mpls[up=true rtt=1.8 loss=0.0]
06:55:59  teams  mpls alternate-within-sla | internet[up=true rtt=222.7 loss=0.0] mpls[up=true rtt=1.8 loss=0.0]
06:56:00  teams  mpls alternate-within-sla | internet[up=true rtt=222.7 loss=0.0] mpls[up=true rtt=1.8 loss=0.0]
06:56:01  teams  mpls alternate-within-sla | internet[up=true rtt=222.8 loss=0.0] mpls[up=true rtt=1.9 loss=0.0]
06:56:02  teams  mpls alternate-within-sla | internet[up=true rtt=222.8 loss=0.0] mpls[up=true rtt=1.9 loss=0.0]
06:56:03  teams  mpls alternate-within-sla | internet[up=true rtt=222.8 loss=0.0] mpls[up=true rtt=1.9 loss=0.0]
06:56:04  teams  mpls alternate-within-sla | internet[up=true rtt=222.9 loss=0.0] mpls[up=true rtt=1.8 loss=0.0]
06:56:05  teams  mpls alternate-within-sla | internet[up=true rtt=222.9 loss=0.0] mpls[up=true rtt=1.8 loss=0.0]
06:56:06  teams  mpls alternate-within-sla | internet[up=true rtt=222.8 loss=0.0] mpls[up=true rtt=1.8 loss=0.0]
06:56:07  teams  mpls alternate-within-sla | internet[up=true rtt=222.9 loss=0.0] mpls[up=true rtt=1.8 loss=0.0]
06:56:09  teams  mpls alternate-within-sla | internet[up=true rtt=222.9 loss=0.0] mpls[up=true rtt=1.8 loss=0.0]
06:56:10  teams  mpls alternate-within-sla | internet[up=true rtt=223.0 loss=0.0] mpls[up=true rtt=1.8 loss=0.0]
06:56:11  teams  mpls alternate-within-sla | internet[up=true rtt=223.2 loss=0.0] mpls[up=true rtt=1.8 loss=0.0]
06:56:12  teams  mpls alternate-within-sla | internet[up=true rtt=223.1 loss=0.0] mpls[up=true rtt=1.8 loss=0.0]
06:56:13  teams  mpls alternate-within-sla | internet[up=true rtt=223.0 loss=0.0] mpls[up=true rtt=1.7 loss=0.0]
=================== D_blackout_sla
# preuve : D_blackout_sla
# date   : 2026-10-22T07:00:16Z
# noeud  : employee
# cmd    : sla

# heure 07:00:16
== Transports (vue Edge Paris) ==
generation=2026-10-meridian-v1 controller_reachable=true
internet        up=true rtt_ms=222.7    loss_pct=0.0    obs=12
mpls    up=false        rtt_ms=1.8      loss_pct=25.0   obs=12
== Chemin choisi par application ==
erp     path=internet   reason=degraded-no-path-meets-sla       error=-
teams   path=internet   reason=degraded-no-path-meets-sla       error=-
backup  path=internet   reason=preferred-and-within-sla error=-
=================== D_blackout_status
# preuve : D_blackout_status
# date   : 2026-10-22T07:00:17Z
# noeud  : employee
# cmd    : curl -s http://10.10.0.1:8080/status

{
  "role": "paris",
  "generation": "2026-10-meridian-v1",
  "controller_reachable": true,
  "controller_last_seen": 1792652415.6402893,
  "http_listen": [
    "10.10.0.1:8080",
    "10.11.0.1:8080"
  ],
  "paths": {
    "internet": {
      "up": true,
      "rtt_ms": 222.7,
      "loss_pct": 0.0,
      "observations": 12
    },
    "mpls": {
      "up": false,
      "rtt_ms": 1.8,
      "loss_pct": 33.3,
      "observations": 12
    }
  },
  "impairment_training_only": {
    "internet": {
      "loss": 0.0,
      "delay_ms": 220
    },
    "mpls": {
      "loss": 100.0,
      "delay_ms": 0
    }
  }
}=================== D_blackout_erp
# preuve : D_blackout_erp
# date   : 2026-10-22T07:00:17Z
# noeud  : employee
# cmd    : curl -s http://10.10.0.1:8080/erp

{
  "selected_path": "internet",
  "policy_reason": "degraded-no-path-meets-sla",
  "request_id": "14aae0485d49406fbe06a2ae64e60cd9",
  "remote": "{\"application\": \"erp\", \"path\": \"/erp?request=14aae0485d49406fbe06a2ae64e60cd9\", \"server_time\": 1792652417.808, \"message\": \"Reponse du service local au laboratoire.\"}"
}=================== D_blackout_watch
# preuve : D_blackout_watch
# date   : 2026-10-22T07:01:56Z
# noeud  : employee
# cmd    : watchpath erp 20

heure     app   chemin   raison | internet[...] mpls[...]
07:01:56  erp  mpls preferred-and-within-sla | internet[up=true rtt=222.8 loss=0.0] mpls[up=true rtt=1.7 loss=0.0]
07:01:57  erp  mpls preferred-and-within-sla | internet[up=true rtt=222.8 loss=0.0] mpls[up=true rtt=1.7 loss=0.0]
07:01:58  erp  mpls preferred-and-within-sla | internet[up=true rtt=222.8 loss=0.0] mpls[up=true rtt=1.8 loss=0.0]
07:01:59  erp  mpls preferred-and-within-sla | internet[up=true rtt=222.8 loss=0.0] mpls[up=true rtt=1.7 loss=0.0]
07:02:00  erp  mpls preferred-and-within-sla | internet[up=true rtt=222.7 loss=0.0] mpls[up=true rtt=1.7 loss=0.0]
07:02:06  erp  mpls overlay-timeout | internet[up=true rtt=222.6 loss=0.0] mpls[up=false rtt=1.6 loss=25.0]
07:02:07  erp  internet degraded-no-path-meets-sla | internet[up=true rtt=222.6 loss=0.0] mpls[up=false rtt=1.6 loss=33.3]
07:02:09  erp  internet degraded-no-path-meets-sla | internet[up=true rtt=222.6 loss=0.0] mpls[up=false rtt=1.5 loss=41.7]
07:02:10  erp  internet degraded-no-path-meets-sla | internet[up=true rtt=222.6 loss=0.0] mpls[up=false rtt=1.5 loss=58.3]
07:02:11  erp  internet degraded-no-path-meets-sla | internet[up=true rtt=222.7 loss=0.0] mpls[up=false rtt=1.4 loss=66.7]
07:02:13  erp  internet degraded-no-path-meets-sla | internet[up=true rtt=222.7 loss=0.0] mpls[up=false rtt=1.3 loss=75.0]
07:02:14  erp  internet degraded-no-path-meets-sla | internet[up=true rtt=222.7 loss=0.0] mpls[up=false rtt=1.2 loss=83.3]
07:02:15  erp  internet degraded-no-path-meets-sla | internet[up=true rtt=222.7 loss=0.0] mpls[up=false rtt=null loss=100.0]
=================== D_return_sla
# preuve : D_return_sla
# date   : 2026-10-22T07:04:45Z
# noeud  : employee
# cmd    : sla

# heure 07:04:45
== Transports (vue Edge Paris) ==
generation=2026-10-meridian-v1 controller_reachable=true
internet        up=true rtt_ms=222.6    loss_pct=0.0    obs=12
mpls    up=true rtt_ms=1.7      loss_pct=0.0    obs=12
== Chemin choisi par application ==
erp     path=mpls       reason=preferred-and-within-sla error=-
teams   path=mpls       reason=alternate-within-sla     error=-
backup  path=internet   reason=preferred-and-within-sla error=-
```
### Preuve D : tableau avant / après

| Événement | Application | RTT (ms) | Perte (%) | Chemin choisi | `policy_reason` | Temps de réaction approximatif |
|---|---|---|---|---|---|---|
| Avant brownout | Teams | `internet` 2,7 | 0 | `internet` | `preferred-and-within-sla` | sans objet |
| Après brownout Internet | Teams | `internet` 222,9 (`mpls` 1,9) | 0 | `mpls` | `alternate-within-sla` | non mesuré (relevé commencé après l'injection) |
| Avant blackout | ERP | `mpls` 1,7 | 0 | `mpls` | `preferred-and-within-sla` | sans objet |
| Après blackout MPLS | ERP | `mpls` 1,2 à 1,8 (trompeur), puis `null` ; `internet` 222,6 | `mpls` 25 puis 100 | `internet` | `degraded-no-path-meets-sla` | environ 6 s (injection vers 07:02:01, premier ERP réacheminé à 07:02:07) |

**Précisions sur le tableau**

- Les lignes « avant brownout » et « avant blackout » viennent de `D_nominal_sla` (06:47:06) et des premières lignes de `D_blackout_watch` (07:01:56).
- Blackout : Internet était déjà à 222 ms (délai du brownout non retiré), d'où `degraded-no-path-meets-sla`
  au lieu de `alternate-within-sla`. L'ERP reste joignable parce que l'Edge utilise le dernier transport « up ».
- Le temps de réaction du blackout inclut la requête émise pendant la fenêtre de détection :
  à 07:02:06 l'ERP répond `overlay-timeout` après 5 s d'attente, car `mpls` était encore considéré « up » ;
  la requête suivante, à 07:02:07, passe par `internet`.

Justifier pourquoi un brownout et un blackout ne doivent pas être diagnostiqués de la même manière.

### Brownout contre blackout

| Critère | Brownout (Internet à 220 ms) | Blackout (MPLS à 100 % de perte) |
|---|---|---|
| Nature de la panne | Dégradation de **qualité** : le lien répond, mais trop lentement | Perte de **disponibilité** : plus aucune réponse |
| Indicateur révélateur | Le **RTT moyen** : 222,9 ms, au-dessus du seuil de 100 ms | La **perte** (25 %, 33 %, 42 %... jusqu'à 100 %) et l'état `up=false` |
| État du lien | `up=true`, perte 0 % | `up=false` après environ 3,5 s sans réponse |
| Détection | Progressive : la moyenne d'une fenêtre de 12 mesures doit franchir le seuil | Rapide : l'absence de réponse aux sondes suffit |
| Symptôme utilisateur | Lenteur, sans erreur | Erreurs ou timeout : une requête `overlay-timeout` après 5 s, puis bascule |
| Décision de la politique | Teams passe sur le transport conforme (`alternate-within-sla`) | L'ERP quitte `mpls` ; sans transport conforme, repli sur le dernier « up » (`degraded-no-path-meets-sla`) |
| Pistes de diagnostic | Congestion, file d'attente, QoS, changement de route, distance | Coupure physique ou opérateur, filtrage, équipement arrêté |

**Un piège visible dans vos relevés.** Pendant le blackout, le RTT de `mpls` affiche 1,6 puis 1,2 ms,
et `null` à 100 % de perte. La moyenne ne porte que sur les sondes qui ont reçu une réponse : un lien mort
semble donc excellent. **Le RTT seul ne prouve jamais la santé d'un lien** : il faut le lire avec la
perte et l'état `up`.

**Conséquence.** Traiter un brownout comme une panne (ou l'inverse) fait fausse route. Un brownout exige
d'abord de mesurer latence et gigue, puis de les comparer au SLA de chaque application, et de déplacer
seulement les flux sensibles. Un blackout se confirme par la perte et les timeouts, puis se traite par
un basculement binaire et une escalade vers l'opérateur. Les seuils et les temporisations diffèrent :
un seuil de latence demande de la tolérance, une détection de perte doit être rapide, et dans les deux cas
un retour trop rapide au transport d'origine provoquerait du flapping.

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

<img width="1900" height="892" alt="image" src="https://github.com/user-attachments/assets/64556ee2-6b48-4591-bafb-8e60845347ab" />

- Attendre environ 15 secondes entre injection et lecture de la télémétrie.
- **Ne jamais appliquer `netem` sur l'interface du réseau de contrôle.**
- L'absence du module noyau `sch_netem` n'est pas éliminatoire : documenter l'erreur et rester sur l'émulation applicative intégrée.
- Penser à supprimer la règle (dernière commande) avant de continuer.

### 9.6 Matrice de relevé obligatoire

| Test | Chemin initial | RTT | Perte | Résultat applicatif |
|---|---|---|---|---|
| Nominal / ERP | `mpls` | `mpls` 1,9 ms (`internet` 2,7 ms) | 0 % | 200, chemin `mpls`, `preferred-and-within-sla` |
| Nominal / Teams | `internet` | `internet` 2,7 ms (`mpls` 1,9 ms) | 0 % | 200, chemin `internet`, `preferred-and-within-sla` |
| Brownout Internet (Teams) | `internet` | `internet` 222,9 ms (`mpls` 1,9 ms) | 0 % | Bascule sur `mpls`, `alternate-within-sla` ; ERP inchangé sur `mpls` |
| Blackout MPLS (ERP) | `mpls` | `mpls` 1,8 ms puis `null` (moyenne sur les seules réponses reçues) ; `internet` 222,6 ms | `mpls` 25 % puis 100 % ; `internet` 0 % | Une requête en `overlay-timeout`, puis chemin `internet`, `degraded-no-path-meets-sla` (200) |
| Retour nominal | à relever après avoir retiré le délai Internet | | | |

**Notes**

- Les lignes « Nominal » viennent de `D_nominal_sla` (06:47:06).
- Brownout : source `D_brownout_sla` (06:59:19). Le RTT d'`internet` passe de 2,7 à 222,9 ms, au-dessus du seuil de 100 ms de Teams. La perte reste à 0 %, donc seul le critère de latence est violé.
- Blackout : sources `D_blackout_sla` (07:00:16) et `D_blackout_watch`. Le RTT de `mpls` reste bas (1,2 à 1,8 ms) alors que le lien est mort : la moyenne ne porte que sur les sondes qui ont reçu une réponse. Il faut lire le RTT avec la perte et l'état `up`.
- Le blackout s'est déroulé avec Internet déjà à environ 222 ms. Aucun transport ne respectait donc le SLA de l'ERP, d'où `degraded-no-path-meets-sla` au lieu de `alternate-within-sla`. L'ERP est resté joignable, car l'Edge utilise alors le dernier transport « up ».

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

<img width="1721" height="977" alt="image" src="https://github.com/user-attachments/assets/b0df3232-62a3-485a-8d7a-d3d2d0e8bfde" />


Attendre au moins 8 secondes (l'Edge interroge le manager toutes les 3 secondes avec un délai de 1,5 seconde), puis relancer :

```bash
sleep 8
docker compose exec employee proof E_stopped_status curl -s http://10.10.0.1:8080/status
docker compose exec employee proof E_stopped_erp curl -s http://10.10.0.1:8080/erp
```

Observer `controller_reachable` (passé à `false`) et `generation` (inchangée). Décrire ce qui continue de fonctionner et les fonctions de gestion désormais impossibles.

<img width="1781" height="990" alt="image" src="https://github.com/user-attachments/assets/4b5bc8c9-e179-41c7-8028-c0ed6c305395" />


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

<img width="1917" height="987" alt="image" src="https://github.com/user-attachments/assets/ccab2dba-9a5c-40c7-b7e8-65b2012a4e77" />
### Observation côté paquets : lien de contrôle (TCP 9000) pendant l'arrêt du manager

**Commande :** capture sur l'interface `control` de `paris-edge` (filtre `tcp port 9000`), arrêt puis redémarrage du
conteneur `controller`, lecture avec `tshark` (fichier `07_control.pcap`, 14 paquets).

**Lecture des drapeaux TCP** (`tcp.flags.str`) : `S` = SYN, `A` = ACK, `P` = PSH (données), `R` = RST, `F` = FIN.

| Trames | Temps relatif | Sens | Drapeaux | Interprétation |
|---|---|---|---|---|
| 1 | 0,000 s | Paris (.11) vers manager (.10) | `S` | Tentative de connexion de l'Edge au manager |
| 2 | 0,000 s | Manager vers Paris | `A` + `R` | **Connexion refusée** (RST) en 0,12 ms : l'adresse `172.28.30.10` répond, mais aucun processus n'écoute encore sur le port 9000 |
| 3 à 5 | 3,002 s | Paris vers manager, puis retour | `S`, `S`+`A`, `A` | **Poignée de main TCP réussie**, 3 secondes après la précédente : c'est la période d'interrogation de l'Edge |
| 6 à 11 | 3,002 à 3,011 s | Requête puis réponse | `AP` et `A` | Requête HTTP `GET /policy`, puis réponse du manager (la politique JSON), en environ 8 ms |
| 12 à 14 | 3,011 s | Les deux sens | `F` et `A` | Fermeture propre de la connexion (HTTP/1.0 : une session par interrogation) |

**Ce que la capture démontre**

- Un cycle d'interrogation réussi tient en **12 trames** (poignée de main, requête, réponse, fermeture) et dure environ 10 ms. Le plan de contrôle est du **TCP/HTTP en clair**, sans authentification : n'importe qui sur ce réseau peut lire la politique.
- La trame 2 est un **refus actif** (RST) et non un silence : l'hôte est joignable, l'application est absente. C'est le signe typique d'un service en cours de redémarrage (conteneur démarré, processus Python pas encore à l'écoute).
- La tentative suivante, 3 secondes plus tard, réussit. L'Edge **se resynchronise seul**, sans intervention : le plan de contrôle se rétablit automatiquement.

**Ce que la capture ne montre pas, et pourquoi**

- **Pas de paquets pendant l'arrêt.** Avec le manager arrêté, les tentatives de l'Edge ne laissent aucune trace TCP. L'explication la plus probable : l'adresse du manager n'existe plus sur le réseau, donc l'Edge reste bloqué sur la résolution ARP et le paquet SYN ne part jamais sur le fil. Les échecs se manifesteraient par des requêtes ARP sans réponse, que le filtre `tcp port 9000` exclut. Ce point est une hypothèse à vérifier (voir ci-dessous).
- **Aucune interrogation avant l'arrêt n'apparaît**, alors que l'Edge interroge toutes les 3 secondes et que le manager répondait pendant les 8 premières secondes de la manipulation. Les temps affichés sont relatifs au premier paquet capturé, donc impossible de les placer sur la chronologie réelle sans les heures absolues.

**Conséquence pour la mission 7.** La panne du manager coupe seulement le plan de **gestion** : plus d'interrogation réussie,
`controller_reachable` passe à `false`, la `generation` reste figée. Le plan de **données** continue (l'Edge conserve la dernière politique valide en mémoire et les requêtes `/erp` aboutissent), ce que les preuves `E_stopped_status` et `E_stopped_erp` doivent confirmer.

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

<img width="1727" height="957" alt="image" src="https://github.com/user-attachments/assets/2b6dd9f4-6317-4ef2-a152-bcd0296d033e" />


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

<img width="1881" height="337" alt="image" src="https://github.com/user-attachments/assets/e951664e-2694-424f-bc2a-6a517052f1ae" />


Ou avec un éditeur (`nano policy/policy.json`, `vim policy/policy.json`) : le dossier `policy/` étant monté, un éditeur qui remplace le fichier est pris en compte.

**3. Valider le JSON puis attendre la propagation :**

```bash
docker compose exec controller python -m json.tool /lab/policy/policy.json
sleep 5
docker compose exec employee proof E_policy_after curl -s http://10.10.0.1:8080/status
docker compose exec employee proof E_policy_after_erp curl -s http://10.10.0.1:8080/erp
```

Comparer la politique et le chemin choisi. Si le JSON est invalide, le manager répond une erreur et l'Edge **conserve la dernière politique valide** : c'est un comportement à observer dans `controller_reachable` et `generation`.

<img width="1837" height="942" alt="image" src="https://github.com/user-attachments/assets/e6fe97a6-d687-45c5-a816-743d63e627f4" />


**4. Revenir à la préférence initiale `mpls` avant la fin du TP :**

```bash
cp policy/policy.original.json policy/policy.json
```

<img width="1797" height="302" alt="image" src="https://github.com/user-attachments/assets/5a70624c-4ae9-4d42-9b7e-9ed014e4608b" />


```bash
sleep 5
docker compose exec employee sla
```

<img width="1769" height="575" alt="image" src="https://github.com/user-attachments/assets/d6cf57b2-19d4-4dba-bcf5-4f26bafbc350" />


### 10.3 Preuve E

**Preuve E.** Les fichiers `E_before_status`, `E_stopped_status`, `E_stopped_erp`, `E_policy_before`, `E_policy_after`, `E_policy_after_erp`. Montrer :

- la génération de politique avant / après ;
- `controller_reachable` pendant l'arrêt ;
- la persistance d'une requête ERP pendant l'arrêt.

Expliquer la différence entre configuration centrale et transfert de données distribué.

### Configuration centrale et transfert de données distribué

| Critère | Configuration centrale (plan de contrôle et de gestion) | Transfert de données distribué (plan de données) |
|---|---|---|
| Rôle | Décider : définir les règles (préférences et seuils SLA par application, applications interdites aux invités) | Exécuter : acheminer réellement le trafic, mesurer les chemins et choisir le transport pour chaque requête |
| Où cela s'exécute | Un seul point : le manager (`controller`, TCP 9000, fichier `policy/policy.json`) | Dans chaque Edge, indépendamment : Paris et Berlin échangent directement en UDP 45900 |
| Flux observé | Interrogation périodique de la politique par l'Edge (environ toutes les 3 s, TCP 9000, 12 trames par cycle) | Requêtes et réponses chiffrées entre Edges sur `mpls` ou `internet`, sondes SLA permanentes |
| Fréquence | Faible volume, changements rares | Volume élevé, en continu |
| En cas de panne | On perd la capacité de **changer** la politique et de superviser de façon centralisée | Le trafic continue : l'Edge applique le dernier état connu |
| Preuve dans le TP | `controller_reachable` passe à `false`, `generation` reste figée (`2026-10-meridian-v1`) | La requête `/erp` aboutit pendant l'arrêt du manager (`E_stopped_erp`) |

**Ce que montre le laboratoire**

- Pendant l'arrêt du contrôleur, `controller_reachable` vaut `false` mais la génération de politique ne change pas : l'Edge **met la politique en cache** et continue de s'en servir. Il n'y a aucun appel au manager dans le chemin d'une requête utilisateur : les données ne transitent jamais par le contrôleur.
- Le manager ne fait que **distribuer** une décision. Le choix du chemin pour chaque requête est pris localement par l'Edge, à partir de la politique en cache et de ses propres sondes RTT et perte (fonction `choose()` de `edge.py`).
- Une modification de politique (mission 8) se propage seulement au prochain cycle d'interrogation, donc avec un délai de quelques secondes. C'est la preuve que la configuration est centralisée mais appliquée de façon distribuée.

**Avantages de la séparation**

- **Résilience** : une panne du manager n'interrompt pas la production. Le plan de contrôle n'est pas un point de défaillance unique pour le trafic.
- **Évolutivité** : le trafic ne passe pas par un nœud central, donc pas de goulot d'étranglement.
- **Cohérence d'administration** : une seule source de vérité pour les règles de tous les sites, qu'il suffit de modifier une fois.

**Limites à connaître**

- Une panne **prolongée** du manager fige la politique : plus de changement possible, plus de supervision centralisée, plus de réaction à un nouvel incident de sécurité ni d'intégration d'un nouvel Edge.
- Dans un vrai SD-WAN, le plan de contrôle gère aussi les **clés et les certificats** des tunnels. Une perte prolongée peut donc entraîner l'expiration des associations de sécurité et, à terme, **la coupure du plan de données**. Ce n'est pas le cas ici, puisque la clé AES est statique, ce qui est justement une des faiblesses du kit.
- La politique voyage ici en HTTP clair, sans authentification : le plan de contrôle est le plus sensible, et il est le moins protégé dans ce laboratoire.

**Conclusion.** La configuration centrale **décide et distribue** : un point, faible volume, mise à jour différée. Le transfert distribué **exécute** : chaque Edge, volume élevé, indépendant du manager tant qu'il détient une politique valide. C'est cette séparation, observée avec `controller_reachable=false` et un `/erp` qui répond, qui fait la robustesse d'une architecture SD-WAN.

### 10.4 ZTP, authentification et haute disponibilité

### ZTP, authentification et haute disponibilité

**Point de départ.** Dans le kit, l'Edge connaît l'adresse du manager (`172.28.30.10:9000`, écrite en dur dans `edge.py`),
n'a aucune identité et n'enregistre rien. Les étapes ci-dessous décrivent donc une architecture de production.
Les ports et noms de protocoles varient selon le constructeur : à adapter à celui étudié dans le cours.

**Schéma (vue d'ensemble)**

    Nouvel Edge --(1) DHCP/DNS--> Internet ou MPLS (accès initial)
         |
         +--(2) HTTPS--> Service de redirection du constructeur (cloud)
         |                   |  renvoie l'adresse des contrôleurs de l'entreprise
         +--(3) TLS/DTLS--> Orchestrateur / validateur (cluster)
         |                   |  contrôle du certificat et du numéro de série
         +--(4) TLS/DTLS--> Contrôleurs de gestion et de politique (cluster)
         |                   |  configuration, politique, clés
         +--(5) IPsec/IKEv2 ou équivalent --> Autres Edges et hubs (tunnels)

#### Les six étapes

| N° | Étape | Qui parle à qui, avec quelle identité, sur quel port |
|---|---|---|
| 1 | Mise sous tension | L'Edge démarre avec une configuration d'usine minimale. Il n'a pas d'adresse et ne parle encore à personne. Son identité est un **numéro de série** et un **certificat constructeur** (TPM ou module sécurisé) inscrit dans l'équipement. Aucune intervention sur site, au-delà du câblage. |
| 2 | Accès initial | L'Edge obtient une adresse IP, une passerelle, un DNS et l'heure : **DHCP** (UDP 67/68) sur l'interface WAN, **DNS** (UDP/TCP 53), **NTP** (UDP 123). L'heure est indispensable : sans elle, la validation des certificats échoue. Pas d'identité d'entreprise à ce stade : l'Edge est identifié par le seul numéro de série. |
| 3 | Découverte du manager | L'Edge contacte le **service de redirection du constructeur** (cloud, **HTTPS TCP 443**), qui présente un certificat serveur. L'Edge se présente avec son certificat constructeur ; le service sait à quelle entreprise appartient ce numéro de série et lui renvoie l'**adresse du ou des contrôleurs**. Alternatives : option DHCP, nom DNS convenu, ou fichier de configuration sur clé USB. |
| 4 | Identité et certificat | L'Edge ouvre une connexion **TLS ou DTLS** vers l'orchestrateur (port propre à chaque constructeur). Les deux côtés s'authentifient **mutuellement** par certificat. L'orchestrateur vérifie que le numéro de série figure dans la liste des équipements autorisés (liste blanche), puis l'Edge reçoit un **certificat d'entreprise** émis par la **PKI** de l'organisation, par exemple via **SCEP ou EST** (HTTPS). C'est l'identité qui sert ensuite à tout. |
| 5 | Récupération de politique | Avec son certificat d'entreprise, l'Edge établit la **connexion de contrôle permanente** avec les contrôleurs (TLS/DTLS). Il reçoit sa **configuration** (adresses, VPN de segmentation), la **politique** (préférences et seuils SLA par application, règles invité), la liste des autres Edges, des hubs et des transports à utiliser, ainsi que les **clés ou paramètres** de chiffrement des tunnels. C'est l'équivalent, en production et sécurisé, de l'interrogation de `/policy` en TCP 9000 du kit. |
| 6 | Création du tunnel | L'Edge établit les tunnels **IPsec** (IKEv2 : **UDP 500** et **UDP 4500** si NAT, ESP protocole 50) ou l'équivalent du constructeur, **vers les hubs et les autres Edges**, sur chaque transport. Les sondes SLA (BFD ou équivalent) démarrent et l'Edge rejoint l'overlay : le site est opérationnel. Identité : le certificat d'entreprise, ou les clés distribuées par les contrôleurs. |

**Mise en correspondance avec le laboratoire**

| Étape de production | Équivalent dans le kit |
|---|---|
| 1 à 4 (identité, autorisation, certificat) | **Absentes** : n'importe quel conteneur dans `172.28.30.0/24` peut lire la politique, aucun certificat |
| 5 (politique) | Présente, mais sans authentification : `GET /policy` en TCP 9000, HTTP clair |
| 6 (tunnel) | Remplacé par le canal UDP 45900 chiffré avec une clé statique partagée, sans négociation |

#### Stratégie de haute disponibilité des contrôleurs

1. **Plusieurs instances.** Au moins **2, idéalement 3 ou plus**, de chaque composant (orchestrateur, gestion, politique), en mode actif-actif ou en cluster avec **quorum** (nombre impair) pour éviter un cerveau partagé (« split-brain »).
2. **Domaines de panne séparés.** Instances réparties sur **deux data centers au minimum**, ou sur plusieurs zones de disponibilité, avec des alimentations, des liens et des hyperviseurs distincts. Une panne d'un site ne doit pas supprimer le quorum.
3. **Plusieurs adresses connues de l'Edge.** Chaque Edge reçoit une **liste ordonnée de contrôleurs** (ou un nom DNS à plusieurs adresses, ou une adresse anycast) et bascule seul vers le suivant, avec une temporisation pour éviter le flapping.
4. **Réplication des données.** Base de configuration et de politiques répliquée en continu, **sauvegardes** chiffrées et testées régulièrement, restauration documentée et répétée.
5. **PKI redondante.** L'autorité de certification, les listes de révocation (CRL) et le service OCSP doivent être hautement disponibles, sinon l'authentification des Edges échoue. Surveiller aussi les dates d'expiration.
6. **Chemins de gestion diversifiés.** Les contrôleurs sont joints par **au moins deux transports indépendants** depuis chaque site (comme l'overlay du TP : Internet et MPLS), et le réseau de contrôle est séparé du réseau de données (comme `172.28.30.0/24` ici).
7. **Mises à jour progressives** (une instance à la fois) et fenêtres de maintenance, pour ne jamais perdre le quorum volontairement.
8. **Supervision et tests.** Alarmes sur l'état de la réplication, la latence entre instances et la santé des certificats, plus des **exercices de bascule** réguliers (arrêter une instance, un site entier).

**Un Edge doit pouvoir fonctionner sans contrôleur.** La HA des contrôleurs réduit le risque, mais n'enlève pas le besoin d'un plan de données autonome : c'est ce que montre la mission 7.

#### Effet d'une perte prolongée des associations de sécurité en production

Une association de sécurité (SA) est l'ensemble des clés et paramètres d'un tunnel IPsec, valable pour une durée de vie limitée (secondes de volume ou d'heures). Si les contrôleurs, la PKI ou le pair deviennent injoignables **pendant plus longtemps que cette durée** (et que le délai de tolérance du constructeur), voici ce qui se passe :

| Phase | Effet |
|---|---|
| Au début de la panne | Les tunnels existants **continuent** : les SA déjà installées fonctionnent tant qu'elles sont valides. Le plan de données reste en place, la dernière politique est conservée (comme avec `controller_reachable=false` dans le TP). |
| Pas de renégociation possible | Les clés ne peuvent pas être renouvelées (rekeying) ou les certificats ne peuvent plus être validés (CRL, OCSP, ou CA injoignable). Plus de nouveaux Edges, plus de changement de politique, plus de révocation d'un équipement compromis. |
| À l'expiration des SA | Les tunnels **tombent**, site par site, puis l'overlay s'effondre. Le trafic inter-sites s'arrête, ou bascule sur un secours non chiffré ou sans politique si la configuration le permet (risque de sécurité). Le breakout local vers Internet peut continuer, mais sans l'inspection centrale. |
| Au rétablissement | Tous les Edges **se reconnectent en même temps** : pic de charge sur les contrôleurs et la PKI, renégociation de masse, nouvelle convergence du routage de l'overlay. Prévoir des **temporisations aléatoires** pour étaler les reconnexions. |

**Mesures** : durée de vie des SA et délai de tolérance dimensionnés pour **dépasser la durée de réparation prévue** (en heures, pas en minutes), HA des contrôleurs (voir plus haut), alarmes bien avant l'expiration (état de la connexion de contrôle, âge des clés, validité des certificats), et procédure d'urgence pour réinstaller des clés ou des certificats par un chemin de secours.

**Dans le laboratoire** : la clé AES est statique et sans durée de vie, donc la panne du contrôleur n'a aucun effet sur le plan de données, même au bout d'une heure. Ce comportement est plus tolérant qu'en production, mais **au prix de la sécurité** : aucune rotation de clé, aucune révocation possible.


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

Résultat : 

```txt
HTTP/1.0 200 OK
Server: BaseHTTP/0.6 Python/3.12.15
Date: Thu, 22 Oct 2026 07:24:29 GMT
Content-Type: application/json; charset=utf-8
Content-Length: 322

{
  "selected_path": "mpls",
  "policy_reason": "preferred-and-within-sla",
  "request_id": "0b3b2bf06f4d4732ba7102d2dc508696",
  "remote": "{\"application\": \"erp\", \"path\": \"/erp?request=0b3b2bf06f4d4732ba7102d2dc508696\", \"server_time\": 1792653869.31, \"message\": \"Reponse du service local au laboratoire.\"}"
}HTTP/1.0 403 Forbidden
Server: BaseHTTP/0.6 Python/3.12.15
Date: Thu, 22 Oct 2026 07:24:29 GMT
Content-Type: application/json; charset=utf-8
Content-Length: 61

{
  "error": "guest-segment-policy",
  "application": "erp"
}HTTP/1.0 200 OK
Server: BaseHTTP/0.6 Python/3.12.15
Date: Thu, 22 Oct 2026 07:24:30 GMT
Content-Type: application/json; charset=utf-8
Content-Length: 76

{
  "guest": "internet-only-demo",
  "note": "application policy, not VRF"

```

**Preuves réseau.** Capturer le LAN invité et lire la source et la décision :

```bash
docker compose exec -d paris-edge sh -c 'timeout 15 tcpdump -i $(ifmap guest_lan) -nn -s 0 -U -Z root -w /captures/04_guest_lan.pcap'
sleep 2
docker compose exec guest curl -s http://10.11.0.1:8080/erp
docker compose exec guest curl -s http://10.11.0.1:8080/guest
sleep 15
docker compose exec paris-edge tshark -r /captures/04_guest_lan.pcap -Y http -T fields -e frame.number -e ip.src -e ip.dst -e http.request.uri -e http.response.code
```

<img width="1917" height="922" alt="image" src="https://github.com/user-attachments/assets/3ceba31c-7f51-47c6-bd01-3b242c1a3c80" />


**Contrôles complémentaires de segmentation :**

```bash
docker compose exec guest curl -s -o /dev/null -w '%{http_code}\n' http://10.11.0.1:8080/status
docker compose exec berlin-edge curl -s -m 3 -o /dev/null -w '%{http_code}\n' http://172.28.10.10:8080/status
```

<img width="1920" height="502" alt="image" src="https://github.com/user-attachments/assets/07d04711-4dee-4646-990e-06229dc718e6" />


- La première commande montre que les routes d'administration sont refusées à l'invité (403).
- La seconde montre que le proxy HTTP de l'Edge Paris n'est pas joignable depuis l'underlay (code `000`, connexion refusée).

**Question.** Quelles mesures faudrait-il ajouter pour garantir une isolation réseau de bout en bout (VLAN/VRF, ACL, firewall stateful, identité) ?

### Mission 9 : mesures pour une isolation de bout en bout

**Constat dans le kit.** L'isolation de l'invité repose sur trois éléments seulement :

- un sous-réseau Docker distinct (`10.11.0.0/24`) ;
- une écoute du proxy sur une adresse dédiée (`10.11.0.1:8080`) ;
- une règle applicative dans `edge.py` : un client invité reçoit `403` pour `erp`, `teams` et `backup` (liste `guest_blocked`), ainsi que pour `/status` et `/lab/impair`.

Cette règle s'applique uniquement aux requêtes HTTP qui atteignent le proxy. Ce n'est ni un VRF, ni une isolation L3 complète : l'invité partage le même Edge, le même processus, la même clé AES et le même overlay que les employés. Un défaut dans le proxy, ou un trafic qui ne passe pas par lui, contournerait la règle.

#### Mesures à ajouter, par couche

| Couche | Mesure | Ce qu'elle garantit | Équivalent ou manque dans le kit |
|---|---|---|---|
| L2, accès | **VLAN dédiés** (un par population : employés, invités, serveurs, gestion), ports d'accès configurés en VLAN fixe, trunks restreints aux VLAN utiles, isolation des clients sur le SSID invité (client isolation) | Les invités ne partagent pas de domaine de diffusion avec les employés, pas de ARP ni de découverte entre eux | Remplacé par deux réseaux Docker distincts, sans mécanisme de VLAN |
| L3, routage | **VRF** (un par segment) sur les Edges et le cœur | Tables de routage séparées : aucune route entre l'invité et le métier, même en cas d'erreur de configuration d'une ACL. Les adresses peuvent même se chevaucher | **Absent.** Un seul processus Python dessert les deux LAN |
| Overlay SD-WAN | **Segmentation de bout en bout dans l'overlay** : un identifiant de VPN/segment par VRF, transporté dans les tunnels, avec des clés ou des associations de sécurité distinctes par segment | Le trafic invité ne peut pas être injecté dans un tunnel métier ni lu avec la clé du métier | **Absent.** Une clé AES unique et publique pour tous les flux |
| Filtrage | **ACL** sur les interfaces et les passerelles : refus par défaut entre segments, ouverture explicite des seuls flux utiles (DNS, accès Internet pour l'invité) | Réduit la surface d'attaque et rend la politique lisible et auditable | Équivalent limité : la liste `guest_blocked`, appliquée au niveau HTTP seulement |
| Filtrage à état | **Pare-feu stateful** (idéalement NGFW) entre segments et à la sortie Internet : suivi de session, inspection applicative, filtrage d'URL et IPS | Autorise uniquement les réponses aux connexions initiées de l'intérieur, bloque les scans et les latéralisations, inspecte le contenu | **Absent.** Aucun filtrage de paquets, aucun suivi de session |
| Identité | **Authentification des utilisateurs et des équipements** : 802.1X avec RADIUS, contrôle d'admission réseau (NAC), affectation dynamique de VLAN selon l'identité, **portail captif** pour les invités avec durée limitée | Le segment dépend de **qui** se connecte et non de l'adresse IP ou du port physique. Une machine inconnue est mise en quarantaine | **Absente.** L'Edge décide « invité » d'après l'adresse d'écoute ou une adresse IP source (10.11.0.x), donc falsifiable |
| Accès aux ressources | **Moindre privilège et Zero Trust** : accès par application, vérification continue de l'identité, de l'état du poste et du contexte (SSE, ZTNA) | Même un utilisateur du segment employé n'accède qu'à ce dont il a besoin | Absente |
| Sortie Internet de l'invité | **Breakout local direct** pour l'invité, sans jamais traverser l'overlay vers les data centers, avec filtrage DNS et web | Un invité n'a aucun chemin vers le réseau d'entreprise, même par erreur de routage | Le test SaaS illustre le principe sans le filtrage |
| Gestion | **Plan de gestion séparé** (VRF et VLAN de gestion, accès par bastion, MFA, comptes nominatifs), **authentification et chiffrement du plan de contrôle** (TLS mutuel) | Un invité ne peut ni lire la politique ni la modifier | Réseau de contrôle séparé, mais HTTP clair sans authentification ; `/lab/impair` sans authentification (refusé seulement à l'invité) |
| Supervision | **Journalisation vers un SIEM** : refus de segmentation, tentatives inter-segments, changements de politique, authentifications échouées. **Tests d'isolation réguliers** (scans depuis le segment invité) | Détecte une dérive et prouve l'isolation | Journaux locaux du proxy uniquement |

#### Pourquoi plusieurs couches

Chaque mesure compense les défauts des autres (défense en profondeur) :

- un VLAN seul ne filtre rien dès que deux VLAN sont routés ensemble ;
- une ACL seule est difficile à maintenir et sans suivi de session ;
- un VRF isole le routage mais ne contrôle pas ce qui passe à l'intérieur d'un même segment ;
- l'identité règle le problème d'attribution du segment, que ni VLAN ni ACL ne résolvent.

Le principe directeur est le **refus par défaut** : tout est interdit entre segments, sauf ce qui est ouvert explicitement et journalisé.

#### Résumé : ce qui manque dans le laboratoire

1. Isolation **L2 et L3** : VLAN et VRF réels (le kit utilise seulement des réseaux Docker).
2. Isolation **dans l'overlay** : un identifiant de segment et des clés distinctes par segment.
3. **Filtrage** : ACL de refus par défaut et pare-feu à état entre segments.
4. **Identité** : authentification des clients (802.1X, NAC) au lieu de se fier à l'adresse IP.
5. **Contrôle d'accès à la gestion** : authentification du manager et de `/lab/impair`.
6. **Observabilité** : journalisation centralisée et tests d'isolation périodiques.

### 11.2 Mission 10 : Local Internet breakout (8 min)

Le service SaaS de démonstration est raccordé au sous-réseau « Internet » virtuel. L'Edge Paris accède localement au SaaS et répond au client, sans passer par Berlin :

```bash
docker compose exec employee curl -s http://10.10.0.1:8080/saas
docker compose exec paris-edge curl -s http://172.28.10.40:8000/office
```
<img width="1910" height="657" alt="image" src="https://github.com/user-attachments/assets/a3394ad9-5849-4819-adeb-47676c13d8d9" />

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

<img width="1892" height="967" alt="image" src="https://github.com/user-attachments/assets/c9c98dbc-458b-49da-8e0f-f46815559bac" />


Constater l'absence de datagrammes UDP/45900 vers Berlin pour cette requête. Indiquer pourquoi ce test illustre seulement le principe de breakout local : il ne vérifie pas un NGFW, un service SSE/SASE, l'inspection TLS ni un accès Internet public.

#### Chemin IP réel du proxy vers le SaaS

| Observation | Valeur relevée | Interprétation |
|---|---|---|
| `ip route get 172.28.10.40` | `dev eth3 src 172.28.10.10`, sans `via` | Destination **directement connectée** : sortie par `eth3` (réseau `internet`), adresse source 172.28.10.10, aucune passerelle |
| `traceroute -n -m 3` | 1 seul saut : 172.28.10.40, 0,114 ms | Le SaaS est le premier saut : aucun routeur intermédiaire, et surtout **aucun passage par Berlin** |
| Réponse à `/saas` | `"breakout": "local-at-paris-edge"` et réponse du service `saas` (`/office`) | L'Edge Paris répond lui-même au client, avec une réponse venue du SaaS |

Chemin réel : `employee (10.10.0.10) → Edge Paris (10.10.0.1, eth0) → eth3 (172.28.10.10) → SaaS (172.28.10.40:8000)`.

#### Lecture de la capture `05_saas_breakout.pcap` (12 trames)

| Trames | Sens | Contenu |
|---|---|---|
| 1 à 3 | Edge (172.28.10.10) vers SaaS, port 8000, et retour | Poignée de main TCP |
| 4 | Edge vers SaaS | `GET /office` en HTTP clair |
| 5 à 8 | SaaS vers Edge (port client 36492) | Acquittement, puis réponse HTTP (trames 6 et 8 ; `/office` associé à la réponse en trame 8) |
| 9 à 12 | Les deux sens | Fermeture de la connexion (une session par requête) |

- Le client (10.10.0.10) n'apparaît **jamais** côté `internet` : l'Edge crée sa propre session HTTP vers le SaaS, depuis son adresse 172.28.10.10. Le SaaS ne voit que l'Edge.
- Le trafic circule en **HTTP clair sur TCP 8000**, avec une seule session TCP pour l'ensemble de l'échange.

#### Absence d'UDP/45900 vers Berlin : preuve à corriger

Votre capture ne peut **pas** démontrer cette absence : le filtre `host 172.28.10.40` ne laisse passer que les paquets à destination ou en provenance du SaaS. Un datagramme UDP vers Berlin (172.28.10.20) est exclu **par construction**, qu'il existe ou non.

Une preuve valable doit capturer largement et regarder les **messages déchiffrés** : les sondes SLA circulent en permanence sur UDP/45900, donc compter les paquets ne suffit pas (il y en aura toujours). Il faut vérifier qu'aucun message applicatif (`kind=req`) ne part pour cette requête.

    docker compose exec -d paris-edge sh -c 'timeout 15 tcpdump -i any -nn -s 0 -U -Z root -w /captures/05b_saas_overlay.pcap udp port 45900 or host 172.28.10.40'
    sleep 2
    docker compose exec employee curl -s http://10.10.0.1:8080/saas
    sleep 15
    docker compose exec paris-edge decrypt-overlay /captures/05b_saas_overlay.pcap --kind req,resp

Résultat attendu : **0 message dechiffre** (seules des sondes `probe` et `pong` circulent). En comparaison, la même manipulation avec `/erp` fait apparaître une paire `req` et `resp`.

#### Pourquoi ce test illustre seulement le principe du breakout local

| Ce qui manque | Pourquoi le test ne le vérifie pas |
|---|---|
| **NGFW** (pare-feu nouvelle génération) | Aucun filtrage applicatif, IPS, antivirus ou contrôle d'URL entre l'Edge et le SaaS : la requête passe sans inspection |
| **SSE/SASE** | Pas de point de présence cloud, de passerelle web sécurisée (SWG), de CASB ni de ZTNA : l'Edge ne fait que relayer |
| **Inspection TLS** | L'échange est en HTTP clair sur le port 8000 : il n'y a ni TLS, ni certificat, ni déchiffrement et réchiffrement à valider |
| **Accès Internet public** | Le SaaS est un conteneur dans un réseau Docker `internal` (172.28.10.0/24, adresses privées), sans route vers Internet : pas de NAT, pas d'adresse publique, pas de DNS, pas de latence ni de variabilité réelles |
| **Politique par utilisateur ou application** | Tous les clients du LAN sortent de la même façon : pas d'identité, pas de règle par application ni par segment |
| **Redondance de la sortie** | Un seul chemin (`internet`) : pas de bascule de la sortie SaaS vers un autre transport en cas de panne |
| **Journalisation et conformité** | Aucun journal d'accès, aucune protection contre la fuite de données (DLP) |

**Conclusion.** Le test prouve un seul fait : **l'Edge Paris peut sortir localement vers une destination SaaS sans repasser par Berlin ni par l'overlay**, ce qui réduit la latence et la charge du WAN. Il ne dit rien de la **sécurité** de cette sortie ni de son comportement sur l'Internet réel. En production, ce breakout local doit s'accompagner d'un NGFW ou d'un service SSE/SASE, d'une inspection TLS adaptée à la politique de l'entreprise, de la sélection du meilleur chemin par application et d'une journalisation centralisée.

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


#### 1. AES-GCM pédagogique et IPsec ESP avec IKEv2

| Critère | AES-GCM pédagogique (kit) | IPsec ESP avec IKEv2 (production) |
|---|---|---|
| **Gestion des clés** | **Une clé unique AES-256, statique**, définie dans `compose.yaml` (`DEMO_KEY_HEX`) et partagée par les deux Edges. Aucune négociation, aucun échange de clés. La clé est lisible par quiconque accède au fichier ou à l'environnement du conteneur. | Clés de session **dérivées dynamiquement** par IKEv2 (échange Diffie-Hellman), propres à chaque association de sécurité (SA) et à chaque direction. Aucune clé de chiffrement n'est stockée en clair dans une configuration. |
| **Rekeying** | **Aucun.** La clé ne change jamais : la compromission d'un seul jour de trafic capturé expose tout le passé et tout le futur. | **Renouvellement périodique** des SA, par durée (heures) ou par volume (octets), sans coupure (CHILD_SA créée avant l'ancienne supprimée). Avec la **PFS** (DH à chaque rekey), la compromission d'une clé n'expose pas les sessions précédentes. |
| **Identité** | **Aucune identité par pair.** Détenir la clé suffit. L'Edge Berlin accepte un paquet s'il se déchiffre et si l'IP source correspond à celle attendue (`172.28.x.x` du transport). Cette adresse est falsifiable. | **Authentification mutuelle** dans IKEv2 : certificats X.509 (PKI) ou clé pré-partagée. Chaque passerelle prouve son identité, les certificats sont révocables (CRL, OCSP) et ont une date d'expiration. |
| **Replay (rejeu)** | **Aucune protection.** Le nonce est tiré au hasard (`os.urandom(12)`, `edge.py` ligne 35) sans compteur et sans mémoire des nonces déjà reçus. Une trame valide capturée peut être renvoyée. L'AAD `MERIDIAN-LAB` est une constante, elle n'attache rien à la session. | **Numéro de séquence** dans chaque paquet ESP (32 bits, ou 64 bits avec ESN) et **fenêtre anti-rejeu** glissante côté récepteur : un paquet déjà vu ou trop ancien est rejeté. |
| **Contrôle d'accès** | Pas de politique de flux. Les seules règles sont applicatives (liste `guest_blocked`, routes `erp`, `teams`, `backup`, `saas`) et portent sur le proxy HTTP. Aucun filtrage de ce qui entre dans le tunnel. | **SPD et sélecteurs de trafic** : seuls les flux dont les adresses, protocoles et ports correspondent aux sélecteurs sont chiffrés et acceptés dans le tunnel. S'y ajoutent le pare-feu, la segmentation et l'identité par certificat. |
| **Algorithmes** | Un seul : AES-256-GCM, figé dans le code. | Suites négociées (AES-GCM, ChaCha20-Poly1305, groupes DH), avec désactivation des algorithmes faibles et agilité cryptographique. |
| **Anti-DoS à l'établissement** | Aucun mécanisme : n'importe quel émetteur peut inonder le port UDP 45900, chaque trame invalide coûte un déchiffrement. | Cookies IKEv2, limites de négociations simultanées, authentification avant toute allocation de ressources. |

**Conclusion.** Le chiffrement du kit (AES-256-GCM) est solide en soi. Tout ce qui l'entoure (gestion de clé, identité, rejeu, négociation, cycle de vie) est absent, et c'est ce que fournit IKEv2.

#### 2. Trois défauts de sécurité volontaires, et leur correction

Les cinq questions de lecture de code ont chacune une réponse, résumée ici avant le détail :

| Question de lecture | Réponse |
|---|---|
| Où la clé est-elle définie, qui peut la lire ? | `compose.yaml`, variable `DEMO_KEY_HEX`. Lisible par tout détenteur du fichier, par `docker inspect`, ou par `env` dans les conteneurs `paris-edge` et `berlin-edge`. |
| Le canal Edge/manager est-il chiffré, authentifié ? | **Non** : HTTP clair sur TCP 9000, sans authentification. L'adresse du manager est écrite en dur (`172.28.30.10`). |
| Que se passe-t-il si une trame valide est rejouée ? | Aucun contrôle : une requête rejouée est exécutée à nouveau (à vérifier avec le test de rejeu). |
| Qui peut appeler `/lab/impair` depuis le LAN employés ? | **Tout client du LAN**, sans identifiant. L'invité reçoit un 403, mais seulement parce que le segment est identifié par l'adresse. |
| Comment l'Edge décide-t-il qu'un client est « invité » ? | D'après l'adresse sur laquelle il écoute (`10.11.0.1`) ou l'adresse source dans `10.11.0.0/24` : une appartenance réseau, pas une identité. |

**Défaut 1 : clé de chiffrement statique, partagée et publique**

| | |
|---|---|
| Preuve | `compose.yaml` (`x-demo-key`), `env` dans `paris-edge` et `berlin-edge`. L'outil `decrypt-overlay` déchiffre les 20 messages de `02_overlay.pcap` avec cette clé (preuve `C_decrypt`). |
| Risque | Un tiers qui capture le trafic ou lit la configuration déchiffre tout, forge des messages valides et se fait passer pour un Edge. Aucune révocation possible sans redéploiement. |
| Correction en entreprise | **IPsec/IKEv2 avec PKI** : certificats par équipement, clés de session éphémères (PFS) et rekeying automatique. Les secrets résiduels sont stockés dans un **gestionnaire de secrets** (HSM, coffre-fort), jamais dans un fichier de configuration. Processus de **révocation** (CRL/OCSP) et rotation planifiée. |

**Défaut 2 : plan de contrôle en HTTP clair, sans authentification**

| | |
|---|---|
| Preuve | `edge.py` interroge `http://172.28.30.10:9000/policy` (adresse figée dans le code). Les 12 trames par cycle sont visibles en clair (capture `07_control.pcap`) et le manager répond à tout client qui le demande. |
| Risque | N'importe quelle machine du réseau de contrôle lit la politique, ou usurpe le manager pour imposer une politique (par exemple faire passer tous les flux par un transport dégradé). Aucune intégrité : une réponse modifiée en route est acceptée. |
| Correction en entreprise | **TLS mutuel** (mTLS) avec certificats d'entreprise entre Edge et contrôleurs, **politique signée** (le contenu est authentifié même si le canal est compromis), liste d'adresses de contrôleurs vérifiée par l'identité du certificat et non par l'adresse IP, réseau de gestion isolé (VRF), journalisation des accès. |

**Défaut 3 : aucune protection contre le rejeu**

| | |
|---|---|
| Preuve | `grep -n 'seq\|replay\|counter\|nonce' /lab/edge.py` ne renvoie que les lignes 35 et 36 : nonce aléatoire et chiffrement. Aucun compteur ni liste de nonces reçus. |
| Risque | Un attaquant qui capture une trame `req` valide peut la renvoyer autant de fois qu'il veut : l'Edge Berlin la déchiffre et exécute à nouveau la requête vers l'ERP. Sur des opérations non idempotentes, cela provoque des doublons ou un déni de service. |
| Correction en entreprise | **Numéro de séquence** par SA avec **fenêtre anti-rejeu** (ESP d'IPsec), horodatage ou nonce de session lié à la connexion, rekeying fréquent. À l'étage applicatif : identifiants de requête uniques, idempotence et limitation de débit. |

Deux défauts supplémentaires, utiles pour la discussion :

- **`/lab/impair` sans authentification.** Tout client du LAN employés peut dégrader ou couper un transport avec une simple requête GET. Correction : retirer cette route en production, ou la protéger par authentification forte (MFA), autorisation par rôle, journalisation de chaque action et séparation du plan d'administration.
- **Segmentation fondée sur l'adresse et non sur l'identité.** L'Edge qualifie un client d'« invité » d'après l'adresse d'écoute ou l'adresse source dans `10.11.0.0/24`. Une machine qui change d'adresse ou d'interface change de segment. Correction : **802.1X et NAC** avec affectation dynamique de VLAN, VRF dédiés, pare-feu à état, identité utilisateur et poste (voir la section 11.1).

À noter : le client et l'ERP échangent en **HTTP clair** sur les deux LAN, ce qui est normal pour un laboratoire, mais inacceptable en production (TLS de bout en bout).

**Vérifications à lancer :**

```bash
docker compose exec paris-edge sh -c 'env | grep DEMO_KEY'
docker compose exec paris-edge tshark -r /captures/01_all_traffic.pcap -Y 'tcp.port==9000 && http.request' -T fields -e ip.src -e ip.dst -e http.request.uri
docker compose exec employee curl -s 'http://10.10.0.1:8080/lab/impair?path=internet&loss=0&delay_ms=0'
docker compose exec guest curl -s -o /dev/null -w '%{http_code}\n' 'http://10.11.0.1:8080/lab/impair?path=internet&loss=0&delay_ms=0'
docker compose exec paris-edge grep -n -A3 'def is_guest' /lab/edge.py
```

Résultats attendus : la clé est affichée en clair ; les requêtes `GET /policy` en TCP 9000 sont lisibles ; l'employé obtient une réponse JSON sans identifiant ; l'invité obtient `403`.

#### 3. Événements à journaliser dans un SIEM

| Famille | Événement | Source | Champs à conserver | Alerte |
|---|---|---|---|---|
| **Changement de politique** | Nouvelle génération de politique appliquée | Contrôleur et Edges | Ancienne et nouvelle `generation`, auteur, heure, différences (diff) | Tout changement hors fenêtre de maintenance, ou par un compte non autorisé |
| | Échec de lecture ou de validation d'une politique (JSON invalide) | Contrôleur | Fichier, erreur, version conservée par l'Edge | Toute occurrence |
| **Plan de contrôle** | Contrôleur injoignable (`controller_reachable=false`), retour de connexion | Edges | Edge, durée de la coupure, nombre de tentatives | Coupure supérieure à N minutes ; plusieurs Edges simultanément |
| **État des tunnels** | Tunnel up ou down, échec de négociation | Edges et hubs | Pair, transport, cause, durée de vie de la SA, rekeying réussi ou échoué | Perte d'un tunnel, échecs répétés de rekeying, expiration proche des SA |
| **Authentification ZTP** | Tentative d'enregistrement d'un équipement, certificat émis, refus | Orchestrateur, PKI | Numéro de série, résultat, adresse source, certificat | Numéro de série inconnu, échecs répétés, enregistrement hors horaire |
| | Expiration ou révocation d'un certificat | PKI | Identité, échéance | Expiration à moins de 30 jours |
| **Passages de chemin** | Changement de transport pour une application | Edges | Application, ancien et nouveau chemin, `policy_reason`, RTT et perte à l'instant | Bascules fréquentes (flapping), repli en `degraded-no-path-meets-sla`, absence de transport |
| | Dépassement de SLA, RTT ou perte | Edges | Transport, valeur, seuil, fenêtre de mesure | Dépassement soutenu |
| **Segmentation** | Requête refusée à un invité (403) | Edges, pare-feu | Source, destination, application, règle appliquée | Pics de refus, un même invité qui sonde plusieurs applications |
| | Trafic inter-segments bloqué par ACL ou pare-feu | Pare-feu | Source, destination, port, règle | Tout accès au segment gestion depuis un segment utilisateur |
| **Administration** | Appel d'une fonction d'administration (`/lab/impair` ou son équivalent), connexion d'un administrateur | Edges, bastion | Compte, adresse, action, paramètres | Toute action d'administration par un compte non nominatif ou hors procédure |
| **Intégrité du chiffrement** | Trame refusée à l'authentification (étiquette GCM invalide), rejeu détecté | Edges | Source, transport, nombre | Taux anormal : signe de sondage ou d'attaque |

**Format conseillé.** Un événement par ligne en JSON, avec heure NTP, nom de l'équipement, identifiant de corrélation et niveau de gravité, par exemple :

```json
{"ts":"2026-10-22T07:02:06Z","host":"paris-edge","event":"path_change","app":"erp","from":"mpls","to":"internet","reason":"degraded-no-path-meets-sla","mpls_loss_pct":25.0,"severity":"warning"}
```

**Règles de corrélation utiles** : bascule de chemin suivie d'un échec applicatif (impact utilisateur), coupure du contrôleur et changement de politique peu après (usurpation possible), refus de segmentation répétés suivis d'une authentification réussie (compromission).

#### 4. Place de SD-WAN, NGFW, SSE, SASE et Zero Trust dans une architecture cible

| Brique | Nature | Rôle | Où elle se situe |
|---|---|---|---|
| **SD-WAN** | Technologie de **réseau** | Connectivité entre sites : overlay chiffré, choix du chemin selon le SLA par application, ZTP, politique centralisée | **Edges** dans chaque site, hubs dans les data centers, contrôleurs redondés. C'est la brique que le kit simule. |
| **NGFW** | Équipement ou service de **sécurité** | Filtrage à état, contrôle applicatif (couche 7), IPS, filtrage d'URL, inspection TLS | **En local** (site, data center, périmètre) ou virtuel. Souvent intégré à l'Edge, ou placé en cœur de data center. |
| **SSE** (Security Service Edge) | Ensemble de services de sécurité **dans le cloud** | Passerelle web sécurisée (SWG), CASB, accès réseau Zero Trust (ZTNA), pare-feu en service (FWaaS), DLP | **Points de présence cloud** du fournisseur, atteints par les sites et les utilisateurs nomades, entre l'utilisateur et Internet ou le SaaS |
| **SASE** | **Architecture** de convergence | SD-WAN **plus** SSE livrés comme un service cloud unifié, avec politique et identité communes | Vue d'ensemble : les Edges SD-WAN envoient le trafic Internet et SaaS vers le SSE, le trafic interne reste sur l'overlay |
| **Zero Trust** | **Principe** de sécurité, pas un produit | Ne jamais faire confiance par défaut, vérifier explicitement chaque accès (identité, poste, contexte), moindre privilège, supposer la compromission | **Transversal** : appliqué par l'identité (IdP, MFA), la microsegmentation, le ZTNA, le NGFW et le SD-WAN lui-même (certificats, segments) |

```text
 Utilisateurs / sites                 Overlay SD-WAN                 Applications

 Site Paris   --[Edge SD-WAN + NGFW local]--+
 Site Londres --[Edge SD-WAN + NGFW local]--+--> Hub / Data center --> Applications internes
 Site Berlin  --[Edge SD-WAN + NGFW local]--+    (NGFW, segmentation,
 Nomades -------------------------------------+    ZTNA)
                |
                +--(sortie Internet et SaaS)--> Service SSE (cloud) --> Internet, SaaS
                                                (SWG, CASB, ZTNA, FWaaS, DLP)

 Contrôleurs SD-WAN et PKI (redondés)    Fournisseur d'identité (MFA)    SIEM (journaux)
   = plan de contrôle                     = base du Zero Trust            = supervision
```

**Lecture.**

- Le **SD-WAN** fournit les chemins et l'overlay, le **NGFW** et le **SSE** protègent ce qui y circule : au plus près du site pour l'un, dans le cloud pour l'autre.
- Le **SASE** n'est pas une brique de plus : c'est la combinaison SD-WAN et SSE sous une gestion commune. L'orientation du trafic (interne par l'overlay, Internet et SaaS par le SSE) est décidée par la politique SD-WAN.
- Le **Zero Trust** fixe la règle de décision pour tous : aucun segment n'est de confiance par nature, chaque accès est authentifié et autorisé.

**Ce que le laboratoire couvre.** Il simule seulement la brique SD-WAN (chemins, SLA, politique centralisée) et un début de segmentation applicative. Il ne contient ni NGFW, ni SSE, ni identité, ni Zero Trust : c'est ce que le test de breakout local (mission 10) et la segmentation (mission 9) rappellent explicitement.

<img width="1917" height="977" alt="image" src="https://github.com/user-attachments/assets/99c1fd62-4487-4ef6-8da9-88fbfcdf5da2" />


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

<img width="1776" height="557" alt="image" src="https://github.com/user-attachments/assets/754b514f-ba73-4856-bb67-ffe3e3a305a6" />
<img width="1917" height="857" alt="image" src="https://github.com/user-attachments/assets/c195659f-4c96-42eb-a264-192b3f7816e8" />
<img width="1865" height="757" alt="image" src="https://github.com/user-attachments/assets/2d4b051e-e93e-4331-9e11-2ec5fcf05ad1" />


| Risque | Preuve | Contre-mesure |
|---|---|---|
| Accès non autorisé à l'ERP depuis le réseau invité | `F_erp_denied.txt` : HTTP 403 Forbidden | Maintenir la segmentation réseau et les règles d'accès par rôle |
| Accès insuffisamment contrôlé à l'ERP depuis le réseau employé | `F_erp_allowed.txt` : HTTP 200 OK ; authentification non démontrée | Renforcer l'authentification et appliquer le principe du moindre privilège |
| Interception des données entre les sites | `F_erp_allowed.txt` : chemin MPLS sélectionné ; chiffrement non vérifié | Mettre en place IPsec ou un mécanisme de chiffrement équivalent |
| Sortie locale SaaS mal contrôlée | `F_saas_local.txt` : `"breakout": "local-at-paris-edge"` | Filtrer les destinations et surveiller le trafic sortant |

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

### 12.2 Gabarits complétés

#### Politique par application (LLD)

Les seuils RTT et perte reprennent ceux du kit (`policy.json`), pour rester cohérents avec les mesures du TP. Les temporisations et seuils de retour sont des propositions de conception : le kit n'en possède pas, et ce sont eux qui évitent le flapping.

| Application | Chemin préféré | Chemin de secours | RTT max (ms) | Perte max (%) | Temporisation de maintien | Seuil de retour | Sonde | Journalisation |
|---|---|---|---|---|---|---|---|---|
| ERP | MPLS | Internet (overlay chiffré) | 100 | 20 | 30 s sur le secours avant retour | Retour sur MPLS si RTT <= 80 ms et perte <= 5 % pendant 60 s consécutives | 1 sonde/s par transport, fenêtre de 12 échantillons, `down` après 3,5 s sans réponse | Chaque bascule : application, ancien et nouveau chemin, `policy_reason`, RTT, perte. Alarme si `degraded-no-path-meets-sla` |
| Teams | Internet | MPLS | 100 | 20 (en production, viser 1 à 2 % pour la voix) | 30 s sur le secours avant retour | Retour sur Internet si RTT <= 80 ms et perte <= 5 % pendant 60 s | Identique, avec mesure de gigue ajoutée en production | Bascules, dépassements de SLA soutenus, alarme en cas de flapping (plus de 3 bascules en 10 min) |
| Sauvegarde | Internet | MPLS | 350 | 60 | 120 s (flux non interactif, tolérant) | Retour sur Internet si RTT <= 300 ms et perte <= 30 % pendant 120 s | Identique | Volume transféré, bascules, reprises de session |
| Invité | Breakout local Internet uniquement, sans overlay | Aucun vers l'overlay (applications métier interdites) ; second accès Internet local si disponible | Sans objet (non garanti) | Sans objet | Sans objet | Sans objet | Sonde de disponibilité de la sortie locale | Chaque refus 403 ou blocage ACL : source, destination, règle. Alarme si pic de refus ou balayage |

Les temporisations de 30, 60 et 120 secondes sont des hypothèses de travail, à valider par des tests de bascule. Le seuil de retour est volontairement plus strict que le seuil de départ (hystérésis) : sans cela, un lien qui oscille autour de 100 ms provoque des allers-retours permanents.

---

#### Comparaison fournisseurs

Les deux colonnes décrivent deux approches d'architecture classiques. À renommer avec les deux produits étudiés dans ton cours, en gardant la structure. Aucun prix n'est avancé.

| Critère | Approche 1 : SD-WAN dédié (orchestrateur, contrôleurs et Edges séparés) | Approche 2 : SD-WAN intégré au NGFW, avec SSE/SASE cloud |
|---|---|---|
| Gestion | Console centrale propre au SD-WAN, politiques par application et par segment, ZTP natif. La sécurité est administrée séparément | Gestion unifiée du réseau et de la sécurité, une seule politique. Moins de finesse possible sur le pilotage de l'overlay selon les cas |
| Overlay | Tunnels IPsec/IKEv2 ou équivalent entre Edges et hubs, maillage ou hub and spoke, segmentation de bout en bout par identifiant de VPN | Tunnels IPsec entre équipements, souvent hub and spoke. Le trafic Internet et SaaS est dirigé vers le service SSE cloud |
| Sécurité | Chiffrement et PKI intégrés. Pare-feu et SSE à ajouter ou à chaîner | NGFW, IPS, filtrage web et ZTNA intégrés. Inspection TLS native, mais dépendance au fournisseur de sécurité |
| Haute disponibilité | Contrôleurs en cluster sur deux data centers, Edges en paire par site. Plus de composants à redonder et à superviser | Paires de pare-feu par site, HA native. Cloud SSE redondé par le fournisseur, avec moins de maîtrise de notre côté |
| Coût | Licences par Edge et par débit, plus coût des contrôleurs et de la PKI. Sécurité facturée en plus | Licences de sécurité souvent plus élevées, mais moins d'équipements à acheter. Abonnement SSE récurrent |

**Conclusion à rédiger dans le rapport** : choisir l'approche 1 si l'exigence porte sur la finesse du pilotage des chemins, l'approche 2 si l'objectif est d'unifier réseau et sécurité. Justifier avec les besoins de Meridian : 3 sites, 2 data centers, du SaaS et un segment invité.

---

#### Modèle de coût

`TCO sur 36 mois = CAPEX + 36 x OPEX mensuel`

Aucun prix n'est inventé : la colonne « Montant » est une formule à remplir avec les devis reçus. Hypothèses de dimensionnement : 5 sites (Paris, Londres, Berlin, 2 data centers), 2 transports par site, 2 Edges par site pour la redondance.

| Poste | Type | Hypothèse | Montant |
|---|---|---|---|
| Edges SD-WAN | CAPEX | 5 sites x 2 Edges, aucun remplacement sur 36 mois | 10 x prix unitaire Edge |
| Contrôleurs, orchestrateur, PKI | CAPEX | Cluster de 3 instances réparties sur 2 data centers | Devis fournisseur |
| NGFW de site ou passerelle SSE d'installation | CAPEX | Un pare-feu par site (approche 2) ou passerelle cloud | Devis fournisseur |
| Installation, ZTP, recette, formation | CAPEX | Forfait initial de mise en service | Nombre de jours x taux journalier |
| Licences SD-WAN | OPEX | Abonnement par Edge et par débit, facturé mensuellement | 10 x licence mensuelle |
| Licences sécurité (NGFW, IPS, SSE) | OPEX | Abonnement par site ou par utilisateur | Devis fournisseur / 12 |
| Liens MPLS | OPEX | 5 liens MPLS | 5 x tarif opérateur mensuel |
| Accès Internet | OPEX | 5 accès Internet, avec secours selon besoin | 5 x tarif mensuel |
| Support et maintenance | OPEX | Contrat annuel, pourcentage du matériel | Pourcentage x CAPEX matériel / 12 |
| Supervision et SIEM | OPEX | Stockage et analyse des journaux | Devis ou coût d'hébergement |
| Exploitation interne | OPEX | Temps d'équipe pour l'administration et les mises à jour | Jours/mois x taux journalier |

**Application de la formule**

- `CAPEX` = somme des quatre premières lignes.
- `OPEX mensuel` = somme des lignes OPEX.
- `TCO 36 mois` = CAPEX + 36 x OPEX mensuel.

**Points d'attention pour le rapport**

- Le SD-WAN permet souvent de réduire le coût des liens MPLS en s'appuyant davantage sur Internet. C'est un gain potentiel, à chiffrer avec des devis réels et non à supposer.
- À l'inverse, la redondance des contrôleurs, la PKI et la supervision ajoutent des coûts récurrents faciles à oublier.
- Distinguer clairement les investissements (CAPEX) des coûts récurrents (OPEX), et indiquer la part de chaque poste dans le TCO.

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

Résultat : 
```txt
/captures:
total 156
-rw-r--r-- 1 1000 1000 67087 Oct 22 05:58 01_all_traffic.pcap
-rw-r--r-- 1 1000 1000  4300 Oct 22 05:59 01b_mpls_only.pcap
-rw-r--r-- 1 root root 26684 Oct 22 06:32 02_overlay.pcap
-rw-r--r-- 1 root root  1917 Oct 22 06:20 03_employee.pcap
-rw-r--r-- 1 root root 22306 Oct 22 06:20 03_paris_edge.pcap
-rw-r--r-- 1 root root  2884 Oct 22 07:25 04_guest_lan.pcap
-rw-r--r-- 1 root root  1440 Oct 22 07:30 05_saas_breakout.pcap
-rw-r--r-- 1 root root    24 Oct 22 07:03 06_blackout_mpls.pcap
-rw-r--r-- 1 root root  1777 Oct 22 07:13 07_control.pcap
drwxrwxr-x 2 1000 1000  4096 Oct 22 07:40 preuves

/captures/preuves:
total 128
-rw-rw-r-- 1 1000 1000 1159 Oct 22 05:37 A_compose_ps.txt
-rw-r--r-- 1 1000 1000  438 Oct 22 05:38 A_erp.txt
-rw-r--r-- 1 1000 1000  722 Oct 22 05:37 A_status.txt
-rw-r--r-- 1 root root  467 Oct 22 06:08 B_icmp.txt
-rw-r--r-- 1 root root  698 Oct 22 06:08 B_udp45900.txt
-rw-r--r-- 1 root root 2877 Oct 22 06:40 C_decrypt.txt
-rw-r--r-- 1 root root 5596 Oct 22 06:40 C_http_lan.txt
-rw-r--r-- 1 root root  861 Oct 22 06:40 C_udp_hex.txt
-rw-r--r-- 1 root root  453 Oct 22 07:00 D_blackout_erp.txt
-rw-r--r-- 1 root root  517 Oct 22 07:00 D_blackout_sla.txt
-rw-r--r-- 1 root root  740 Oct 22 07:00 D_blackout_status.txt
-rw-r--r-- 1 root root 1713 Oct 22 07:02 D_blackout_watch.txt
-rw-r--r-- 1 root root  499 Oct 22 06:59 D_brownout_sla.txt
-rw-r--r-- 1 root root 3333 Oct 22 06:56 D_brownout_watch.txt
-rw-r--r-- 1 root root  504 Oct 22 06:47 D_nominal_sla.txt
-rw-r--r-- 1 root root  503 Oct 22 07:10 D_return_sla.txt
-rw-r--r-- 1 root root  727 Oct 22 07:11 E_before_status.txt
-rw-r--r-- 1 root root  729 Oct 22 07:17 E_policy_after.txt
-rw-r--r-- 1 root root  455 Oct 22 07:17 E_policy_after_erp.txt
-rw-r--r-- 1 root root  730 Oct 22 07:16 E_policy_before.txt
-rw-r--r-- 1 root root  446 Oct 22 07:12 E_stopped_erp.txt
-rw-r--r-- 1 root root  729 Oct 22 07:12 E_stopped_status.txt
-rw-r--r-- 1 root root  924 Oct 22 07:40 F_erp_allowed.txt
-rw-r--r-- 1 root root  664 Oct 22 07:40 F_erp_denied.txt
-rw-r--r-- 1 root root  330 Oct 22 07:40 F_saas_local.txt
-rw-r--r-- 1 1000 1000  290 Oct 22 05:49 M1_berlin_ifmap.txt
-rw-r--r-- 1 1000 1000  164 Oct 22 05:49 M1_employee_route.txt
-rw-r--r-- 1 1000 1000  327 Oct 22 05:49 M1_paris_ifmap.txt
-rw-r--r-- 1 1000 1000  421 Oct 22 05:49 M1_paris_route.txt
-rw-r--r-- 1 root root  331 Oct 22 06:26 Q3_erp_arrete.txt
-rw-r--r-- 1 root root  264 Oct 22 06:27 Q3_overlay_coupe.txt
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

<img width="1917" height="891" alt="image" src="https://github.com/user-attachments/assets/34e380d2-0b6c-4b6d-9a70-c641dabf392d" />


```bash
cp policy/policy.original.json policy/policy.json
```

## Nettoyage :

```bash
cat > nettoyage_total.sh <<'EOF'
#!/usr/bin/env bash
# nettoyage_total.sh : supprime le laboratoire SD-WAN et tout le contenu Docker.
#
# Usage (depuis le dossier du projet, celui qui contient compose.yaml) :
#   chmod +x nettoyage_total.sh
#   ./nettoyage_total.sh                  # vide Docker + supprime le dossier du projet
#   ./nettoyage_total.sh --purge-docker   # idem + désinstalle Docker de la machine
#   ./nettoyage_total.sh --keep-captures  # copie captures/ dans ~/sauvegarde_captures avant
#
# ATTENTION : supprime TOUS les conteneurs, images, réseaux, volumes et caches
# Docker de la machine, pas seulement ceux du TP. Action irréversible.

set -u

PURGE_DOCKER=0
KEEP_CAPTURES=0
for arg in "$@"; do
  case "$arg" in
    --purge-docker)  PURGE_DOCKER=1 ;;
    --keep-captures) KEEP_CAPTURES=1 ;;
    -h|--help) sed -n '2,12p' "$0"; exit 0 ;;
    *) echo "Option inconnue : $arg"; exit 1 ;;
  esac
done

PROJECT_DIR="$(pwd -P)"

# Sécurités : on ne supprime que le dossier du projet
if [ ! -f "$PROJECT_DIR/compose.yaml" ]; then
  echo "Erreur : compose.yaml introuvable ici. Lancez le script depuis le dossier du projet."
  exit 1
fi
case "$PROJECT_DIR" in
  /|/home|/root|"$HOME"|/usr|/etc|/var|/opt)
    echo "Erreur : dossier refusé par sécurité : $PROJECT_DIR"; exit 1 ;;
esac

# Docker avec ou sans sudo
if docker info >/dev/null 2>&1; then
  DOCKER="docker"
elif sudo docker info >/dev/null 2>&1; then
  DOCKER="sudo docker"
else
  DOCKER=""
fi

echo "=== Nettoyage total ==="
echo "Dossier du projet : $PROJECT_DIR"
echo "Docker de la machine : tout sera vidé"
[ "$PURGE_DOCKER" -eq 1 ] && echo "Docker sera aussi désinstallé"
echo
read -r -p "Tapez OUI pour confirmer : " REP
[ "$REP" = "OUI" ] || { echo "Annulé."; exit 0; }

# 1. Sauvegarde facultative des captures
if [ "$KEEP_CAPTURES" -eq 1 ] && [ -d "$PROJECT_DIR/captures" ]; then
  DEST="$HOME/sauvegarde_captures"
  echo "[1] Sauvegarde des captures dans $DEST"
  mkdir -p "$DEST"
  sudo cp -r "$PROJECT_DIR/captures/." "$DEST/"
  sudo chown -R "$(id -u):$(id -g)" "$DEST"
fi

# 2. Docker
if [ -n "$DOCKER" ]; then
  echo "[2] Arrêt et suppression du projet Compose"
  $DOCKER compose down --rmi all --volumes --remove-orphans 2>/dev/null

  echo "[3] Suppression de tous les conteneurs"
  IDS=$($DOCKER ps -aq)
  [ -n "$IDS" ] && $DOCKER rm -f $IDS

  echo "[4] Suppression de toutes les images"
  IDS=$($DOCKER images -aq)
  [ -n "$IDS" ] && $DOCKER rmi -f $IDS

  echo "[5] Suppression de tous les volumes"
  IDS=$($DOCKER volume ls -q)
  [ -n "$IDS" ] && $DOCKER volume rm -f $IDS

  echo "[6] Suppression des réseaux personnalisés"
  IDS=$($DOCKER network ls --filter type=custom -q)
  [ -n "$IDS" ] && $DOCKER network rm $IDS 2>/dev/null

  echo "[7] Nettoyage final (caches de build, éléments orphelins)"
  $DOCKER system prune -a --volumes -f
  $DOCKER builder prune -a -f
else
  echo "Docker introuvable ou inaccessible : étapes Docker ignorées."
fi

# 3. Désinstallation de Docker (facultatif)
if [ "$PURGE_DOCKER" -eq 1 ]; then
  echo "[8] Désinstallation de Docker"
  sudo systemctl stop docker docker.socket containerd 2>/dev/null
  sudo apt purge -y docker-ce docker-ce-cli containerd.io \
       docker-buildx-plugin docker-compose-plugin docker-ce-rootless-extras 2>/dev/null
  sudo apt autoremove -y --purge
  sudo rm -rf /var/lib/docker /var/lib/containerd /etc/docker
  sudo rm -f /etc/apt/sources.list.d/docker.list /etc/apt/keyrings/docker.asc
fi

# 4. Suppression des fichiers du projet (sudo : captures/ appartient à root)
echo "[9] Suppression du dossier du projet : $PROJECT_DIR"
cd .. || exit 1
sudo rm -rf "$PROJECT_DIR"

echo
echo "=== Terminé ==="
if command -v docker >/dev/null 2>&1; then
  echo "Vérification :"
  docker ps -a 2>/dev/null || sudo docker ps -a
  docker images 2>/dev/null || sudo docker images
  docker network ls 2>/dev/null || sudo docker network ls
fi
EOF
chmod +x nettoyage_total.sh
```

```bash
./nettoyage_total.sh 
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
