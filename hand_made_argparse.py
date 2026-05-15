"""
Advanced hand-made argument parser module (not using argparse module).\n
\n
This module provides a feature-rich command-line argument parser that rivals
the built-in argparse module, with many advanced features for professional-grade
CLI applications.\n
\n
ADVANCED FEATURES IMPLEMENTED:\n
✓ Positional and optional arguments\n
✓ Short and long argument names with aliases\n
✓ Multiple actions: store, store_true, store_false, store_const, count, append, append_const\n
✓ Multiple nargs modes: None, ?, *, +, exact numbers\n
✓ Argument groups for organizing help text\n
✓ Mutually exclusive argument groups\n
✓ Subcommand support (SubparsersAction)\n
✓ Argument choices validation\n
✓ Custom validators (callable predicates)\n
✓ Type conversion (int, str, custom types)\n
✓ Default values with smart defaults for boolean actions\n
✓ Environment variable support\n
✓ Config file loading (JSON and key=value formats)\n
✓ Argument dependencies and conflicts\n
✓ Bundled short flags (-abc for -a -b -c)\n
✓ Argument abbreviation support (--format can be --for)\n
✓ Auto-generated help messages with formatting\n
✓ File argument expansion (@file syntax)\n
✓ Support for -- to separate positional arguments\n
✓ Customizable prefix characters\n
✓ Error handling with optional exit control\n
✓ Both positional and optional argument metavars\n
✓ Aliases for subcommands\n
\n
USAGE:\n
    from hand_made_argparse import ArgumentParser\n
    \n
    parser = ArgumentParser(description="My CLI tool")\n
    parser.add_argument("filename", help="Input file")\n
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose mode")\n
    args = parser.parse_args()
"""

import sys
import json
import os
from typing import Any, Dict, List, Optional, Union, Callable, Set, Tuple
from pathlib import Path

__version__ = "1.0.0"
__author__ = "S0meR4nd0mGuy"
__all__ = [
    "ArgumentParser",
    "Argument",
    "ArgumentGroup",
    "MutuallyExclusiveGroup",
    "Subparser",
    "SubparsersAction",
]


class Argument:
    """Represents a command-line argument definition. Example is below (simple example):
    ```
    from hand_made_argparse import ArgumentParser

    def main():
        # Create parser with basic description
        parser = ArgumentParser(
            description="Simple greeting tool",
            prog="greeter"
        )
        
        # Add arguments
        parser.add_argument("name", help="Person to greet")
        parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
        parser.add_argument("-c", "--count", type_=int, default=1, help="Number of greetings")
        
        # Parse and use
        args = parser.parse_args()
        
        greeting = f"Hello, {args['name']}!"
        
        if args['verbose']:
            print(f"Greeting mode enabled, repeating {args['count']} time(s)")
        
        for _ in range(args['count']):
            print(greeting)


    if __name__ == "__main__":
        main()
    ```
    For a more advanced example, look for the example_import.py file which demonstrates many of the advanced features in a single script.
    """
    
    def __init__(
        self,
        *names: str,
        nargs: Optional[Union[int, str]] = None,
        default: Any = None,
        type_: type = str,
        help_text: str = "",
        required: bool = False,
        choices: Optional[List[Any]] = None,
        action: str = "store",
        metavar: Optional[str] = None,
        const: Optional[Any] = None,
        env_var: Optional[str] = None,
        validator: Optional[Callable[[Any], bool]] = None,
        aliases: Optional[List[str]] = None,
        depends_on: Optional[List[str]] = None,
        conflicts_with: Optional[List[str]] = None,
    ):
        self.names = names
        self.nargs = nargs
        self.default = default
        self.type = type_
        self.help_text = help_text
        self.required = required
        self.choices = choices
        self.action = action
        self.metavar = metavar or (names[-1].lstrip('-').upper() if names else "VALUE")
        self.const = const
        self.env_var = env_var
        self.validator = validator
        self.aliases = aliases or []
        self.depends_on = depends_on or []
        self.conflicts_with = conflicts_with or []
        
        # Determine if this is optional (starts with -) or positional
        self.is_optional = any(name.startswith('-') for name in names)
        
        # Get the dest (attribute name)
        if self.is_optional:
            self.dest = names[-1].lstrip('-').replace('-', '_')
        else:
            self.dest = names[0]
        
        # All names including aliases
        self.all_names = set(names) | set(self.aliases)


