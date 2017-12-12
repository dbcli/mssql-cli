# Usage Guide
Contents
* [Description](#description)
* [Options](#options)
* [Examples](#examples)
*  [Environment Variables](#environment-variables)

## Description
mssql-cli is a new and interactive command line query tool for SQL Server. This open source tool works cross-platform and is a proud member of the dbcli community.

mssql-cli provides the following key enhancements over sqlcmd in the Terminal environment:
- T-SQL IntelliSense
- Syntax highlighting
- Pretty formatting for query results, including Vertical Format
- Multi-line edit mode
- Configuration file support


## Options
Type **mssql-cli --help** to also see these options.

```bash 
$ mssql-cli --help
Usage: main.py [OPTIONS]

Options:
    -S, --server TEXT       SQL Server instance name or address.
    -U, --username TEXT     Username to connect to the database.
    -W, --password          Force password prompt.
    -E, --integrated        Use integrated authentication on windows.
    -v, --version           Version of mssql-cli.
    -d, --database TEXT     database name to connect to.
    --mssqlclirc TEXT       Location of mssqlclirc config file.
    --row-limit INTEGER     Set threshold for row limit prompt. Use 0 to disable
                            prompt.
    --less-chatty           Skip intro on startup and goodbye on exit.
    --auto-vertical-output  Automatically switch to vertical output mode if the
                            result is wider than the terminal width.
    --help                  Show this message and exit.
```
      
## Examples
Below are example commands that run against the AdventureWorks database in a localhost server instance. Here is a list of examples:

 * [Connect to a server](#connect-to-a-server)
 * [Exit mssql-cli](#exit-mssql-cli)
 * [Navigate multiple pages of query result](#navigate-multiple-pages-of-query-result)
 * [Quit a query](#quit-a-query)
 * [Clear screen](#clear-screen)
 * [Toggle multi-line mode](#toggle-multi-line-mode)

### Connect to a server
Connect to a server, a specific database, and with a username. -S -d and -U are optional. You can [set environment variables](#Environment-Variables) to set default settings.

```bash
mssql-cli -S localhost -d AdventureWorks -U sa
```

### Exit mssql-cli 
Press **Ctrl+D** or type:
```bash
quit
```

### Navigate multiple pages of query result
If you select a table that has many rows, it may display the results in multiple pages.

- Press **Enter** key to see one row at a time.
- Press **Space bar** to see one page at a time.
- Press **q** to escape from the result view.

### Quit a query
If you are in the middle of writing a query and would like to cancel it, press **Ctrl+C**

### Clear screen
If you want to clear the Terminal view, press **Ctrl+K**

If you want to clear in Command Prompt, press **Ctrl+L**

### Toggle multi-line mode
To enable multi-line mode, press **F3 key**. You can see at bottom of screen if Multiline is on or off.

To use multi-line mode, follow these instruction:

1. Type the beginning of your query.

```sql
SELECT *
```

2. Press **Enter** key and finish our query. You can keep adding lines pressing **Enter** key.

```sql
SELECT *
......FROM "HumanResources"."Department" as hr
```

3. To go back and make changes to your query, navigate with the arrow keys, including up or down.

```sql
SELECT "Name", "DepartmentID"
......FROM "HumanResources"."Department" as hr;
```

4. To execute your multi-line query, add a semi-colon **;** at the end of the last line of your query, then press **Enter** key

```sql
SELECT "Name", "DepartmentID"
......FROM "HumanResources"."Department" as hr;
```

## Environment Variables
Below are a list of environment variables that can be set.
* MSSQL_CLI_SERVER - [Set default server](#set-default-server)
* MSSQL_CLI_DATABASE - [Set default database](#set-default-database)
* MSSQL_CLI_USER - [Set default user](#set-default-user)
* MSSQL_CLI_PASSWORD - [Set default password](#set-default-password)
* MSSQL_CLI_ROW_LIMIT - [Set default row limit](#set-default-row-limit)

**Important: If you are using macOS or Linux, use 'export' instead of 'set'. 'set' is Windows-only.**

### Set default server
Set environment variable MSSQL_CLI_SERVER to set a default SQL Server instance name or address

```bash
set MSSQL_CLI_SERVER=localhost
mssql-cli
```

### Set default database
Set environment variable MSSQL_CLI_DATABASE to set a default database.

```bash
set MSSQL_CLI_DATABASE=AdventureWorks
mssql-cli -S localhost -U sa
```

### Set default user
Set environment variable MSSQL_CLI_USER to set a default user.

```bash
set MSSQL_CLI_USER=sa
mssql-cli -S localhost -d AdventureWorks
```

### Set default password
Set environment variable MSSQL_CLI_PASSWORD to set a default password.

```bash
set MSSQL_CLI_PASSWORD=abc123
mssql-cli -S localhost -d AdventureWorks -U sa
```

### Set default row limit
Set environment variable MSSQL_CLI_ROW_LIMIT to set threshold for row limit prompt. Use 0 to disable prompt.

```bash
set MSSQL_CLI_ROW_LIMIT=10
mssql-cli -S localhost -U sa
```
