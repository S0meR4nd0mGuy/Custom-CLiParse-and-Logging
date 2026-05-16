# CliParse - Modern CLI Argument Parser

A feature-rich, from-scratch CLI parsing library with an intuitive API that doesn't mimic argparse. Built for modern Python applications with semantic validation, rich colored output, and parameter grouping.

## Features

✅ **Distinct API** - Not argparse; unique naming (`CliApp`, `define_param`, `define_flag`)  
✅ **Type Safety** - `ParamType` enum prevents typos  
✅ **Semantic Validation** - Dependencies, conflicts, custom constraints  
✅ **Rich Terminal Output** - ANSI colors with emoji indicators  
✅ **Parameter Groups** - Organize related parameters  
✅ **Positional & Optional** - Full support for both  
✅ **Short Flags** - `-v` style shortcuts  
✅ **Environment Variables** - Automatic fallback support  
✅ **Custom Transformers** - Transform input values  
✅ **Zero Dependencies** - Pure Python stdlib  

## Installation

```bash
pip install -e .
```

## Quick Start

```python
from cliparse import CliApp, ParamType

app = CliApp(name="hello", version="1.0.0")

app.define_param("name", required=True, help_text="Your name")
app.define_param("--count", short="c", param_type=ParamType.INTEGER, default=1)
app.define_flag("verbose", short="v", help_text="Verbose output")

config = app.parse()

for _ in range(config['count']):
    print(f"Hello {config['name']}!")
    
if config['verbose']:
    print("Verbose mode enabled")
```

**Run:** `python hello.py Alice --count 3 -v`

## Core Concepts

### CliApp vs ArgumentParser

CliParse is **not** a copy of argparse:

| Feature | argparse | CliParse |
|---------|----------|----------|
| Main class | `ArgumentParser` | `CliApp` |
| Define parameter | `add_argument()` | `define_param()` |
| Define flag | `add_argument(action='store_true')` | `define_flag()` |
| Types | String names | `ParamType` enum |
| Validation | Limited | Rich constraints |
| Colors | ❌ | ✅ |
| Groups | Basic | Advanced with descriptions |

### Parameters vs Flags

**Parameters** take values:
```python
app.define_param("input")           # Positional
app.define_param("--output")        # Optional
app.define_param("--count", param_type=ParamType.INTEGER)
```

**Flags** are boolean:
```python
app.define_flag("verbose", short="v")   # True if present
app.define_flag("--debug")              # False by default
```

## API Reference

### CliApp

**Constructor:**
```python
CliApp(
    name: str = "app",              # Application name
    version: str = "1.0.0",         # Version string
    description: str = "",          # Help description
    auto_help: bool = True,         # Auto-add -h/--help
    enable_color: bool = True,      # Use ANSI colors
    strict: bool = False            # Strict parsing mode
)
```

**Methods:**

```python
# Define parameters and flags
app.define_param(name, **options) -> Parameter
app.define_flag(name, **options) -> Flag

# Organize parameters
app.create_group(name, description) -> ParameterGroup

# Add validation constraints
app.require_one_of(*param_names)
app.forbid_together(*param_names)
app.require_if(when, then)
app.add_constraint(validator_func)

# Parse and display
app.parse(args=None) -> Dict[str, Any]
app.show_help()
app.get_help_text() -> str
```

### define_param()

```python
app.define_param(
    name: str,                          # "input" or "--output"
    *aliases: str,                      # Alternative names
    param_type: ParamType = STRING,     # Value type
    required: bool = False,             # Must be provided
    help_text: str = "",                # Help description
    default: Any = None,                # Default value
    choices: List[Any] = None,          # Allowed values
    validator: Callable = None,         # Custom validation
    transformer: Callable = None,       # Transform input
    env_var: str = None,                # Environment variable fallback
    short: str = None,                  # Short flag like "o"
    multi: bool = False,                # Accept multiple values
    hidden: bool = False                # Hide from help
) -> Parameter
```

**Examples:**

```python
# Positional parameter
app.define_param("filename", required=True, help_text="Input file")

# Optional with short flag
app.define_param("--output", short="o", help_text="Output file")

# With type
app.define_param("--count", param_type=ParamType.INTEGER, default=1)

# With choices
app.define_param("--format", param_type=ParamType.CHOICE, 
                 choices=["json", "csv", "xml"])

# Environment variable fallback
app.define_param("--api-key", env_var="API_KEY")

# Custom transformer
def to_path(value):
    return Path(value)
app.define_param("--input", transformer=to_path)
```

### define_flag()

```python
app.define_flag(
    name: str,                  # "verbose" or "--debug"
    *aliases: str,              # Alternative names
    short: str = None,          # Short flag like "v"
    help_text: str = "",        # Help description
    default: bool = False,      # Default value
    hidden: bool = False        # Hide from help
) -> Flag
```

**Examples:**

```python
# Simple flag
app.define_flag("verbose", short="v", help_text="Verbose output")

# Long form only
app.define_flag("--debug", help_text="Enable debug mode")
```

### ParamType Enum

```python
from cliparse import ParamType

ParamType.STRING       # Text (default)
ParamType.INTEGER      # Whole numbers
ParamType.FLOAT        # Decimal numbers
ParamType.BOOLEAN      # True/False
ParamType.PATH         # File paths (returns Path object)
ParamType.CHOICE       # Limited set (use with choices=)
ParamType.MULTI        # Multiple values (use with multi=True)
```