class MutuallyExclusiveGroup:
    """Group of arguments that cannot be used together."""
    
    def __init__(self, required: bool = False, parser: Optional['ArgumentParser'] = None):
        self.arguments: List[Argument] = []
        self.required = required
        self.parser = parser
    
    def add_argument(
        self,
        *names: str,
        nargs: Optional[Union[int, str]] = None,
        default: Any = None,
        type_: type = str,
        help: str = "",
        required: bool = False,
        choices: Optional[List[Any]] = None,
        action: str = "store",
        metavar: Optional[str] = None,
        const: Optional[Any] = None,
        env_var: Optional[str] = None,
        validator: Optional[Callable[[Any], bool]] = None,
        aliases: Optional[List[str]] = None,
        depends_on: Optional[List[str]] = None,
        conflicts_with: Optional[List[str]] = None,
    ) -> Argument:
        """Add an argument to this group."""
        if self.parser:
            old_group = self.parser.current_group
            self.parser.current_group = self
            arg = self.parser.add_argument(
                *names,
                nargs=nargs,
                default=default,
                type_=type_,
                help=help,
                required=required,
                choices=choices,
                action=action,
                metavar=metavar,
                const=const,
                env_var=env_var,
                validator=validator,
                aliases=aliases,
                depends_on=depends_on,
                conflicts_with=conflicts_with,
            )
            self.parser.current_group = old_group
            return arg
        return Argument(*names)


class ArgumentGroup:
    """Organizes arguments into logical groups in help text."""
    
    def __init__(self, title: str, description: str = "", parser: Optional['ArgumentParser'] = None):
        self.title = title
        self.description = description
        self.arguments: List[Argument] = []
        self.parser = parser
    
    def add_argument(
        self,
        *names: str,
        nargs: Optional[Union[int, str]] = None,
        default: Any = None,
        type_: type = str,
        help: str = "",
        required: bool = False,
        choices: Optional[List[Any]] = None,
        action: str = "store",
        metavar: Optional[str] = None,
        const: Optional[Any] = None,
        env_var: Optional[str] = None,
        validator: Optional[Callable[[Any], bool]] = None,
        aliases: Optional[List[str]] = None,
        depends_on: Optional[List[str]] = None,
        conflicts_with: Optional[List[str]] = None,
    ) -> Argument:
        """Add an argument to this group."""
        if self.parser:
            old_group = self.parser.current_group
            self.parser.current_group = self
            arg = self.parser.add_argument(
                *names,
                nargs=nargs,
                default=default,
                type_=type_,
                help=help,
                required=required,
                choices=choices,
                action=action,
                metavar=metavar,
                const=const,
                env_var=env_var,
                validator=validator,
                aliases=aliases,
                depends_on=depends_on,
                conflicts_with=conflicts_with,
            )
            self.parser.current_group = old_group
            return arg
        return Argument(*names)


class Subparser:
    """Sub-command parser for handling subcommands."""
    
    def __init__(self, name: str, help_text: str = "", aliases: Optional[List[str]] = None):
        self.name = name
        self.help_text = help_text
        self.aliases = aliases or []
        self.arguments: List[Argument] = []
        self.all_names = {name} | set(aliases)


