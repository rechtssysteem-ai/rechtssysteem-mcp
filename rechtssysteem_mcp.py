#!/usr/bin/env python3
"""rechtssysteem-mcp — eerlijke Nederlandse rechtspraak-laag voor AI-agents.

Copyright 2026 Rechtssysteem.ai
Licensed under the Apache License, Version 2.0. Zie LICENSE en NOTICE.

Open-core client: deze MCP-server roept de gehoste API van Rechtssysteem.ai
aan. Het model, de trainingsdata én de lekkage-knip draaien op onze servers en
zijn niet publiek. Deze client bevat uitsluitend protocol-afhandeling en
gebruikt alleen de Python-standaardbibliotheek — geen externe pakketten, dus
niets te installeren en niets te vergiftigen.

Alle output is AI-gegenereerd (LightGBM), zonder menselijke tussenkomst.
Niet bestemd voor gebruik door of namens een rechterlijke instantie.

Tools:
  voorspel_uitkomst   - oordeel over een Nederlandse zaaktekst (lekkage-vrij)
  rechtspraak_cijfers - benchmark-cijfers (609.715 zaken)
  lekkage_check       - meet of een tekst de uitkomst al verraadt

Instellen:
    export RECHTSSYSTEEM_API_KEY="je-sleutel"
    export RECHTSSYSTEEM_API_URL="https://api.rechtssysteem.ai"  # optioneel

Registreren in Claude Code:
    claude mcp add rechtssysteem --scope user \
      --env RECHTSSYSTEEM_API_KEY=... \
      -- python3 /pad/naar/rechtssysteem_mcp.py

Registreren in Claude Desktop (claude_desktop_config.json):
{
  "mcpServers": {
    "rechtssysteem": {
      "command": "python3",
      "args": ["/pad/naar/rechtssysteem_mcp.py"],
      "env": {"RECHTSSYSTEEM_API_KEY": "je-sleutel"}
    }
  }
}

Risico-indicatie op basis van vergelijkbare rechtspraak; geen juridisch advies.
Zekerheid < 55% = "weet niet".
"""
import json
import os
import sys
import urllib.error
import urllib.request

NAAM = "rechtssysteem-mcp"
VERSIE = "0.3.0"
PROTOCOL = "2024-11-05"

API_URL = os.environ.get("RECHTSSYSTEEM_API_URL",
                         "https://api.rechtssysteem.ai").rstrip("/")
API_KEY = os.environ.get("RECHTSSYSTEEM_API_KEY", "")
TIMEOUT = float(os.environ.get("RECHTSSYSTEEM_TIMEOUT", "30"))
TEKST_CAP = 20_000

GEEN_SLEUTEL = (
    "RECHTSSYSTEEM_API_KEY is niet gezet. Vraag een sleutel aan op "
    "https://rechtssysteem.ai en zet hem in de omgeving van deze MCP-server."
)


class ApiFout(Exception):
    """Nette fout die als tool-tekst richting de agent gaat."""


