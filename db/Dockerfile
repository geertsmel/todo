# Petite image dont le seul rôle est d'exécuter init.sql sur le serveur SQL (service "db").
# Elle réutilise l'image SQL Server pour disposer de l'outil sqlcmd, puis s'arrête.
FROM mcr.microsoft.com/mssql/server:2022-latest

COPY --chmod=644 init.sql /init.sql

CMD ["/bin/bash", "-c", "/opt/mssql-tools18/bin/sqlcmd -C -S db -U sa -P \"$MSSQL_SA_PASSWORD\" -b -i /init.sql"]
