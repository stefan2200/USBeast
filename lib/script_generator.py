from lib import utils
import os


#  gets list of scripts from folder, custom script names may be supplied
def get_scripts(scripts_folder="scripts", names=[]):
    scripts = []
    if names == []:
        scripts = [x for x in os.listdir(scripts_folder)]
    else:
        scripts = names
    output = {}
    for script in scripts:
        with open(os.path.join(scripts_folder, script), 'r') as f:
            script_data = f.read()
            temp_var = utils.random_string(10)
            script_data = script_data.replace('{var}', temp_var)
            output[script] = [script_data, temp_var]
    return output


#  creates final payload + result var from executed commands
def pre_process_output(commands, output_type="script_name", debug=False):
    output = ""
    temp_var = utils.random_string(5)
    after_process = '$%s = "Output>"' % temp_var

    for c in commands:
        command, var = commands[c]
        if not command.endswith(";"):
            command += ";"
        output += command
        if output_type == "script_name":
            after_process += ' + "`n%s: " + $%s' % (c.replace('.script', ''), var)
        if output_type == "script":
            after_process += ' + "`n%s: " + $%s' % (c, var)
    after_process += ";"
    if debug:
        after_process += "Out-File -FilePath debug.txt -InputObject $%s;" % temp_var
    return output, after_process, temp_var

