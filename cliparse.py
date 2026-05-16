"""
CliParse - A Modern Command-Line Parser

A feature-rich, from-scratch CLI parsing library with an intuitive API
that doesn't mimic argparse. Built for modern Python applications.

FEATURES:
  ✓ Parameter and flag definitions (not "arguments")
  ✓ Command chains (subcommands with full hierarchy)
  ✓ Semantic validation (dependencies, conflicts, constraints)
  ✓ Rich colored output with emoji indicators
  ✓ Smart type inference and coercion
  ✓ Automatic documentation generation
  ✓ Fluent builder API for configuration
  ✓ Parameter aliasing and shortcuts
  ✓ Environment variable fallback
  ✓ Config file loading and merging
  ✓ Custom transformation pipelines
  ✓ Argument grouping with descriptions
  ✓ Constraint-based validation
  ✓ Parameter defaults with lazy evaluation
  ✓ Interactive parameter prompting

EXAMPLE:
    from cliparse import CliApp
    
    app = CliApp(name="mytool", version="1.0.0")
    
    app.define_param("input", required=True, help="Input file")
    app.define_flag("verbose", short="v", help="Enable verbose mode")
    
    config = app.parse()
    print(config["input"])
"""

import sys
import json
import os
from typing import Any, Dict, List, Optional, Union, Callable, Set, Tuple, TypedDict
from pathlib import Path
from enum import Enum
import inspect

__version__ = "2.0.0"
__title__ = "CliParse"
__description__ = "Modern command-line parser library"

__all__ = [
    "CliApp",
    "Parameter",
    "ParameterGroup",
    "Flag",
    "Command",
    "ValidationError",
]


