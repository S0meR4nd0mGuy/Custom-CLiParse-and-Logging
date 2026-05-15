# CliParse - Modern CLI Argument Parser

A lightweight, powerful Python CLI argument parser with a modern API and rich terminal features.

## 🎯 Key Differences from argparse

CliParse is a **completely redesigned** argument parser with a unique, intuitive API:

| Feature | argparse | CliParse |
|---------|----------|----------|
| **Main Class** | `ArgumentParser` | `CliApp` |
| **Add Argument** | `add_argument()` | `define_param()` or `define_flag()` |
| **Argument Type** | `Argument` class | `Parameter` class |
| **Types** | Multiple string forms ("int", "float") | `ParamType` enum (STRING, INTEGER, FLOAT, etc.) |
| **Groups** | `ArgumentGroup` | `ParameterGroup` |
| **Constraints** | Limited (mutually exclusive) | Rich: `forbid_together()`, `require_one_of()`, `require_if()`, `add_constraint()` |
| **Styling** | Plain text | **Built-in ANSI colors & emojis** 🎨 |
| **Output** | Static | `define_param()` + `define_flag()` → Clear intent |
| **Transformers** | Limited | Full `transformer` callback support |
| **Validators** | Limited | `validator` callbacks + constraint system |

## ✨ Key Features

- **Distinct API**: Not a copy of argparse - unique naming and structure
- **Type Safety**: `ParamType` enum instead of string type names
- **Rich Constraints**: Dependencies, conflicts, custom validators
- **Colored Output**: Optional ANSI colors for better UX
- **Transformer Functions**: Custom type conversion and processing
- **Environment Variables**: Automatic fallback to env vars
- **Parameter Groups**: Organize related parameters
- **Multi-Values**: Built-in support for multi-value parameters
- **No Dependencies**: Pure Python stdlib only

## 📦 Installation

Just import from cliparse.py:

```python
from cliparse import CliApp, ParamType, Parameter, Flag, ValidationError
```

## 🚀 Quick Start

### Simple Example

```python
from cliparse import CliApp, ParamType

app = CliApp(
    name="hello",
    version="1.0.0",
    description="Simple greeting app"
)

# Define positional parameter
app.define_param("name", required=True, help_text="Person to greet")

# Define optional parameter
app.define_param("--count", short="c", param_type=ParamType.INTEGER, 
                 default=1, help_text="Number of greetings")

# Define flag
app.define_flag("verbose", short="v", help_text="Show details")

# Parse arguments
config = app.parse()

print(f"Hello {config['name']}!" * config['count'])
if config['verbose']:
    print("Done!")
```

Run: `python hello.py Alice -c 3 -v`

### Advanced Example

```python
from cliparse import CliApp, ParamType, ValidationError

app = CliApp(name="datamunger", version="2.0.0")

# Positional parameter
app.define_param("input_file", required=True)

# Optional parameters in groups
app.create_group("Processing", "Control processing")
app.define_param("--format", param_type=ParamType.CHOICE,
                 choices=["json", "csv", "xml"])
app.define_param("--threads", short="t", param_type=ParamType.INTEGER,
                 default=1, choices=[1, 2, 4, 8])

# Flags
app.define_flag("verbose", short="v")
app.define_flag("quiet", short="q")

# Constraints
app.forbid_together("verbose", "quiet")  # Can't use both

# Custom validator
def validate_format(config):
    if config.get('format') == 'xml' and config['threads'] > 2:
        raise ValidationError("XML format only supports 1-2 threads")
    return True

app.add_constraint(validate_format)

# Parse
config = app.parse()

# Use config dict
print(f"Processing {config['input_file']} as {config['format']}")
```

## 📚 API Reference

### CliApp Class

Main application class for parsing CLI arguments.

#### Constructor

```python
CliApp(
    name: str = "app",
    version: str = "1.0.0",
    description: str = "",
    auto_help: bool = True,
    enable_color: bool = True,
    strict: bool = False
)
```

**Parameters:**
- `name`: Application name
- `version`: Version string
- `description`: Help text description
- `auto_help`: Automatically add `-h/--help`
- `enable_color`: Use ANSI colors in output
- `strict`: Strict validation mode

#### Methods

##### `define_param(name, **kwargs)`

Define a parameter (positional or optional).

```python
app.define_param(
    name: str,
    aliases: Tuple[str, ...] = (),
    short: Optional[str] = None,
    param_type: ParamType = ParamType.STRING,
    required: bool = False,
    help_text: str = "",
    default: Any = None,
    choices: List[Any] = None,
    validator: Callable[[Any], bool] = None,
    transformer: Callable[[Any], Any] = None,
    env_var: Optional[str] = None,
    multi: bool = False,
    hidden: bool = False
)
```

**Parameters:**
- `name`: Parameter name (positional: "filename", optional: "--output" or "-o")
- `aliases`: Alternative names
- `short`: Short flag (e.g., "v" for "-v")
- `param_type`: Type from `ParamType` enum
- `required`: Must be provided
- `help_text`: Help description
- `default`: Default value if not provided
- `choices`: Allowed values (list or values from ParamType.CHOICE)
- `validator`: Custom validation function
- `transformer`: Transform input value
- `env_var`: Environment variable fallback
- `multi`: Accept multiple values
- `hidden`: Hide from help

**Returns:** `Parameter` object

