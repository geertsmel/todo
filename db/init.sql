-- Création de la base et de la table des todos, avec un statut à trois valeurs :
--   todo (à faire), in_progress (en cours), done (terminée).
-- Le script peut être relancé sans danger : il ne recrée rien s'il existe déjà,
-- et il migre automatiquement une ancienne table qui utilisait la colonne IsDone.

IF DB_ID(N'TodoDb') IS NULL
BEGIN
    CREATE DATABASE TodoDb;
END
GO

USE TodoDb;
GO

-- 1. Nouvelle installation : création de la table
IF OBJECT_ID(N'dbo.Todos', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.Todos (
        Id        INT IDENTITY(1,1) PRIMARY KEY,
        Title     NVARCHAR(200) NOT NULL,
        Status    NVARCHAR(20) NOT NULL CONSTRAINT DF_Todos_Status DEFAULT N'todo',
        CreatedAt DATETIME2 NOT NULL CONSTRAINT DF_Todos_CreatedAt DEFAULT SYSUTCDATETIME(),
        CONSTRAINT CK_Todos_Status CHECK (Status IN (N'todo', N'in_progress', N'done'))
    );

    -- Les tâches d'exemple sont insérées via EXEC : sans cela, SQL Server vérifie la colonne Status
    -- avant l'exécution du bloc et refuse tout le lot quand une ancienne table (sans Status) existe déjà.
    EXEC(N'INSERT INTO dbo.Todos (Title, Status) VALUES
        (N''Installer Docker'', N''done''),
        (N''Lancer SQL Server dans un conteneur'', N''done''),
        (N''Ajouter un graphique en camembert'', N''in_progress''),
        (N''Gérer ma liste de todos dans le navigateur'', N''todo'')');
END
GO

-- 2. Ancienne table : ajout de la colonne Status
IF COL_LENGTH(N'dbo.Todos', N'Status') IS NULL
BEGIN
    ALTER TABLE dbo.Todos ADD Status NVARCHAR(20) NOT NULL CONSTRAINT DF_Todos_Status DEFAULT N'todo';
END
GO

-- 3. Ancienne table : reprise des anciennes valeurs (IsDone = 1 devient done), puis suppression d'IsDone
IF COL_LENGTH(N'dbo.Todos', N'IsDone') IS NOT NULL
BEGIN
    EXEC(N'UPDATE dbo.Todos SET Status = N''done'' WHERE IsDone = 1');

    DECLARE @df sysname = (
        SELECT dc.name
        FROM sys.default_constraints dc
        JOIN sys.columns c ON c.object_id = dc.parent_object_id AND c.column_id = dc.parent_column_id
        WHERE dc.parent_object_id = OBJECT_ID(N'dbo.Todos') AND c.name = N'IsDone'
    );
    IF @df IS NOT NULL
        EXEC(N'ALTER TABLE dbo.Todos DROP CONSTRAINT ' + @df);

    EXEC(N'ALTER TABLE dbo.Todos DROP COLUMN IsDone');
END
GO

-- 4. Ancienne table : contrainte qui n'autorise que les trois statuts
IF NOT EXISTS (
    SELECT 1 FROM sys.check_constraints
    WHERE name = N'CK_Todos_Status' AND parent_object_id = OBJECT_ID(N'dbo.Todos')
)
BEGIN
    ALTER TABLE dbo.Todos ADD CONSTRAINT CK_Todos_Status CHECK (Status IN (N'todo', N'in_progress', N'done'));
END
GO
