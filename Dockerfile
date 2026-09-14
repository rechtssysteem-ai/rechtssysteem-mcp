# De client is één bestand en gebruikt uitsluitend de Python-standaardbibliotheek.
# Er valt dus niets te installeren: geen pip, geen wheels, geen supply chain.
#
# Deze image draait de server in streamable-http modus, zodat registers zoals
# Glama hem als draaiende server kunnen tonen én bevragen (Inspector). Voor
# dagelijks gebruik is Docker niet nodig — zie de README (stdio modus).
FROM python:3.12-slim

WORKDIR /app
COPY rechtssysteem_mcp.py .

# Onbuffered, anders blijven JSON-RPC-antwoorden in de pijp hangen.
ENV PYTHONUNBUFFERED=1

# voorspel_uitkomst heeft een sleutel nodig; lekkage_check en
# rechtspraak_cijfers niet. Introspectie werkt zonder.
#   docker run -p 8000:8000 -e RECHTSSYSTEEM_API_KEY=... <image>
EXPOSE 8000
ENTRYPOINT ["python3", "rechtssysteem_mcp.py", "--http", "--port", "8000"]
