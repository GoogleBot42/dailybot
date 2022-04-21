# coding=utf-8

# Help Module for drastikbot modules.
#
# This module provides help messages for the loaded drastikbot modules.
#
# Usage
# -----
# Calling the command without arguments returns a list of all the
# loaded modules with help information.  Example: .help
#
# Giving the name of a module as an argument returns the available
# bot_commands of that module.  Example: .help text
#
# Giving the name of a module followed by one of its bot_commands
# returns a help message of that command:  Example: .help text ae
#
# API
# ---
# To  provide help  messages through  this module  other modules  must
# include  the manual  variable  in  their Module  class.  If no  such
# variable is provided the module will be unlisted.


# Copyright (C) 2021 drastik.org
#
# This file is part of drastikbot.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, version 3 only.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import itertools


class Module:
    def __init__(self):
        self.commands = ["help"]


def get_module_object(i, module_name):
    # drastikbot v2.2
    if hasattr(i, "mod"):
        for mod_object, mod_path in i.mod["modules_d"].values():
            if mod_path.stem == module_name:
                return mod_object

    # drastikbot v2.1
    if hasattr(i, "modules") and module_name in i.modules:
        return i.modules[module_name]

    return None


def hidden_status(i, module_name: str) -> bool:
    """Is ``module'' a hidden module?"""

    module_object = get_module_object(i, module_name)
    if module_object is None:
        return True  # Module not found

    if not hasattr(module_object, "Module"):
        return True  # No Module class, it's hidden

    if hasattr(module_object.Module(), "manual"):
        return module_object.Module().manual
    elif hasattr(module_object.Module(), "helpmsg"):  # Old method
        if "__hidden__" in  module_object.Module().helpmsg:
            return "hidden"


def is_hidden(i, module_name):
    return hidden_status(i, module_name) == "hidden"


def module_checks(i, irc, module):
    if module not in i.modules.keys():
        irc.notice(i.channel, f"Help: `{module}' is not an imported module.")
        return False

    try:
        module_bl = irc.var.modules_obj["blacklist"][module]
        if module_bl and i.channel in module_bl:
            irc.notice(i.channel, f"Help: This module has been disabled.")
            return False
    except KeyError:
        pass  # No blacklist, move on

    try:
        module_wl = irc.var.modules_obj["whitelist"][module]
        if module_wl and i.channel not in module_wl:
            irc.notice(i.channel, f"Help: This module has been disabled.")
            return False
    except KeyError:
        pass  # No whitelist, move on

    module_c = i.modules[module].Module()
    if not hasattr(module_c, "manual"):
        irc.notice(i.channel, "Help: This module does not have a manual.")
        return False

    return True

def module_help(i, irc, module):
    if not module_checks(i, irc, module):
        return

    module_c = i.modules[module].Module()

    commands = ""
    if hasattr(module_c, "commands"):
        commands = ", ".join(module_c.commands)
        commands = f"Commands: {commands} | "

    info = ""
    if "desc" in module_c.manual:
        info = module_c.manual["desc"]
        info = f"Info: {info}"

    t = f"\x0311{module}\x0F: {commands}{info}"
    t += f" | Use: {i.cmd_prefix}help <module> <command> for command info."
    irc.notice(i.channel, t)


def command_help(i, irc, module, command):
    if not module_checks(i, irc, module):
        return

    module_c = i.modules[module].Module()

    if not hasattr(module_c, "commands"):
        irc.notice(i.channel, "Help: This module does not provide commands.")
        return

    if "bot_commands" not in module_c.manual:
        irc.notice(i.channel, "Help: No manual entry for this command ")
        return

    command_manual = module_c.manual["bot_commands"]

    if command not in command_manual:
        irc.notice(i.channel, "Help: No manual entry for this command.")
        return

    command_entry = command_manual[command]

    t = []

    if "usage" in command_entry:
        usage = command_entry["usage"](i.cmd_prefix)
        usage = f"Usage: {usage}"
        t.append(usage)

    if "info" in command_entry:
        info = command_entry["info"]
        info = f"Info: {info}"
        t.append(info)

    if "alias" in command_entry:
        alias = ", ".join(command_entry["alias"])
        alias = f"Aliases: {alias}"
        t.append(alias)

    t = " | ".join(t)
    t = f"{command}: {t}"
    irc.notice(i.channel, t)


def module_list(i, irc):
    m1 = filter(lambda x: not is_hidden(i, x) and i.whitelist(x, i.channel) \
                          and not i.blacklist(x, i.channel),
               set(i.command_dict.values()))
    m2 = filter(lambda x: not is_hidden(i, x) and i.whitelist(x, i.channel) \
                          and not i.blacklist(x, i.channel) and not x in m1,
               i.auto_list)
    m = itertools.chain(m1, m2)
    t = "Help: " + ", ".join(sorted(m))
    t += f" | Use: {i.cmd_prefix}help <module> for module info."
    irc.notice(i.channel, t)


def main(i, irc):
    if i.msg_nocmd:
        argv = i.msg_nocmd.split()
        argc = len(argv)
        if argc == 1:
            module_help(i, irc, argv[0])
        elif argc == 2:
            command_help(i, irc, argv[0], argv[1])
        else:
            m = f"Usage: {i.cmd_prefix}help [module] [command]"
            irc.notice(i.channel, m)
    else:
        module_list(i, irc)
