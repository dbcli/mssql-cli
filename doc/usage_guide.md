# Usage Guide
This article explores mssql-cli features. Click a link below to jump to a specific section:
* [Options](#options)
* [Examples](#examples)
* [Environment Variables](#environment-variables)
* [Special Commands](#special-commands)
* [Non-Interactive Options](#non-interactive-options)
* [Configuration](#configuration)
* [Troubleshooting](#troubleshooting)

## Options
Type `mssql-cli --help` to list supported arguments:

```bash 
$ mssql-cli --help
Usage: main.py [OPTIONS]

optional arguments:
  -h, --help            show this help message and exit
  -U , --username       Username to connect to the database
  -P , --password       If not supplied, defaults to value in environment
                        variable MSSQL_CLI_PASSWORD.
  -d , --database       database name to connect to.
  -S , --server         SQL Server instance name or address.
  -E, --integrated      Use integrated authentication on windows.
  -v, --version         Version of mssql-cli.
  --mssqlclirc          Location of mssqlclirc config file.
  --row-limit           Set threshold for row limit prompt. Use 0 to disable
                        prompt.
  --less-chatty         Skip intro on startup and goodbye on exit.
  --auto-vertical-output
                        Automatically switch to vertical output mode if the
                        result is wider than the terminal width.
  -N, --encrypt         SQL Server uses SSL encryption for all data if the
                        server has a certificate installed.
  -C, --trust-server-certificate
                        The channel will be encrypted while bypassing walking
                        the certificate chain to validate trust.
  -l , --connect-timeout 
                        Time in seconds to wait for a connection to the server
                        before terminating request.
  -K , --application-intent 
                        Declares the application workload type when connecting
                        to a database in a SQL Server Availability Group.
  -M, --multi-subnet-failover
                        If application is connecting to AlwaysOn AG on
                        different subnets, setting this provides faster
                        detection and connection to currently active server.
  -a , --packet-size    Size in bytes of the network packets used to
                        communicate with SQL Server.
  -A, --dac-connection  Connect to SQL Server using the dedicated
                        administrator connection.
  -Q , --query          Executes a query outputting the results to stdout and
                        exits.
  -i , --input_file     Specifies the file that contains a batch of SQL
                        statements for processing.
  -o , --output_file    Specifies the file that receives output from a query.
  --enable-sqltoolsservice-logging
                        Enables diagnostic logging for the SqlToolsService.
  --prompt              Prompt format (Default: \d>
```
      
## Examples
Below are example commands that run against the AdventureWorks database in a localhost server instance. Here is a list of examples:

 * [Connect to a Server](#connect-to-a-server)
 * [Exit mssql-cli](#exit-mssql-cli)
 * [Navigate Multiple Pages of Query Result](#navigate-multiple-pages-of-query-result)
 * [Quit a Query](#quit-a-query)
 * [Clear Screen](#clear-screen)
 * [Toggle Multi-Line Mode](#toggle-multi-line-mode)

### Connect to a Server
Connect to a server, a specific database, and with a username. -S -d and -U are optional. You can [set environment variables](#Environment-Variables) to set default settings.

```bash
mssql-cli -S localhost -d AdventureWorks -U sa
```

### Exit mssql-cli 
Press **Ctrl+D** or type `quit`.

### Navigate Multiple Pages of Query Result
If you select a table that has many rows, it may display the results in multiple pages.

- Press **Enter** key to see one row at a time.
- Press **Space** to see one page at a time.
- Press **q** to escape from the result view.

### Quit a Query
If you are in the middle of writing a query and would like to cancel it, press **Ctrl+C**

### Clear Screen
If you want to clear the Terminal view, press **Ctrl+K**

If you want to clear in Command Prompt, press **Ctrl+L**

### Toggle Multi-Line Mode
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
......FROM "HumanResources"."Department" as hr
```

4. To execute your multi-line query, add **GO** on a new-line, then press **Enter** key

```sql
SELECT "Name", "DepartmentID"
......FROM "HumanResources"."Department" as hr
......GO
```

## Environment Variables
Below are a list of environment variables that can be set.
* MSSQL_CLI_SERVER - [Set Default Server](#set-default-server)
* MSSQL_CLI_DATABASE - [Set Default Database](#set-default-database)
* MSSQL_CLI_USER - [Set Default User](#set-default-user)
* MSSQL_CLI_PASSWORD - [Set Default Password](#set-default-password)
* MSSQL_CLI_ROW_LIMIT - [Set Default Row Limit](#set-default-row-limit)

**Important: If you are using macOS or Linux, use 'export' instead of 'set'. 'set' is Windows-only.**

### Set Default Server
Set environment variable MSSQL_CLI_SERVER to set a default SQL Server instance name or address

```bash
set MSSQL_CLI_SERVER=localhost
mssql-cli
```

### Set Default Database
Set environment variable MSSQL_CLI_DATABASE to set a default database.

```bash
set MSSQL_CLI_DATABASE=AdventureWorks
mssql-cli -S localhost -U sa
```

### Set Default User
Set environment variable MSSQL_CLI_USER to set a default user.

```bash
set MSSQL_CLI_USER=sa
mssql-cli -S localhost -d AdventureWorks
```

### Set Default Password
Set environment variable MSSQL_CLI_PASSWORD to set a default password.

```bash
set MSSQL_CLI_PASSWORD=abc123
mssql-cli -S localhost -d AdventureWorks -U sa
```

### Set Default Row Limit
Set environment variable MSSQL_CLI_ROW_LIMIT to set threshold for row limit prompt. Use 0 to disable prompt.

```bash
set MSSQL_CLI_ROW_LIMIT=10
mssql-cli -S localhost -U sa
```

## Special Commands
Special commands are meant to make your life easier. They are shortcuts to a lot of commonly performed tasks and queries.
Moreover you can save your own commonly used queries as shortcuts. 

All special commands start with a backslash ('\\') and doing so will bring up an autocomplete with all special commands and their descriptions. 

For more help simply type '\\?' inside the mssql-cli prompt to list all the special commands, their usage and description.

```bash
mssql-cli>\?
```

Here are a few examples:

### Example 1: List Tables
Show all tables which contain foo in their names:
```bash
mssql-cli>\lt foo
```
For verbose output:
```bash
mssql-cli>\lt+ foo
```


### Example 2: Named Queries
Save 'select * from HumanResources.Department' as a named query called 'dept':
```bash
mssql-cli>\sn dept select * from "HumanResources"."Department"
```
Run the named query:
```bash
mssql-cli>\n dept
```

You can even add parameters to your saved query:
```bash
mssql-cli>\sn dept select * from "HumanResources"."Department" where "Name" like '%$1%'
```
Run the named query 'dept' with a parameter:
```bash
mssql-cli>\n dept Human
```

### Full list of Special Commands
Below table summarizes the special commands supported

| Command | Usage | Description
| --- | --- | --- |
|\d   | \d OBJECT                        | List or describe database objects. Calls sp_help.
|\dn  | \dn [name]                       | Delete a named query.                            
|\e   | \e [file]                        | Edit the query with external editor.             
|\ld  | \ld[+] [pattern]                 | List databases.                                  
|\lf  | \lf[+] [pattern]                 | List functions.                                  
|\li  | \li[+] [pattern]                 | List indexes.                                    
|\ll  | \ll[+] [pattern]                 | List logins and associated roles.                                
|\ls  | \ls[+] [pattern]                 | List schemas.                                    
|\lt  | \lt[+] [pattern]                 | List tables.                                     
|\lv  | \lv[+] [pattern]                 | List views.      
|\n   | \n[+] [name] [param1 param2 ...] | List or execute named queries.                                   
|\sf  | \sf FUNCNAME                     | Show a function's definition.                    
|\sn  | \sn name query                   | Save a named query.                              
|help | \?                               | Show this help.                                  

## Non-Interactive Options
Non-interactive mode is a great way to query SQL Server using `mssql-cli` without needing to jump into an interactive command-line interface.

### Executing a Query in Non-Interactive Mode
`mssql-cli` supports the following options for query exection in non-interactive mode:

**Note:** Ensure a connection to your server is established using the `-S`, `-U`, `-P`, and `-d` arguments, or by specifying your [environment variables](#environment-variables).

#### -Q, --query
To make a query in non-interactive mode, use the `-Q` (or `--query`) argument, followed by a T-SQL statement surrounded in double or single quotes. sqlcmd syntax is also supported.

#### -i, --input-file
An input file using T-SQL or sqlcmd syntax may be specified as an alternative to using `-Q`.

### Outputting a Query Execution in Non-Interactive Mode
If no argument is specified, the output of a query execution in non-interactive mode prints to standard output. Results may also be printed to a file using the [non-interactive output file argument](#-o---output_file).

#### -o, --output_file
To print the results of your [non-interactive query](#executing-a-query-in-non-interactive-mode) to a file, add the `-o` (or `--output_file`) argument followed by a file path surrounded by double or single quotes. `mssql-cli` will create a file if the specified value does not exist. **Using `-o` will overwrite any existing file.**

**Note:** `-Q`/`--query` or `-i`/`--input-file` is required.

## Configuration
Customization and persistence of settings can be achieved with a config file, whose path can be passed as the `--mssqlclirc <file>` command line argument. Otherwise it is read from the default path `~/.config/mssqlcli/config` on macOS and Linux, and `%LOCALAPPDATA%\dbcli\mssqlcli\config` on Windows. See the [config file](https://github.com/dbcli/mssql-cli/blob/master/mssqlcli/mssqlclirc) itself for a description of all available options.

## Troubleshooting
If you encounter any issues, see the [troubleshooting](troubleshooting_guide.md) section for known issues and workarounds.