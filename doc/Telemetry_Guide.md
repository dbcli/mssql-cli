# Telemetry Guide

By default, Microsoft collects anonymous usage data in order to improve the user experience. The usage data collected allows the team to prioritize features and bug fixes.

Microsoft Privacy statement: https://privacy.microsoft.com/en-us/privacystatement

## Table of Contents
1. [How do we anonymize the data?](#anonymize)
1. [What do we collect](#collect)
2. [How do I opt out?](#opt_out)
3. [Additional Information](#information)


### <a name="anonymize"></a>How do we anonymize data?
Hashed random UUID: a cryptographically (SHA256) anonymous and unique ID per user.

### <a name="collect"></a>What do we collect?
##### Environment
Environment data points give the team insight into commonly used platforms and allow the team to prioritize features, bug fixes, and packaging.
  - Platform name
  - Platform version
  - Target Server edition and version
  - Connection Type (Azure vs. Single Instance)
  - Python version
  - Product version
  - Locale
  - Shell type

##### Measurements
Measurement data points allow the team to be proactive in improving performance.
  - Start time
  - End time
  - Session duration

##### Errors
Abnormal process termination.
- Error flag to indicate type of shutdown.

### <a name="opt_out"></a>How do I opt out?
The mssql-cli Tools telemetry feature is enabled by default. Opt-out of the telemetry feature by setting the ```MSSQL_CLI_TELEMETRY_OPTOUT``` environment variable to ```true``` or ```1```.

##### Windows
```
set MSSQL_CLI_TELEMETRY_OPTOUT=True
```
##### MacOS/Linux (bash)
```
export MSSQL_CLI_TELEMETRY_OPTOUT=True
```

### <a name="information"></a>Additional Information

##### What does the anonymous usage data actually look like?
For those interested, anonymous usage data of the previous session will always be outputted to a telemetry file in the user's configuration directory. It can be found right next to the location of the configuration file.
##### MacOSX & Linux
```
~/.config/mssqlcli/mssqlcli_telemetry.log
```
##### Windows
```
C:\Users\<Username>\AppData\Local\dbcli\mssqlcli\mssqlcli_telemetry.log
```

##### Partial sample of log content
```
  {
    "name": "mssqlcli",
    "properties": {
      "Reserved.SequenceNumber": 1,
      "Reserved.EventId": "e6f0bdab-65b0-4e79-87a4-b05fa514c92d",
      "Reserved.SessionId": "3fa7361c-50ff-4bff-8a55-f22bdc26452d",
      }
  }
```