def _roep_api(pad, methode="POST", body=None):
    """Praat met de model-API. Geeft dict terug of gooit ApiFout."""
    if not API_KEY:
        raise ApiFout(GEEN_SLEUTEL)

    data = None if body is None else json.dumps(body).encode("utf-8")
    verzoek = urllib.request.Request(
        f"{API_URL}{pad}",
        data=data,
        method=methode,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": f"{NAAM}/{VERSIE}",
        },
    )
    try:
        with urllib.request.urlopen(verzoek, timeout=TIMEOUT) as antwoord:
            return json.loads(antwoord.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        romp = e.read().decode("utf-8", "replace")[:500]
        try:
            detail = json.loads(romp).get("detail", romp)
        except (ValueError, AttributeError):
            detail = romp
        if e.code == 401:
            raise ApiFout("ongeldige of ontbrekende API-sleutel (401)") from e
        if e.code == 413:
            raise ApiFout(f"tekst te lang (max {TEKST_CAP:,} tekens)") from e
        if e.code == 429:
            raise ApiFout("te veel verzoeken (429) — probeer het zo weer") from e
        raise ApiFout(f"server gaf {e.code}: {detail}") from e
    except urllib.error.URLError as e:
        raise ApiFout(f"server niet bereikbaar op {API_URL} ({e.reason})") from e
    except TimeoutError as e:
        raise ApiFout(f"time-out na {TIMEOUT:g}s") from e
    except json.JSONDecodeError as e:
        raise ApiFout("server gaf geen geldige JSON terug") from e


def _eis_tekst(args):
    tekst = args.get("tekst") or ""
    if not tekst.strip():
        raise ApiFout("lege tekst")
    if len(tekst) > TEKST_CAP:
        raise ApiFout(f"tekst is {len(tekst):,} tekens, max {TEKST_CAP:,}")
    return tekst


# ---------------- tools --------------------------------------------------------
def tool_voorspel(args):
    uit = _roep_api("/voorspel", body={
        "tekst": _eis_tekst(args),
        "domein": args.get("rechtsgebied") or None,
    })
    kansen = ", ".join(f"{l}={k:.1%}" for l, k in uit["kansen"].items())
    regels = [
        f"UITKOMST: {uit['label']} (zekerheid {uit['zekerheid']:.0%})",
        f"rechtsgebied: {uit['rechtsgebied']}",
        f"kansen: {kansen}",
    ]
    if uit["zekerheid"] < 0.55:
        regels.append("LET OP: zekerheid onder 55% — behandel dit als 'weet niet'.")
    regels.append("Risico-indicatie op basis van vergelijkbare rechtspraak; "
                  "geen juridisch advies.")
    return "\n".join(regels)


def tool_cijfers(_args):
    c = _roep_api("/cijfers", methode="GET")

    def nl(x, cijfers=4):
        """Nederlandse notatie: komma als decimaalteken."""
        return f"{x:.{cijfers}f}".replace(".", ",")

    def pct(x, cijfers=1):
        return f"{x * 100:.{cijfers}f}".replace(".", ",") + "%"

    zaken = f"{c['zaken']:,}".replace(",", ".")
    verdeling = " / ".join(f"{k} {pct(v)}" for k, v in c["verdeling"].items())
    per_klasse = " · ".join(f"{k} {nl(v, 3)}" for k, v in c["f1_per_klasse"].items())
    return (
        "Rechtssysteem.ai — Nederlandse rechtspraak-analyse "
        "(eerlijk, antwoorden uit de invoer):\n"
        f"records: {zaken} · labels: {verdeling}\n"
        f"model ({c['validatie']}): accuracy {nl(c['accuracy'])} · "
        f"macro-F1 {nl(c['macro_f1'])}\n"
        f"per klasse F1: {per_klasse}\n"
        f"restlekkage na knip R2: {pct(c['restlekkage'])} "
        f"(was {pct(c['lekkage_zonder_knip'], 0)} zonder knip)\n"
        f"meerderheidsbaseline: {pct(c['baseline'])}\n"
        f"Bron: {c['bron']}"
    )


def tool_lekkage(args):
    uit = _roep_api("/lekkage", body={"tekst": _eis_tekst(args)})
    tekens = f"{uit['tekens']:,}".replace(",", ".")
    regels = [f"tekst: {tekens} tekens"]
    regels.append(
        "LEKKAGE: de tekst spreekt de uitkomst al uit ("
        + ", ".join(uit["sterk_ruw"]) + ")."
        if uit["sterk_ruw"] else "tekst is schoon."
    )
    regels.append(
        "waarschuwing: ook na de knip resteert uitkomst-taal ("
        + ", ".join(uit["sterk_na"]) + ")."
        if uit["sterk_na"] else "na de rechtssysteem-knip (R2): invoer is lekkage-vrij."
    )
    return "\n".join(regels)


HANDLERS = {
    "voorspel_uitkomst": tool_voorspel,
    "rechtspraak_cijfers": tool_cijfers,
    "lekkage_check": tool_lekkage,
}

_PRIVACY = (" De zaaktekst wordt voor de analyse naar de server van "
            "Rechtssysteem.ai gestuurd; stuur geen tekst die u niet mag delen.")

TOOLS = [
    {"name": "voorspel_uitkomst",
     "description": ("Voorspelt de uitkomst van een Nederlandse rechtszaak "
                     "(afgewezen/gedeeltelijk/toegewezen) uit de zaaktekst. "
                     "Uitkomst-aankondigende zinnen worden eerst verwijderd "
                     "(lekkage-vrij). Gemeten 5-fold CV op 609.715 zaken: "
                     "accuracy 78,2%, macro-F1 77,1%, tegen een "
                     "meerderheidsbaseline van 43,7%. Zekerheid < 55% = "
                     "'weet niet'. Risico-indicatie, geen juridisch advies."
                     + _PRIVACY),
     "inputSchema": {"type": "object",
                     "properties": {"tekst": {"type": "string"},
                                    "rechtsgebied": {"type": "string"}},
                     "required": ["tekst"]}},
    {"name": "rechtspraak_cijfers",
     "description": ("Benchmark-cijfers van de Nederlandse rechtspraak-analyse: "
                     "609.715 zaken, acc 78,2%, macro-F1 77,1%, restlekkage "
                     "0,1% (was 92% zonder knip), baseline 43,7%."),
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "lekkage_check",
     "description": ("Meet of een tekst de uitkomst al letterlijk bevat. "
                     "Controle voor datasets en AI-claims." + _PRIVACY),
     "inputSchema": {"type": "object",
                     "properties": {"tekst": {"type": "string"}},
                     "required": ["tekst"]}},
]


# ---------------- MCP-protocol -------------------------------------------------
def afhandel(msg):
    methode = msg.get("method")
    idd = msg.get("id")
    if methode == "initialize":
        return {"jsonrpc": "2.0", "id": idd, "result": {
            "protocolVersion": PROTOCOL, "capabilities": {"tools": {}},
            "serverInfo": {"name": NAAM, "version": VERSIE}}}
    if methode in ("notifications/initialized", "notifications/cancelled"):
        return None
    if methode == "ping":
        return {"jsonrpc": "2.0", "id": idd, "result": {}}
    if methode == "tools/list":
        return {"jsonrpc": "2.0", "id": idd, "result": {"tools": TOOLS}}
    if methode == "tools/call":
        naam = msg.get("params", {}).get("name")
        args = msg.get("params", {}).get("arguments", {}) or {}
        handler = HANDLERS.get(naam)
        if handler is None:
            tekst, fout = f"onbekende tool: {naam}", True
        else:
            try:
                tekst, fout = handler(args), False
            except ApiFout as e:
                tekst, fout = f"FOUT: {e}", True
            except Exception as e:  # noqa: BLE001
                tekst, fout = f"FOUT: onverwachte fout ({type(e).__name__})", True
        return {"jsonrpc": "2.0", "id": idd, "result": {
            "content": [{"type": "text", "text": tekst}], "isError": fout}}
    return {"jsonrpc": "2.0", "id": idd, "error": {
        "code": -32601, "message": f"onbekende methode: {methode}"}}


def main():
    for regel in sys.stdin:
        regel = regel.strip()
        if not regel:
            continue
        try:
            msg = json.loads(regel)
        except json.JSONDecodeError:
            continue
        antwoord = afhandel(msg)
        if antwoord is not None:
            print(json.dumps(antwoord, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
