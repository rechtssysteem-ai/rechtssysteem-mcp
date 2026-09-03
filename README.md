# rechtssysteem-mcp

Een MCP-server die AI-agents toegang geeft tot een **eerlijke** voorspelling van
Nederlandse rechtszaken: het model heeft de uitkomst nooit gezien.

## Waarom "eerlijk"

De meeste uitkomstvoorspellers scoren hoog omdat de uitspraak zelf het antwoord
al bevat. Meet je dat, dan blijkt 92% van de teksten de uitkomst letterlijk te
verraden. Wij knippen die zinnen er eerst uit (knipregel R2) en meten wat er
overblijft: **0,1% restlekkage**.

Wat het model daarna nog kan, is dus echt geleerd:

| | |
|---|---|
| Zaken | 609.715 |
| Accuracy | 78,2% |
| Macro-F1 | 77,1% |
| Meerderheidsbaseline | 43,7% |
| Restlekkage na knip | 0,1% (was 92%) |
| Validatie | 5-fold CV, out-of-fold |

Per klasse F1: afgewezen 0,827 · gedeeltelijk 0,726 · toegewezen 0,761.

De baseline staat er met opzet bij. 78,2% zegt niets zonder die 43,7% ernaast.

## Tools

| Tool | Wat het doet |
|---|---|
| `voorspel_uitkomst` | afgewezen / gedeeltelijk / toegewezen, met kansen per klasse |
| `rechtspraak_cijfers` | de benchmarkcijfers hierboven |
| `lekkage_check` | meet of een tekst de uitkomst al verraadt — bruikbaar om andermans dataset of AI-claim te toetsen |

## Installeren

Er is niets te installeren. De client gebruikt uitsluitend de Python-standaard-
bibliotheek — geen pip, geen wheels, geen supply chain. Python 3.10 of hoger.

```bash
curl -O https://raw.githubusercontent.com/<org>/rechtssysteem-mcp/main/rechtssysteem_mcp.py
```

Vraag een API-sleutel aan op https://rechtssysteem.ai.

### Claude Code

```bash
claude mcp add rechtssysteem --scope user \
  --env RECHTSSYSTEEM_API_KEY=je-sleutel \
  -- python3 /pad/naar/rechtssysteem_mcp.py
```

### Claude Desktop — `claude_desktop_config.json`

```json
{
  "mcpServers": {
    "rechtssysteem": {
      "command": "python3",
      "args": ["/pad/naar/rechtssysteem_mcp.py"],
      "env": { "RECHTSSYSTEEM_API_KEY": "je-sleutel" }
    }
  }
}
```

## Instellingen

| Variabele | Standaard | |
|---|---|---|
| `RECHTSSYSTEEM_API_KEY` | — | verplicht |
| `RECHTSSYSTEEM_API_URL` | `https://api.rechtssysteem.ai` | |
| `RECHTSSYSTEEM_TIMEOUT` | `30` | seconden |

## Privacy

De zaaktekst gaat naar de server van Rechtssysteem.ai om geanalyseerd te worden.
Stuur geen tekst die u niet mag delen. Maximaal 20.000 tekens per verzoek.

## Wat dit niet is

Een risico-indicatie op grond van vergelijkbare rechtspraak. **Geen juridisch
advies.** Bij een zekerheid onder 55% zegt de tool "weet niet", en dat is dan ook
het enige juiste antwoord.

## Juridische status & aansprakelijkheid

1. **Geen juridisch advies.** Deze MCP-server is uitsluitend bedoeld voor
   statistische analyse, benchmarking en onderzoek van openbare rechterlijke
   uitspraken. De output vormt uitdrukkelijk geen juridisch advies, geen
   bindende proceskansenbeoordeling en geen vervanging van een advocaat.
2. **Beperking.** Rechterlijke beslissingen hangen af van individuele feiten,
   procesvoering, bewijswaardering en de discretionaire bevoegdheid van de
   rechter. Statistiek over het verleden garandeert niets over de toekomst.
3. **Onzekerheidsdrempel.** Bij een zekerheid onder 55% geeft het systeem
   "onbepaald — onvoldoende statistische significantie". De drempel is een
   gekozen instelling en kan wijzigen.
4. **Aansprakelijkheid.** Rechtssysteem.ai is niet aansprakelijk voor schade
   die voortvloeit uit gebruik van of vertrouwen op deze software, behoudens
   opzet of bewuste roekeloosheid. Tegenover zakelijke afnemers is de
   aansprakelijkheid in elk geval beperkt tot het bedrag dat in de twaalf
   maanden vóór de schadeveroorzakende gebeurtenis voor de dienst is betaald.
   Tegenover consumenten geldt deze beperking slechts voor zover zij niet
   onredelijk bezwarend is; dwingend consumentenrecht blijft onverkort gelden.
5. **AI-transparantie.** Alle output wordt volledig gegenereerd door een
   machine-learning model (LightGBM); er komt geen menselijke beoordeling aan
   te pas. Rechtssysteem.ai vermeldt dit uit eigen beweging. Het systeem
   genereert geen synthetische inhoud in de zin van artikel 50, lid 2, van de
   AI-verordening.
6. **Niet bestemd voor rechterlijke instanties.** Deze software is niet
   bedoeld voor gebruik door of namens een rechterlijke instantie bij het
   onderzoeken en uitleggen van feiten en recht, noch voor autonome
   geschilbeslechting zonder menselijke tussenkomst.

## Merk, intellectueel eigendom & licentie

Copyright 2026 Rechtssysteem.ai (The Coppola Connection).

Deze client is gelicentieerd onder de Apache License, Version 2.0. Zie
[LICENSE](LICENSE) en [NOTICE](NOTICE).

Het model, de trainingsdata en de lekkage-knipregel (R2) zijn **niet** onder
deze licentie vrijgegeven en blijven eigendom van Rechtssysteem.ai.

"Rechtssysteem.ai" en "rechtssysteem-mcp" zijn handelsnamen. Conform Section 6
van de Apache-2.0 licentie verleent deze licentie geen recht op het gebruik van
handelsnamen, merken of productnamen van de licentiegever, behoudens redelijk
en gebruikelijk redactioneel gebruik ter aanduiding van de herkomst.
