import rich_click as click

from .global_config import GLOBAL_CONFIG


class CommandSupportsAddingHelpTextToItsArguments(click.RichCommand):
    """
    this class should be used with `class ArgumentSupportsAddingHelpText`.
    """
    
    def format_help(self, ctx, formatter):
        return self.rich_format_help(self, ctx, formatter)
    
    # noinspection PyProtectedMember,PyPep8Naming,PyUnusedLocal,PyTypeChecker
    # noinspection PyAssignmentToLoopOrWithParameter,PyUnresolvedReferences
    @staticmethod
    def rich_format_help(obj, ctx, formatter):
        """
        warning:
            this is a dirty hack.
            we copied the source code from `rich_click/rich_click.py :
            rich_format_help`, and modified its 318th and 331th line (note:
            rich-click v1.2.1).
            
            before modification (line 318):
                if type(param) is click.core.Argument and not SHOW_ARGUMENTS:
            after:
                if isinstance(param, click.core.Argument) and not SHOW_ARGUMENTS:
                
            before modification (line 331):
                if type(param) is click.core.Argument and not GROUP_ARGUMENTS_OPTIONS:
            after:
                if isinstance(param, click.core.Argument) and not GROUP_ARGUMENTS_OPTIONS:
            
            finally we put the modified version here.
        """
        from rich_click.rich_click import (
            ALIGN_COMMANDS_PANEL,
            ALIGN_OPTIONS_PANEL,
            ARGUMENTS_PANEL_TITLE,
            COMMAND_GROUPS,
            COMMANDS_PANEL_TITLE,
            COLOR_SYSTEM,
            FOOTER_TEXT,
            GROUP_ARGUMENTS_OPTIONS,
            HEADER_TEXT,
            MAX_WIDTH,
            OPTION_GROUPS,
            OPTIONS_PANEL_TITLE,
            RANGE_STRING,
            REQUIRED_SHORT_STRING,
            SHOW_ARGUMENTS,
            STYLE_COMMANDS_PANEL_BORDER,
            STYLE_FOOTER_TEXT,
            SHOW_METAVARS_COLUMN,
            STYLE_HEADER_TEXT,
            STYLE_METAVAR,
            STYLE_OPTION,
            STYLE_OPTIONS_PANEL_BORDER,
            STYLE_REQUIRED_SHORT,
            STYLE_SWITCH,
            STYLE_USAGE,
            STYLE_USAGE_COMMAND,
            USE_CLICK_SHORT_HELP,
            Align, Console, Padding, Panel, Table, Text, Theme,
            highlighter,
            _get_help_text,
            _get_parameter_help,
            _make_command_help,
            _make_rich_rext,
        )
        
        # override some styles by our own.
        # (copied from `./click.py : line 13-15`.)
        SHOW_ARGUMENTS = True
        STYLE_COMMANDS_PANEL_BORDER = 'magenta'
        
        # ---------------------------------------------------------------------
        
        console = Console(
            theme=Theme(
                {
                    "option" : STYLE_OPTION,
                    "switch" : STYLE_SWITCH,
                    "metavar": STYLE_METAVAR,
                    "usage"  : STYLE_USAGE,
                }
            ),
            highlighter=highlighter,
            color_system=COLOR_SYSTEM,
        )
        
        # Header text if we have it
        if HEADER_TEXT:
            console.print(
                Padding(_make_rich_rext(HEADER_TEXT, STYLE_HEADER_TEXT), (1, 1, 0, 1))
            )
        
        # Print usage
        console.print(
            Padding(highlighter(obj.get_usage(ctx)), 1), style=STYLE_USAGE_COMMAND
        )
        
        # Print command / group help if we have some
        if obj.help:
            # Print with a max width and some padding
            console.print(
                Padding(
                    Align(_get_help_text(obj), width=MAX_WIDTH, pad=False),
                    (0, 1, 1, 1),
                )
            )
        
        # Look through OPTION_GROUPS for this command
        # stick anything unmatched into a default group at the end
        option_groups = OPTION_GROUPS.get(ctx.command_path, []).copy()
        option_groups.append({"options": []})
        argument_groups = {"name": ARGUMENTS_PANEL_TITLE, "options": []}
        for param in obj.get_params(ctx):
            
            # Skip positional arguments - they don't have opts or helptext and are covered in usage
            # See https://click.palletsprojects.com/en/8.0.x/documentation/#documenting-arguments
            if isinstance(param, click.core.Argument) and not SHOW_ARGUMENTS:  # LKEDIT
                continue
            
            # Skip if option is hidden
            if getattr(param, "hidden", False):
                continue
            
            # Already mentioned in a config option group
            for option_group in option_groups:
                if any([opt in option_group.get("options", []) for opt in param.opts]):
                    break
            # No break, no mention - add to the default group
            else:
                if isinstance(param, click.core.Argument) and not GROUP_ARGUMENTS_OPTIONS:  # LKEDIT
                    argument_groups["options"].append(param.opts[0])
                else:
                    option_groups[-1]["options"].append(param.opts[0])
        
        # If we're not grouping arguments and we got some, prepend before default options
        if len(argument_groups["options"]) > 0:
            option_groups.insert(len(option_groups) - 1, argument_groups)
        
        # Print each option group panel
        for option_group in option_groups:
            
            options_rows = []
            for opt in option_group.get("options", []):
                
                # Get the param
                for param in obj.get_params(ctx):
                    if any([opt in param.opts]):
                        break
                # Skip if option is not listed in this group
                else:
                    continue
                
                # Short and long form
                opt_long_strs = []
                opt_short_strs = []
                for idx, opt in enumerate(param.opts):
                    opt_str = opt
                    if param.secondary_opts and idx in param.secondary_opts:
                        opt_str += "/" + param.secondary_opts[idx]
                    if "--" in opt:
                        opt_long_strs.append(opt_str)
                    else:
                        opt_short_strs.append(opt_str)
                
                # Column for a metavar, if we have one
                metavar = Text(style=STYLE_METAVAR)
                metavar_str = param.make_metavar()
                # Do it ourselves if this is a positional argument
                if type(param) is click.core.Argument and metavar_str == param.name.upper():
                    metavar_str = param.type.name.upper()
                # Skip booleans
                if metavar_str != "BOOLEAN":
                    metavar.append(metavar_str)
                
                try:
                    if (
                            isinstance(param.type, click.types._NumberRangeBase)
                            # skip count with default range type
                            and not (param.count and
                                     param.type.min == 0 and
                                     param.type.max is None)
                    ):
                        range_str = param.type._describe_range()
                        if range_str:
                            metavar.append(RANGE_STRING.format(range_str))
                except AttributeError:
                    # click.types._NumberRangeBase is only in Click 8x onwards
                    pass
                
                # Required asterisk
                required = ""
                if param.required:
                    required = Text(REQUIRED_SHORT_STRING, style=STYLE_REQUIRED_SHORT)
                
                rows = [
                    required,
                    highlighter(highlighter(",".join(opt_long_strs))),
                    highlighter(highlighter(",".join(opt_short_strs))),
                    metavar,
                    _get_parameter_help(param, ctx),
                ]
                
                # Remove metavar if specified in config
                if not SHOW_METAVARS_COLUMN:
                    rows.pop(3)
                
                options_rows.append(rows)
            
            if len(options_rows) > 0:
                options_table = Table(highlight=True, box=None, show_header=False)
                # Strip the required column if none are required
                if all([x[0] == "" for x in options_rows]):
                    options_rows = [x[1:] for x in options_rows]
                for row in options_rows:
                    options_table.add_row(*row)
                console.print(
                    Panel(
                        options_table,
                        border_style=STYLE_OPTIONS_PANEL_BORDER,
                        title=option_group.get("name", OPTIONS_PANEL_TITLE),
                        title_align=ALIGN_OPTIONS_PANEL,
                        width=MAX_WIDTH,
                    )
                )
        
        #
        # Groups only:
        # List click command groups
        #
        if hasattr(obj, "list_commands"):
            # Look through COMMAND_GROUPS for this command
            # stick anything unmatched into a default group at the end
            cmd_groups = COMMAND_GROUPS.get(ctx.command_path, []).copy()
            cmd_groups.append({"commands": []})
            for command in obj.list_commands(ctx):
                for cmd_group in cmd_groups:
                    if command in cmd_group.get("commands", []):
                        break
                else:
                    cmd_groups[-1]["commands"].append(command)
            
            # Print each command group panel
            for cmd_group in cmd_groups:
                commands_table = Table(highlight=False, box=None, show_header=False)
                # Define formatting in first column, as commands don't match highlighter regex
                commands_table.add_column(style="bold cyan", no_wrap=True)
                for command in cmd_group.get("commands", []):
                    # Skip if command does not exist
                    if command not in obj.list_commands(ctx):
                        continue
                    cmd = obj.get_command(ctx, command)
                    # Use the truncated short text as with vanilla text if requested
                    if USE_CLICK_SHORT_HELP:
                        helptext = cmd.get_short_help_str()
                    else:
                        # Use short_help function argument if used, or the full help
                        helptext = cmd.short_help or cmd.help or ""
                    commands_table.add_row(command, _make_command_help(helptext))
                if commands_table.row_count > 0:
                    console.print(
                        Panel(
                            commands_table,
                            border_style=STYLE_COMMANDS_PANEL_BORDER,
                            title=cmd_group.get("name", COMMANDS_PANEL_TITLE),
                            title_align=ALIGN_COMMANDS_PANEL,
                            width=MAX_WIDTH,
                        )
                    )
        
        # Epilogue if we have it
        if obj.epilog:
            # Remove single linebreaks, replace double with single
            lines = obj.epilog.split("\n\n")
            epilogue = "\n".join([x.replace("\n", " ").strip() for x in lines])
            console.print(
                Padding(Align(highlighter(epilogue), width=MAX_WIDTH, pad=False), 1)
            )
        
        # Footer text if we have it
        if FOOTER_TEXT:
            console.print(
                Padding(_make_rich_rext(FOOTER_TEXT, STYLE_FOOTER_TEXT), (1, 1, 0, 1))
            )


