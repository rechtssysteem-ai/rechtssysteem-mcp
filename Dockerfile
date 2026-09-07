# De client is één bestand en gebruikt uitsluitend de Python-standaardbibliotheek.
# Er valt dus niets te installeren: geen pip, geen wheels, geen supply chain.
#
# Deze image bestaat voor registers die een draaiende server willen zien
# (Glama start hem en stuurt een introspectieverzoek). Voor dagelijks gebruik
# is Docker niet nodig — zie de README.
FROM python:3.12-slim

WORKDIR /app
COPY rechtssysteem_mcp.py .

# Onbuffered, anders blijven JSON-RPC-antwoorden in de pijp hangen.
ENV PYTHONUNBUFFERED=1

# voorspel_uitkomst heeft een sleutel nodig; lekkage_check en
# rechtspraak_cijfers niet. Introspectie werkt zonder.
#   docker run -i -e RECHTSSYSTEEM_API_KEY=... <image>
ENTRYPOINT ["python3", "rechtssysteem_mcp.py"]