**Examples:**
```python
# Positional
app.define_param("filename", required=True, help_text="Input file")

# Optional with short flag
app.define_param("--output", short="o", help_text="Output file")

# With type
app.define_param("--count", short="c", param_type=ParamType.INTEGER)

# With choices
app.define_param("--format", param_type=ParamType.CHOICE,
                 choices=["json", "csv", "xml"])

# With default
app.define_param("--threads", param_type=ParamType.INTEGER, default=4)

# With custom validator
def validate_port(value):
    if not (1 <= value <= 65535):
        raise ValidationError("Port must be 1-65535")
    return True

app.define_param("--port", param_type=ParamType.INTEGER, validator=validate_port)

# With transformer
def to_path(value):
    from pathlib import Path
    return Path(value)

app.define_param("--input", param_type=ParamType.PATH, transformer=to_path)
```

##### `define_flag(name, **kwargs)`

Define a boolean flag.

```python
app.define_flag(
    name: str,
    aliases: Tuple[str, ...] = (),
    short: Optional[str] = None,
    help_text: str = "",
    default: bool = False,
    hidden: bool = False
)
```

**Examples:**
```python
app.define_flag("verbose", short="v", help_text="Verbose output")
app.define_flag("quiet", short="q", help_text="Minimal output")
app.define_flag("debug", help_text="Debug mode")
```

##### `create_group(name, description="")`

Create an organizational group for parameters.

```python
app.create_group("Processing", "Data processing options")
```

After creating a group, all subsequent `define_param()`/`define_flag()` calls belong to that group until you create another group.

##### `forbid_together(*param_names)`

Constraint: These parameters cannot be used together.

```python
app.forbid_together("verbose", "quiet")
app.forbid_together("--output", "--stdout")
```

##### `require_one_of(*param_names)`

Constraint: At least one of these parameters is required.

```python
app.require_one_of("--input-file", "--input-dir")
```

##### `require_if(trigger_param, required_param)`

Constraint: If `trigger_param` is provided, `required_param` must also be provided.

```python
app.require_if("--encrypt", "--key-file")
```

##### `add_constraint(validator)`

Add custom constraint validator function.

```python
def custom_constraint(config):
    if config['threads'] > 4 and not config.get('memory_gb'):
        raise ValidationError("Must specify --memory-gb when threads > 4")
    return True

app.add_constraint(custom_constraint)
```

##### `parse(args=None)`

Parse command-line arguments.

```python
config = app.parse()  # Parse sys.argv
config = app.parse(["alice", "-c", "3"])  # Parse specific args
```

**Returns:** `dict` with parameter values

**Raises:** `ValidationError` on validation failure

##### `show_help()`

Display colored help message.

```python
app.show_help()
```

##### `get_help_text()`

Get help message as string.

```python
help_str = app.get_help_text()
```

### ParamType Enum

Type system for parameters.

```python
from cliparse import ParamType

ParamType.STRING       # Text (default)
ParamType.INTEGER      # Whole numbers
ParamType.FLOAT        # Decimal numbers
ParamType.BOOLEAN      # True/False
ParamType.PATH         # File paths
ParamType.CHOICE       # Limited set of values
ParamType.MULTI        # Multiple values
```

**Examples:**
```python
app.define_param("--count", param_type=ParamType.INTEGER)
app.define_param("--ratio", param_type=ParamType.FLOAT)
app.define_param("--input", param_type=ParamType.PATH)
app.define_param("--format", param_type=ParamType.CHOICE, choices=["json", "csv"])
```

### Parameter Class

Individual parameter definition.

```python
from cliparse import Parameter

param = Parameter(
    name="filename",
    required=True,
    param_type=ParamType.STRING
)
```

### Flag Class

Boolean flag definition.

```python
from cliparse import Flag

flag = Flag(
    name="verbose",
    short="v",
    help_text="Verbose output"
)
```

### ValidationError Exception

Raised when validation fails.

```python
from cliparse import ValidationError

try:
    config = app.parse()
except ValidationError as e:
    print(f"Validation error: {e}")
```

## 🎨 Color & Styling

CliParse includes built-in color support via ANSI codes.

### Disable Colors

```python
from cliparse import Color

Color.disable()  # Disable colors globally
```

Or disable per-app:

```python
app = CliApp(enable_color=False)
```

### Color Class

```python
from cliparse import Color

# Color constants
Color.BOLD
Color.YELLOW
Color.CYAN
Color.GREEN
Color.MAGENTA
Color.RED
Color.RESET
```

## 🔄 Validators and Transformers

### Validators

Custom validation functions that return `True` or raise `ValidationError`:

```python
def validate_port(value):
    if not (1 <= value <= 65535):
        raise ValidationError(f"Port must be 1-65535, got {value}")
    return True

app.define_param("--port", validator=validate_port)
```

### Transformers

Custom transformation functions that convert input values:

```python
from pathlib import Path

def to_path(value):
    return Path(value).resolve()

app.define_param("--input", transformer=to_path)
```

## 📖 Examples

See included example files:

- **example_cliparse_simple.py**: Basic usage
- **example_cliparse_advanced.py**: Groups, constraints, validation

Run them:

```bash
python example_cliparse_simple.py --help
python example_cliparse_simple.py Alice -c 3 -v

python example_cliparse_advanced.py --help
python example_cliparse_advanced.py data.csv -o result.json -v
```

## 🔧 Environment Variables

Parameters can fall back to environment variables:

```python
app.define_param("--api-key", env_var="API_KEY")
```

If `--api-key` is not provided on CLI, CliParse will check the `API_KEY` environment variable.

## 📝 Notes

- **No external dependencies**: Uses Python stdlib only
- **Python 3.6+**: Uses f-strings and type hints
- **Lightweight**: ~1000 lines of code
- **Typed**: Full type hints for IDE support
- **Modular**: Import only what you need

## 🤝 Integration

Import into your projects:

```python
from cliparse import CliApp, ParamType, ValidationError
```

## 📄 License

This is a custom implementation created as an educational alternative to argparse.
