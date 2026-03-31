#!/bin/bash
# Generate multi-language Voxtral TTS demos
# Designed and built by the architect

VOXTRAL="/srv/ai/voxtral/voxtral-tts.c/voxtral_tts"
MODEL="/srv/ai/models/voxtral-4b-tts"
OUTDIR="/srv/ai/voxtral/demos"

mkdir -p "$OUTDIR"

echo "=== Voxtral Multi-Language Demo Generation ==="
echo ""

# English
echo "[1/10] English..."
$VOXTRAL -d $MODEL -v casual_male -o $OUTDIR/en_demo.wav \
  "Welcome to halo ai. Eighty seven tokens per second. Thirty three services. Zero cloud. Built from source on bare metal. Designed and built by the architect."

# French
echo "[2/10] French..."
$VOXTRAL -d $MODEL -v fr_male -o $OUTDIR/fr_demo.wav \
  "Bienvenue sur halo ai. Quatre-vingt-sept tokens par seconde. Trente-trois services. Zero cloud. Compilé depuis les sources. Conçu et construit par l'architecte."

# Spanish
echo "[3/10] Spanish..."
$VOXTRAL -d $MODEL -v es_male -o $OUTDIR/es_demo.wav \
  "Bienvenido a halo ai. Ochenta y siete tokens por segundo. Treinta y tres servicios. Sin nube. Compilado desde el código fuente. Diseñado y construido por el arquitecto."

# German
echo "[4/10] German..."
$VOXTRAL -d $MODEL -v de_male -o $OUTDIR/de_demo.wav \
  "Willkommen bei halo ai. Siebenundachtzig Tokens pro Sekunde. Dreiunddreißig Dienste. Keine Cloud. Aus dem Quellcode kompiliert. Entworfen und gebaut vom Architekten."

# Portuguese
echo "[5/10] Portuguese..."
$VOXTRAL -d $MODEL -v pt_male -o $OUTDIR/pt_demo.wav \
  "Bem-vindo ao halo ai. Oitenta e sete tokens por segundo. Trinta e três serviços. Zero nuvem. Compilado a partir do código fonte. Projetado e construído pelo arquiteto."

# Italian
echo "[6/10] Italian..."
$VOXTRAL -d $MODEL -v it_male -o $OUTDIR/it_demo.wav \
  "Benvenuto su halo ai. Ottantasette token al secondo. Trentatré servizi. Zero cloud. Compilato dal codice sorgente. Progettato e costruito dall'architetto."

# Dutch
echo "[7/10] Dutch..."
$VOXTRAL -d $MODEL -v nl_male -o $OUTDIR/nl_demo.wav \
  "Welkom bij halo ai. Zevenentachtig tokens per seconde. Drieëndertig services. Geen cloud. Gecompileerd vanuit de broncode. Ontworpen en gebouwd door de architect."

# Hindi
echo "[8/10] Hindi..."
$VOXTRAL -d $MODEL -v hi_male -o $OUTDIR/hi_demo.wav \
  "halo ai mein aapka swaagat hai. Sattaasi tokens prati second. Taintees services. Zero cloud. Source code se compile kiya gaya. Architect dwara design aur nirmit."

# Arabic
echo "[9/10] Arabic..."
$VOXTRAL -d $MODEL -v ar_male -o $OUTDIR/ar_demo.wav \
  "Marhaba fi halo ai. Sabaa wa thamaneen token fi al-thaniya. Thalatha wa thalatheen khadima. Bidoon sahaba. Mabni min al-masdar. Samama wa bana min al-muhandis al-miamari."

# Cheerful female English (bonus)
echo "[10/10] English female..."
$VOXTRAL -d $MODEL -v cheerful_female -o $OUTDIR/en_female_demo.wav \
  "Hey there! Welcome to halo ai. The complete bare metal AI stack. Thirty three services, seventeen agents, ninety eight tools. All running on one chip. No cloud. No containers. Just pure silicon. Stamped by the architect."

echo ""
echo "=== Done! $(ls $OUTDIR/*.wav | wc -l) demos generated ==="
ls -lh $OUTDIR/*.wav