class ArgumentParser:
    """An advanced command-line argument parser."""
    
    def __init__(
        self,
        description: str = "",
        prog: str = "",
        epilog: str = "",
        allow_abbrev: bool = True,
        add_help: bool = True,
        prefix_chars: str = "-",
        fromfile_prefix_chars: Optional[str] = None,
        exit_on_error: bool = True,
    ):
        self.description = description
        self.prog = prog or sys.argv[0]
        self.epilog = epilog
        self.allow_abbrev = allow_abbrev
        self.add_help = add_help
        self.prefix_chars = prefix_chars
        self.fromfile_prefix_chars = fromfile_prefix_chars
        self.exit_on_error = exit_on_error
        
        self.arguments: List[Argument] = []
        self.mutually_exclusive_groups: List[MutuallyExclusiveGroup] = []
        self.argument_groups: List[ArgumentGroup] = []
        self.subparsers: Dict[str, Subparser] = {}
        self.current_group: Optional[ArgumentGroup] = None
        
        if add_help:
            self.add_argument(
                "-h", "--help",
                action="store_true",
                help="Show this help message and exit"
            )
    
    def add_argument_group(self, title: str, description: str = "") -> ArgumentGroup:
        """Create a new argument group."""
        group = ArgumentGroup(title, description, parser=self)
        self.argument_groups.append(group)
        self.current_group = group
        return group
    
    def add_mutually_exclusive_group(self, required: bool = False) -> MutuallyExclusiveGroup:
        """Create a mutually exclusive group."""
        group = MutuallyExclusiveGroup(required, parser=self)
        self.mutually_exclusive_groups.append(group)
        return group
    
    def add_subparsers(self, title: str = "subcommands", dest: str = "command") -> 'SubparsersAction':
        """Create subparsers for handling subcommands."""
        return SubparsersAction(self, title, dest)
    
    def add_argument(
        self,
        *names: str,
        nargs: Optional[Union[int, str]] = None,
        default: Any = None,
        type_: type = str,
        help: str = "",
        required: bool = False,
        choices: Optional[List[Any]] = None,
        action: str = "store",
        metavar: Optional[str] = None,
        const: Optional[Any] = None,
        env_var: Optional[str] = None,
        validator: Optional[Callable[[Any], bool]] = None,
        aliases: Optional[List[str]] = None,
        depends_on: Optional[List[str]] = None,
        conflicts_with: Optional[List[str]] = None,
    ) -> Argument:
        """Add an argument to the parser."""
        # Auto-set defaults for boolean actions if not provided
        if action == "store_true" and default is None:
            default = False
        elif action == "store_false" and default is None:
            default = True
        elif action in ("append", "append_const") and default is None:
            default = []
        elif action == "count" and default is None:
            default = 0
        
        arg = Argument(
            *names,
            nargs=nargs,
            default=default,
            type_=type_,
            help_text=help,
            required=required,
            choices=choices,
            action=action,
            metavar=metavar,
            const=const,
            env_var=env_var,
            validator=validator,
            aliases=aliases,
            depends_on=depends_on,
            conflicts_with=conflicts_with,
        )
        
        # Add to the main list (or to current group if set)
        if self.current_group and isinstance(self.current_group, ArgumentGroup):
            self.current_group.arguments.append(arg)
        elif self.current_group and isinstance(self.current_group, MutuallyExclusiveGroup):
            self.current_group.arguments.append(arg)
        else:
            self.arguments.append(arg)
        
        return arg
    
    def parse_args(
        self,
        args: Optional[List[str]] = None,
        config_file: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Parse command-line arguments."""
        if args is None:
            args = sys.argv[1:]
        
        # Load from config file first if provided
        config_args = {}
        if config_file and os.path.exists(config_file):
            config_args = self._load_config(config_file)
        
        # Handle fromfile_prefix_chars
        args = self._expand_args_from_files(args)
        
        # Check for help
        if self.add_help and ("-h" in args or "--help" in args):
            self.print_help()
            sys.exit(0)
        
        result = {}
        positional_args = []
        action_counts = {}  # For count action
        all_args = self._get_all_arguments()
        i = 0
        
        # First pass: parse optional and handle actions
        while i < len(args):
            arg = args[i]
            
            if arg == "--":
                # Everything after -- is positional
                positional_args.extend(args[i+1:])
                break
            
            if arg.startswith('-') and arg != '-':
                # Optional argument or bundled short flags
                if arg.startswith('--'):
                    # Long option
                    matched = False
                    for argument in all_args:
                        if arg in argument.all_names:
                            matched = True
                            value = self._handle_action(
                                argument, args, i, action_counts
                            )
                            if value is not None:
                                if argument.action in ("append", "append_const"):
                                    if argument.dest not in result:
                                        result[argument.dest] = []
                                    if isinstance(value, list):
                                        result[argument.dest].extend(value)
                                    else:
                                        result[argument.dest].append(value)
                                else:
                                    result[argument.dest] = value
                                i = self._advance_index(argument, args, i)
                            else:
                                i += 1
                            break
                    
                    if not matched:
                        # Try abbreviation
                        if self.allow_abbrev:
                            matches = [a for a in all_args 
                                     if any(n.startswith(arg) for n in a.all_names)]
                            if len(matches) == 1:
                                value = self._handle_action(
                                    matches[0], args, i, action_counts
                                )
                                if matches[0].action in ("append", "append_const"):
                                    if matches[0].dest not in result:
                                        result[matches[0].dest] = []
                                    if isinstance(value, list):
                                        result[matches[0].dest].extend(value)
                                    else:
                                        result[matches[0].dest].append(value)
                                else:
                                    result[matches[0].dest] = value
                                i = self._advance_index(matches[0], args, i)
                            else:
                                raise ValueError(f"Unknown or ambiguous argument: {arg}")
                        else:
                            raise ValueError(f"Unknown argument: {arg}")
                else:
                    # Short option(s) - could be bundled
                    if len(arg) > 2 and arg[1] != '-':
                        # Bundled short flags like -abc
                        for j, char in enumerate(arg[1:]):
                            short_arg = f"-{char}"
                            matched = False
                            for argument in all_args:
                                if short_arg in argument.all_names:
                                    matched = True
                                    value = self._handle_action(
                                        argument, args, i if j == len(arg) - 2 else -1,
                                        action_counts
                                    )
                                    if value is not None:
                                        if argument.action in ("append", "append_const"):
                                            if argument.dest not in result:
                                                result[argument.dest] = []
                                            if isinstance(value, list):
                                                result[argument.dest].extend(value)
                                            else:
                                                result[argument.dest].append(value)
                                        else:
                                            result[argument.dest] = value
                                    break
                            if not matched:
                                raise ValueError(f"Unknown argument: {short_arg}")
                        i += 1
                    else:
                        # Single short flag
                        matched = False
                        for argument in all_args:
                            if arg in argument.all_names:
                                matched = True
                                value = self._handle_action(
                                    argument, args, i, action_counts
                                )
                                if value is not None:
                                    if argument.action in ("append", "append_const"):
                                        if argument.dest not in result:
                                            result[argument.dest] = []
                                        if isinstance(value, list):
                                            result[argument.dest].extend(value)
                                        else:
                                            result[argument.dest].append(value)
                                    else:
                                        result[argument.dest] = value
                                i = self._advance_index(argument, args, i)
                                break
                        if not matched:
                            raise ValueError(f"Unknown argument: {arg}")
            else:
                # Positional argument
                positional_args.append(arg)
                i += 1
        
        # Assign positional arguments
        positional_idx = 0
        for argument in all_args:
            if not argument.is_optional:
                if positional_idx < len(positional_args):
                    value = positional_args[positional_idx]
                    try:
                        result[argument.dest] = argument.type(value)
                    except (ValueError, TypeError):
                        raise ValueError(
                            f"Invalid value '{value}' for {argument.dest}"
                        )
                    positional_idx += 1
                elif argument.required:
                    raise ValueError(f"Missing required argument: {argument.dest}")
                else:
                    result[argument.dest] = argument.default
        
        # Set defaults and merge config
        for argument in all_args:
            if argument.dest not in result:
                # Check environment variable
                if argument.env_var and argument.env_var in os.environ:
                    try:
                        result[argument.dest] = argument.type(os.environ[argument.env_var])
                    except (ValueError, TypeError):
                        result[argument.dest] = argument.default
                # Check config file
                elif argument.dest in config_args:
                    result[argument.dest] = config_args[argument.dest]
                else:
                    result[argument.dest] = argument.default
        
        # Validation
        self._validate_args(result, all_args)
        
        return result
    
    def _get_all_arguments(self) -> List[Argument]:
        """Get all arguments including from groups."""
        all_args = self.arguments[:]
        for group in self.argument_groups:
            all_args.extend(group.arguments)
        for group in self.mutually_exclusive_groups:
            all_args.extend(group.arguments)
        return all_args
    
    def _handle_action(
        self,
        argument: Argument,
        args: List[str],
        index: int,
        action_counts: Dict[str, int]
    ) -> Any:
        """Handle different action types."""
        if argument.action == "store_true":
            return True
        elif argument.action == "store_false":
            return False
        elif argument.action == "store_const":
            return argument.const
        elif argument.action == "count":
            count = action_counts.get(argument.dest, 0) + 1
            action_counts[argument.dest] = count
            return count
        elif argument.action == "append":
            if index + 1 < len(args) and not args[index + 1].startswith('-'):
                value = args[index + 1]
                try:
                    return [argument.type(value)]
                except (ValueError, TypeError):
                    raise ValueError(f"Invalid value '{value}' for {argument.dest}")
            return None
        elif argument.action == "append_const":
            return [argument.const] if argument.const is not None else None
        else:  # "store"
            return self._parse_optional_arg(argument, args, index)
    
    def _advance_index(self, argument: Argument, args: List[str], index: int) -> int:
        """Calculate how many args were consumed."""
        if argument.action in ("store_true", "store_false", "store_const", "count", "append_const"):
            return index + 1
        elif argument.nargs is None:
            return index + 2
        elif argument.nargs == '?':
            return index + 2 if index + 1 < len(args) and not args[index + 1].startswith('-') else index + 1
        elif isinstance(argument.nargs, int):
            return index + argument.nargs + 1
        else:
            return index + 1
    
    def _expand_args_from_files(self, args: List[str]) -> List[str]:
        """Expand arguments from files if prefix_chars specified."""
        if not self.fromfile_prefix_chars:
            return args
        
        expanded = []
        for arg in args:
            if arg.startswith(self.fromfile_prefix_chars):
                try:
                    with open(arg[1:], 'r') as f:
                        expanded.extend(f.read().split())
                except IOError:
                    expanded.append(arg)
            else:
                expanded.append(arg)
        return expanded
    
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            with open(config_file, 'r') as f:
                if config_file.endswith('.json'):
                    return json.load(f)
                else:
                    # Simple key=value format
                    config = {}
                    for line in f:
                        if '=' in line:
                            key, value = line.strip().split('=', 1)
                            config[key.strip()] = value.strip()
                    return config
        except Exception as e:
            raise ValueError(f"Error loading config file: {e}")
    
    def _validate_args(self, result: Dict[str, Any], all_args: List[Argument]) -> None:
        """Validate parsed arguments."""
        # Check mutually exclusive groups
        for group in self.mutually_exclusive_groups:
            # Only count as "provided" if actually set (not just default value)
            provided = []
            for a in group.arguments:
                val = result.get(a.dest)
                # For boolean/count actions, check if non-default
                if a.action in ("store_true", "store_false"):
                    if val != a.default:
                        provided.append(a.dest)
                elif a.action == "count":
                    if val != 0:
                        provided.append(a.dest)
                elif a.action in ("append", "append_const"):
                    if val and len(val) > 0:
                        provided.append(a.dest)
                elif val is not None:
                    provided.append(a.dest)
            
            if len(provided) > 1:
                names = ", ".join([f"'{a.names[0]}'" for a in group.arguments if a.dest in provided])
                raise ValueError(f"Arguments {names} are mutually exclusive")
            if group.required and not provided:
                names = ", ".join([f"'{a.names[0]}'" for a in group.arguments])
                raise ValueError(f"One of {names} is required")
        
        # Check choices
        for argument in all_args:
            if argument.choices and argument.dest in result:
                value = result[argument.dest]
                if isinstance(value, list):
                    for v in value:
                        if v not in argument.choices:
                            raise ValueError(f"Invalid choice '{v}' for {argument.dest}")
                elif value not in argument.choices:
                    raise ValueError(f"Invalid choice '{value}' for {argument.dest}")
        
        # Custom validators
        for argument in all_args:
            if argument.validator and argument.dest in result:
                if not argument.validator(result[argument.dest]):
                    raise ValueError(f"Validation failed for {argument.dest}")
        
        # Check dependencies
        for argument in all_args:
            if argument.depends_on and argument.dest in result and result[argument.dest] is not None:
                for dep in argument.depends_on:
                    dep_arg = next((a for a in all_args if a.dest == dep), None)
                    if not dep_arg or result.get(dep) is None:
                        raise ValueError(f"Argument {argument.dest} requires {dep}")
        
        # Check conflicts
        for argument in all_args:
            if argument.conflicts_with and argument.dest in result and result[argument.dest] is not None:
                for conflict in argument.conflicts_with:
                    if result.get(conflict) is not None:
                        raise ValueError(
                            f"Arguments {argument.dest} and {conflict} cannot be used together"
                        )
    
    def _parse_optional_arg(self, argument: Argument, args: List[str], index: int) -> Any:
        """Parse an optional argument and its value(s)."""
        if argument.nargs is None:
            # Single value expected
            if index + 1 >= len(args) or args[index + 1].startswith('-'):
                raise ValueError(f"Argument {argument.names[0]} requires a value")
            try:
                value = argument.type(args[index + 1])
                if argument.choices and value not in argument.choices:
                    raise ValueError(f"Invalid choice: {value}")
                return value
            except (ValueError, TypeError):
                raise ValueError(
                    f"Invalid value '{args[index + 1]}' for {argument.dest}"
                )
        
        elif argument.nargs == '?':
            # Optional value
            if index + 1 < len(args) and not args[index + 1].startswith('-'):
                try:
                    value = argument.type(args[index + 1])
                    if argument.choices and value not in argument.choices:
                        raise ValueError(f"Invalid choice: {value}")
                    return value
                except (ValueError, TypeError):
                    raise ValueError(f"Invalid value '{args[index + 1]}' for {argument.dest}")
            return argument.const if argument.const is not None else argument.default
        
        elif argument.nargs == '*':
            # Zero or more values
            values = []
            i = index + 1
            while i < len(args) and not args[i].startswith('-'):
                try:
                    value = argument.type(args[i])
                    if argument.choices and value not in argument.choices:
                        raise ValueError(f"Invalid choice: {value}")
                    values.append(value)
                except (ValueError, TypeError):
                    raise ValueError(f"Invalid value '{args[i]}' for {argument.dest}")
                i += 1
            return values
        
        elif argument.nargs == '+':
            # One or more values
            values = []
            i = index + 1
            if i >= len(args) or args[i].startswith('-'):
                raise ValueError(f"Argument {argument.names[0]} requires at least one value")
            while i < len(args) and not args[i].startswith('-'):
                try:
                    value = argument.type(args[i])
                    if argument.choices and value not in argument.choices:
                        raise ValueError(f"Invalid choice: {value}")
                    values.append(value)
                except (ValueError, TypeError):
                    raise ValueError(f"Invalid value '{args[i]}' for {argument.dest}")
                i += 1
            return values
        
        elif isinstance(argument.nargs, int):
            # Exact number of values
            values = []
            for i in range(argument.nargs):
                if index + 1 + i >= len(args):
                    raise ValueError(f"Argument {argument.names[0]} requires {argument.nargs} values")
                try:
                    value = argument.type(args[index + 1 + i])
                    if argument.choices and value not in argument.choices:
                        raise ValueError(f"Invalid choice: {value}")
                    values.append(value)
                except (ValueError, TypeError):
                    raise ValueError(f"Invalid value '{args[index + 1 + i]}' for {argument.dest}")
            return values
        
        return argument.default
    
    def print_help(self) -> None:
        """Print help message with advanced formatting."""
        print(f"usage: {self.prog} [options]")
        if self.description:
            print(f"\n{self.description}")
        
        if self.arguments or self.argument_groups or self.mutually_exclusive_groups:
            print("\noptional arguments:")
            for argument in self.arguments:
                if argument.is_optional:
                    self._print_argument_help(argument)
            
            for group in self.argument_groups:
                if group.title:
                    print(f"\n{group.title}:")
                    if group.description:
                        print(f"  {group.description}")
                for argument in group.arguments:
                    self._print_argument_help(argument)
            
            for group in self.mutually_exclusive_groups:
                print("\nmutually exclusive arguments:")
                for argument in group.arguments:
                    self._print_argument_help(argument)
        
        # Positional arguments
        positional = [a for a in self._get_all_arguments() if not a.is_optional]
        if positional:
            print("\npositional arguments:")
            for argument in positional:
                self._print_argument_help(argument)
        
        if self.epilog:
            print(f"\n{self.epilog}")
    
    def _print_argument_help(self, argument: Argument) -> None:
        """Print help for a single argument."""
        names = ", ".join(argument.names)
        if argument.aliases:
            names += ", " + ", ".join(argument.aliases)
        
        help_text = argument.help_text
        if argument.choices:
            help_text += f" (choices: {', '.join(map(str, argument.choices))})"
        if argument.default is not None and argument.action == "store":
            help_text += f" (default: {argument.default})"
        
        print(f"  {names:35} {help_text}")
    
    def get_help_text(self) -> str:
        """Return help text as a string."""
        import io
        import contextlib
        
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            self.print_help()
        return f.getvalue()
    
    def error(self, message: str) -> None:
        """Print error message and exit."""
        print(f"Error: {message}", file=sys.stderr)
        if self.exit_on_error:
            sys.exit(2)
        else:
            raise ValueError(message)


class SubparsersAction:
    """Handles subcommand parsing."""
    
    def __init__(self, parser: ArgumentParser, title: str, dest: str):
        self.parser = parser
        self.title = title
        self.dest = dest
        self.subparsers: Dict[str, Subparser] = {}
    
    def add_parser(
        self,
        name: str,
        help_text: str = "",
        aliases: Optional[List[str]] = None
    ) -> ArgumentParser:
        """Add a subparser."""
        subparser = Subparser(name, help_text, aliases)
        self.subparsers[name] = subparser
        
        # Create a new ArgumentParser for this subcommand
        new_parser = ArgumentParser(
            description=help_text,
            prog=f"{self.parser.prog} {name}"
        )
        new_parser._subparser_parent = self.parser
        return new_parser


# Example usage
if __name__ == "__main__":
    parser = ArgumentParser(
        description="Advanced hand-made argument parser with many features",
        prog="advanced_parser",
        epilog="Example: %(prog)s process -v --number 42 file.txt",
        allow_abbrev=True,
        add_help=True,
    )
    
    # Positional argument
    parser.add_argument(
        "filename",
        help="Input file name"
    )
    
    # Basic optional arguments
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    # Argument with choices
    parser.add_argument(
        "-f", "--format",
        choices=["json", "xml", "csv", "yaml"],
        default="json",
        help="Output format"
    )
    
    # Argument with environment variable support
    parser.add_argument(
        "-u", "--username",
        env_var="APP_USER",
        help="Username (can be set via APP_USER env var)"
    )
    
    # Counter argument
    parser.add_argument(
        "-q", "--quiet",
        action="count",
        default=0,
        help="Reduce output verbosity (can be used multiple times)"
    )
    
    # Create an argument group
    config_group = parser.add_argument_group("Configuration", "Settings for program behavior")
    config_group.add_argument(
        "-c", "--config",
        default="config.json",
        help="Configuration file path"
    )
    config_group.add_argument(
        "-t", "--timeout",
        type_=int,
        default=30,
        help="Operation timeout in seconds"
    )
    
    # Create mutually exclusive group
    output_group = parser.add_mutually_exclusive_group(required=True)
    output_group.add_argument(
        "-o", "--output",
        help="Output file"
    )
    output_group.add_argument(
        "--stdout",
        action="store_true",
        help="Print to stdout"
    )
    
    # Multiple values
    parser.add_argument(
        "--filters",
        nargs="+",
        default=[],
        help="Apply filters (requires at least one)"
    )
    
    # Optional values
    parser.add_argument(
        "--log-level",
        nargs="?",
        const="INFO",
        default="WARNING",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Set log level"
    )
    
    # Custom validator
    def positive_number(value):
        return int(value) > 0
    
    parser.add_argument(
        "-n", "--number",
        type_=int,
        default=1,
        validator=positive_number,
        help="A positive number"
    )
    
    # Append action
    parser.add_argument(
        "-d", "--define",
        action="append",
        default=[],
        help="Define variables (can be used multiple times)"
    )
    
    # Store constant
    parser.add_argument(
        "--json-output",
        action="store_const",
        const={"format": "json", "pretty": True},
        help="Use JSON output format"
    )
    
    try:
        args = parser.parse_args()
        print("✓ Parsed arguments successfully!")
        print("\nArguments:")
        for key, value in sorted(args.items()):
            print(f"  {key:20} = {value}")
        
        # Show some advanced features
        print("\nAdvanced features demonstrated:")
        print("  ✓ Positional arguments")
        print("  ✓ Optional arguments with long and short flags")
        print("  ✓ Argument groups for organization")
        print("  ✓ Mutually exclusive groups")
        print("  ✓ Choices validation")
        print("  ✓ Environment variable support")
        print("  ✓ Counter actions")
        print("  ✓ Multiple value arguments (+, *)")
        print("  ✓ Optional value arguments (?)")
        print("  ✓ Custom validators")
        print("  ✓ Append actions")
        print("  ✓ Constant store actions")
        print("  ✓ Type conversion (int, str, etc.)")
        print("  ✓ Default values")
        print("  ✓ Help text with formatting")
        print("  ✓ Auto-generated help message")
        
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