class DoNotSortCommands(click.RichGroup):
    """
    references:
        https://stackoverflow.com/questions/47972638/how-can-i-define-the-order
            -of-click-sub-commands-in-help

    usage:
        @click.group(cls=DoNotSortCommandsAddingOrder)
        def cli():
            ...
    """
    _raw_order = {}  # dict[str cmd_name, int order]
    
    def command(self, *args, **kwargs):
        def decorator(func):
            order = kwargs.pop('cmd_order', len(self._raw_order) + 1000)
            #   ... + 1000: make sure the auto generated order is always higher
            #       than user defined.
            cmd = super(DoNotSortCommands, self).command(
                *args, **kwargs)(func)
            self._raw_order[cmd.name] = order
            return cmd
        
        return decorator
    
    def list_commands(self, ctx):
        if GLOBAL_CONFIG.DO_NOT_SORT_COMMANDS:
            return sorted(super().list_commands(ctx),
                          key=lambda name: self._raw_order[name])
        else:
            return super().list_commands(ctx)


class ArgumentSupportsAddingHelpText(click.Argument):
    """
    references:
        https://github.com/ewels/rich-click/issues/11
    """
    
    def __init__(self, param_decls, required=None, **attrs) -> None:
        self.help = attrs.pop('help', None)
        super().__init__(param_decls, required, **attrs)
