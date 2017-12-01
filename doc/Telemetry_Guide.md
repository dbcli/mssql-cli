# Telemetry Disclosure

By default, Microsoft collects anonymous usage data in order to improve the user experience. The usage data collected allows the team to prioritize features and bug fixes.

## Table of Contents
1. [What do we collect](#collect)
2. [How do I opt out?](#opt_out)
3. [Additional Information](#information)


#### <a name="collect"></a>What do we collect?
A unique user ID is sent with each telemetry event for the purpose of counting distinct users and correlating errors or exceptions. It does not contain any personally identifiable information nor can it be used to find any personal information.

  - SHA256 Hashed Mac address
  
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
Error data points allow the team to be proactive in troubleshooting and fixing common issues/exceptions.
- Exceptions

### <a name="opt_out"></a>How do I opt out?
Users can opt out of anonymous data collection by setting the following option in the configuration file:
##### Example configuration file
```
[main]

# Allows Microsoft to collect anonymous usage data.
# Setting this option to False opts out usage data collection.
collect_telemetry = False
```
The configuration file can be found at the following location:
##### MacOSX & Linux
```
~/.config/mssqlcli/
```
##### Windows
```
C:\Users\<Username>\AppData\Local\dbcli\mssqlcli\
```

### <a name="information"></a>Additional Information

##### What does the anonymous usage data actually look like?
For those interested, anonymous usage data of the previous session will always be outputted to a telemetry file in the user's configuration directory. It can be found right next to the location of the configuration file.
**Note**: The data in this file is sent to Microsoft, **IF** the collect_telemetry  option is set to **True**.
##### MacOSX & Linux
```
~/.config/mssqlcli/mssqlcli_telemetry.log
```
##### Windows
```
C:\Users\<Username>\AppData\Local\dbcli\mssqlcli\mssqlcli_telemetry.log
```