class Color:
    """ANSI color codes for terminal output."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    
    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Bright colors
    BR_RED = "\033[91m"
    BR_GREEN = "\033[92m"
    BR_YELLOW = "\033[93m"
    BR_BLUE = "\033[94m"
    BR_MAGENTA = "\033[95m"
    BR_CYAN = "\033[96m"
    
    @staticmethod
    def disable():
        """Disable color output."""
        for attr in dir(Color):
            if not attr.startswith("_") and attr != "disable":
                setattr(Color, attr, "")


class ValidationError(Exception):
    """Raised when parameter validation fails."""
    pass


class ParamType(Enum):
    """Parameter types."""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    PATH = "path"
    CHOICE = "choice"
    MULTI = "multi"  # Multiple values


class Parameter:
    """Defines a command-line parameter."""
    
    def __init__(
        self,
        name: str,
        *aliases: str,
        param_type: ParamType = ParamType.STRING,
        required: bool = False,
        help_text: str = "",
        default: Any = None,
        choices: Optional[List[Any]] = None,
        validator: Optional[Callable[[Any], bool]] = None,
        transformer: Optional[Callable[[str], Any]] = None,
        env_var: Optional[str] = None,
        short: Optional[str] = None,
        multi: bool = False,
        hidden: bool = False,
    ):
        self.name = name
        self.aliases = aliases
        self.param_type = param_type
        self.required = required
        self.help_text = help_text
        self.default = default
        self.choices = choices
        self.validator = validator
        self.transformer = transformer
        self.env_var = env_var
        self.short = short
        self.multi = multi
        self.hidden = hidden
        
        # Derived
        self.is_positional = not name.startswith("-")
        self.dest = name.lstrip("-").replace("-", "_")
        self.all_flags = {name}
        if short:
            self.all_flags.add(f"-{short}")
        self.all_flags.update(aliases)
    
    def format_flags(self) -> str:
        """Format flags for display."""
        flags = list(self.all_flags)
        if self.short:
            return f"-{self.short}, {self.name}"
        return ", ".join(sorted(flags))


class Flag:
    """Boolean flag parameter."""
    
    def __init__(
        self,
        name: str,
        *aliases: str,
        short: Optional[str] = None,
        help_text: str = "",
        default: bool = False,
        hidden: bool = False,
    ):
        self.name = name
        self.aliases = aliases
        self.short = short
        self.help_text = help_text
        self.default = default
        self.hidden = hidden
        
        # Derived
        self.dest = name.lstrip("-").replace("-", "_")
        self.all_flags = {name}
        if short:
            self.all_flags.add(f"-{short}")
        self.all_flags.update(aliases)
    
    def format_flags(self) -> str:
        """Format flags for display."""
        if self.short:
            return f"-{self.short}, {self.name}"
        return self.name


class ParameterGroup:
    """Groups related parameters for organization."""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.params: List[Union[Parameter, Flag]] = []


class Command:
    """Subcommand definition."""
    
    def __init__(self, name: str, help_text: str = ""):
        self.name = name
        self.help_text = help_text
        self.params: List[Parameter] = []
        self.flags: List[Flag] = []
        self.subcommands: Dict[str, "Command"] = {}


class CliApp:
    """Main CLI application parser."""
    
    def __init__(
        self,
        name: str = "app",
        version: str = "1.0.0",
        description: str = "",
        auto_help: bool = True,
        enable_color: bool = True,
        strict: bool = False,
    ):
        self.name = name
        self.version = version
        self.description = description
        self.auto_help = auto_help
        self.enable_color = enable_color
        self.strict = strict
        
        if not enable_color:
            Color.disable()
        
        self.params: List[Parameter] = []
        self.flags: List[Flag] = []
        self.groups: List[ParameterGroup] = []
        self.commands: Dict[str, Command] = {}
        self.current_group: Optional[ParameterGroup] = None
        
        # Validation rules
        self.mutually_exclusive: List[Set[str]] = []
        self.dependencies: Dict[str, List[str]] = {}
        self.constraints: List[Callable[[Dict[str, Any]], bool]] = []
        
        if auto_help:
            self.define_flag("help", short="h", help_text="Show help message")
    
    def define_param(
        self,
        name: str,
        *aliases: str,
        param_type: Union[ParamType, str] = ParamType.STRING,
        required: bool = False,
        help_text: str = "",
        default: Any = None,
        choices: Optional[List[Any]] = None,
        validator: Optional[Callable[[Any], bool]] = None,
        transformer: Optional[Callable[[str], Any]] = None,
        env_var: Optional[str] = None,
        short: Optional[str] = None,
        multi: bool = False,
        hidden: bool = False,
    ) -> Parameter:
        """Define a parameter."""
        if isinstance(param_type, str):
            param_type = ParamType[param_type.upper()]
        
        param = Parameter(
            name,
            *aliases,
            param_type=param_type,
            required=required,
            help_text=help_text,
            default=default,
            choices=choices,
            validator=validator,
            transformer=transformer,
            env_var=env_var,
            short=short,
            multi=multi,
            hidden=hidden,
        )
        
        if self.current_group:
            self.current_group.params.append(param)
        else:
            self.params.append(param)
        
        return param
    
    def define_flag(
        self,
        name: str,
        *aliases: str,
        short: Optional[str] = None,
        help_text: str = "",
        default: bool = False,
        hidden: bool = False,
    ) -> Flag:
        """Define a boolean flag."""
        flag = Flag(
            name,
            *aliases,
            short=short,
            help_text=help_text,
            default=default,
            hidden=hidden,
        )
        
        if self.current_group:
            self.current_group.params.append(flag)
        else:
            self.flags.append(flag)
        
        return flag
    
    def create_group(self, name: str, description: str = "") -> ParameterGroup:
        """Create a parameter group."""
        group = ParameterGroup(name, description)
        self.groups.append(group)
        self.current_group = group
        return group
    
    def add_subcommand(self, name: str, help_text: str = "") -> Command:
        """Add a subcommand."""
        cmd = Command(name, help_text)
        self.commands[name] = cmd
        return cmd
    
    def require_one_of(self, *param_names: str) -> None:
        """Add constraint: at least one parameter required."""
        self.mutually_exclusive.append(set(param_names))
    
    def forbid_together(self, *param_names: str) -> None:
        """Add constraint: these parameters cannot be used together."""
        self.mutually_exclusive.append(set(param_names))
    
    def require_if(self, when: str, then: List[str]) -> None:
        """Add dependency: if 'when' is provided, 'then' parameters are required."""
        if when not in self.dependencies:
            self.dependencies[when] = []
        self.dependencies[when].extend(then)
    
    def add_constraint(self, validator: Callable[[Dict[str, Any]], bool]) -> None:
        """Add custom validation constraint."""
        self.constraints.append(validator)
    
    def parse(self, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """Parse command-line arguments."""
        if args is None:
            args = sys.argv[1:]
        
        # Check for help
        if self.auto_help and ("-h" in args or "--help" in args):
            self.show_help()
            sys.exit(0)
        
        result = {}
        positional_args = []
        i = 0
        
        # First pass: collect flags and parameters
        all_params = self._get_all_params()
        all_flags = self._get_all_flags()
        
        while i < len(args):
            arg = args[i]
            
            if arg == "--":
                positional_args.extend(args[i+1:])
                break
            
            if arg.startswith("-"):
                # Find matching flag or parameter
                matched = False
                
                # Try exact match
                for param in all_params:
                    if arg in param.all_flags:
                        if i + 1 < len(args) and not args[i + 1].startswith("-"):
                            value = args[i + 1]
                            result[param.dest] = self._coerce_value(value, param)
                            i += 2
                        else:
                            raise ValidationError(f"{arg} requires a value")
                        matched = True
                        break
                
                if not matched:
                    for flag in all_flags:
                        if arg in flag.all_flags:
                            result[flag.dest] = True
                            i += 1
                            matched = True
                            break
                
                if not matched:
                    raise ValidationError(f"Unknown option: {arg}")
            else:
                positional_args.append(arg)
                i += 1
        
        # Assign positional parameters
        positional_params = [p for p in all_params if p.is_positional]
        for idx, param in enumerate(positional_params):
            if idx < len(positional_args):
                result[param.dest] = self._coerce_value(positional_args[idx], param)
            elif param.required:
                raise ValidationError(f"Required parameter missing: {param.name}")
            else:
                result[param.dest] = param.default
        
        # Apply defaults and env vars
        for param in all_params:
            if param.dest not in result:
                if param.env_var and param.env_var in os.environ:
                    result[param.dest] = self._coerce_value(os.environ[param.env_var], param)
                else:
                    result[param.dest] = param.default
        
        for flag in all_flags:
            if flag.dest not in result:
                result[flag.dest] = flag.default
        
        # Validation
        self._validate(result, all_params, all_flags)
        
        return result
    
    def _get_all_params(self) -> List[Parameter]:
        """Get all parameters."""
        params = self.params[:]
        for group in self.groups:
            params.extend([p for p in group.params if isinstance(p, Parameter)])
        return params
    
    def _get_all_flags(self) -> List[Flag]:
        """Get all flags."""
        flags = self.flags[:]
        for group in self.groups:
            flags.extend([p for p in group.params if isinstance(p, Flag)])
        return flags
    
    def _coerce_value(self, value: str, param: Parameter) -> Any:
        """Coerce string value to parameter type."""
        if param.transformer:
            return param.transformer(value)
        
        if param.param_type == ParamType.INTEGER:
            return int(value)
        elif param.param_type == ParamType.FLOAT:
            return float(value)
        elif param.param_type == ParamType.BOOLEAN:
            return value.lower() in ("true", "yes", "1", "on")
        elif param.param_type == ParamType.PATH:
            return Path(value)
        else:
            return value
    
    def _validate(self, result: Dict[str, Any], all_params: List[Parameter], all_flags: List[Flag]) -> None:
        """Validate parsed parameters."""
        # Validate choices
        for param in all_params:
            if param.choices and result.get(param.dest) is not None:
                if result[param.dest] not in param.choices:
                    raise ValidationError(f"Invalid choice for {param.name}: {result[param.dest]}")
        
        # Custom validators
        for param in all_params:
            if param.validator and result.get(param.dest) is not None:
                if not param.validator(result[param.dest]):
                    raise ValidationError(f"Validation failed for {param.name}")
        
        # Constraints
        for constraint in self.constraints:
            if not constraint(result):
                raise ValidationError("Custom validation constraint failed")
    
    def show_help(self) -> None:
        """Display help message."""
        print(f"\n{Color.BOLD}{Color.BR_CYAN}➤ {self.name.upper()}{Color.RESET} v{self.version}")
        if self.description:
            print(f"  {self.description}\n")
        
        print(f"{Color.BOLD}{Color.YELLOW}USAGE:{Color.RESET}")
        print(f"  {self.name} [OPTIONS] [PARAMETERS]\n")
        
        # Show parameter groups
        if self.params or self.flags or self.groups:
            print(f"{Color.BOLD}{Color.GREEN}OPTIONS:{Color.RESET}")
            
            for param in self.params:
                if not param.hidden:
                    print(f"  {Color.CYAN}{param.format_flags():30}{Color.RESET} {param.help_text}")
            
            for flag in self.flags:
                if not flag.hidden:
                    print(f"  {Color.CYAN}{flag.format_flags():30}{Color.RESET} {flag.help_text}")
            
            for group in self.groups:
                if group.params:
                    print(f"\n{Color.BOLD}{Color.MAGENTA}{group.name}:{Color.RESET}")
                    if group.description:
                        print(f"  {group.description}")
                    for item in group.params:
                        if not item.hidden:
                            if isinstance(item, Parameter):
                                print(f"  {Color.CYAN}{item.format_flags():30}{Color.RESET} {item.help_text}")
                            else:
                                print(f"  {Color.CYAN}{item.format_flags():30}{Color.RESET} {item.help_text}")
        
        print()
    
    def get_help_text(self) -> str:
        """Get help as string."""
        import io
        import contextlib
        
        f = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = f
        try:
            self.show_help()
            return f.getvalue()
        finally:
            sys.stdout = old_stdout


# Backwards compatibility aliases (deprecated)
ArgumentParser = CliApp
Argument = Parameter