### Parameter Groups

```python
# Create a group
app.create_group("Processing Options", "Options for data processing")

# Subsequent definitions belong to this group
app.define_param("--format", ...)
app.define_param("--threads", ...)

# Create another group
app.create_group("Output Options")
app.define_param("--output", ...)
```

### Validation Constraints

**Forbid parameters together:**
```python
app.define_flag("verbose")
app.define_flag("quiet")
app.forbid_together("verbose", "quiet")
```

**Require at least one:**
```python
app.define_param("--input-file")
app.define_param("--input-dir")
app.require_one_of("--input-file", "--input-dir")
```

**Conditional requirements:**
```python
app.define_flag("encrypt")
app.define_param("--key-file")
app.require_if("encrypt", ["--key-file"])
```

**Custom constraints:**
```python
def validate_config(config):
    if config['threads'] > 4 and config.get('memory', 0) < 8:
        raise ValidationError("High thread count requires 8GB+ memory")
    return True

app.add_constraint(validate_config)
```

### Parsing

```python
# Parse sys.argv
config = app.parse()

# Parse specific arguments
config = app.parse(["file.txt", "--count", "5", "-v"])

# Access values
print(config['filename'])
print(config['count'])
print(config['verbose'])
```

Returns a dictionary where:
- Parameter names become keys (with `--` stripped and `-` replaced with `_`)
- Values are coerced to the specified `param_type`
- Missing optional parameters have their `default` value
- Flags are `True` if present, `False` otherwise

### Exception Handling

```python
from cliparse import ValidationError

try:
    config = app.parse()
except ValidationError as e:
    print(f"Error: {e}")
    app.show_help()
    sys.exit(1)
```

## Usage Examples

### File Processor

```python
from cliparse import CliApp, ParamType

app = CliApp(name="processor", version="1.0.0", 
             description="Process data files")

app.define_param("input", required=True, param_type=ParamType.PATH,
                 help_text="Input file to process")
app.define_param("--output", short="o", param_type=ParamType.PATH,
                 help_text="Output file (default: stdout)")

app.create_group("Processing Options")
app.define_param("--format", param_type=ParamType.CHOICE,
                 choices=["json", "csv", "xml"], default="json",
                 help_text="Output format")
app.define_param("--threads", short="t", param_type=ParamType.INTEGER,
                 default=4, help_text="Number of worker threads")

app.define_flag("verbose", short="v", help_text="Verbose output")
app.define_flag("--debug", help_text="Debug mode")

config = app.parse()

# Use the config
process_file(
    input_file=config['input'],
    output_file=config.get('output'),
    format=config['format'],
    threads=config['threads'],
    verbose=config['verbose']
)
```

### With Constraints

```python
app = CliApp(name="backup", version="1.0.0")

app.define_param("--local-dir", help_text="Local directory")
app.define_param("--remote-url", help_text="Remote URL")
app.define_param("--s3-bucket", help_text="S3 bucket")

# Must specify exactly one backup target
app.require_one_of("--local-dir", "--remote-url", "--s3-bucket")

app.define_flag("encrypt", help_text="Encrypt backup")
app.define_param("--key-file", help_text="Encryption key")

# If encrypting, key is required
app.require_if("encrypt", ["--key-file"])

config = app.parse()
```

### Environment Variable Fallback

```python
app = CliApp(name="api-client", version="1.0.0")

app.define_param("--api-key", env_var="API_KEY", required=True,
                 help_text="API key (or set API_KEY env var)")
app.define_param("--api-url", env_var="API_URL",
                 default="https://api.example.com",
                 help_text="API URL")

# If --api-key not provided, falls back to API_KEY environment variable
config = app.parse()
```

## Help Output

CliParse generates beautiful, organized help:

```
➤ PROCESSOR v1.0.0
  Process data files

USAGE:
  processor [OPTIONS] [PARAMETERS]

OPTIONS:
  input                          Input file to process
  -o, --output                   Output file (default: stdout)

Processing Options:
  -f, --format                   Output format
  -t, --threads                  Number of worker threads

  -v, verbose                    Verbose output
  --debug                        Debug mode
  -h, --help                     Show help message
```

## Implementation Notes

- Positional parameters are identified by names not starting with `-`
- The `dest` name (dictionary key) is derived from parameter name: strips `--`, replaces `-` with `_`
- Short flags are automatically added to the parameter's `all_flags` set
- Multi-value parameters are not fully implemented in current parsing logic
- Type coercion happens automatically based on `param_type`
- Boolean flags don't take values; their presence sets them to `True`

## Comparison with argparse

**What's different:**
- Naming: `CliApp`, `define_param`, `define_flag` (not `ArgumentParser`, `add_argument`)
- Types: Type-safe `ParamType` enum instead of string names
- Flags: Separate `define_flag()` method for boolean flags
- Constraints: Rich semantic validation (forbid, require, conditional)
- Output: Colored, emoji-enhanced help messages
- Groups: More descriptive with better organization

**What's similar:**
- Both support positional and optional arguments
- Both have short flags (`-v`)
- Both generate help automatically
- Both are zero-dependency

## License

Custom License - See LICENSE file for details.

## Author

S0meR4nd0mGuy

Version: 2.0.0