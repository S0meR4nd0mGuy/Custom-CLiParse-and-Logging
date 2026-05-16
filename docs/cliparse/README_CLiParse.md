# CliParse - Modern CLI Argument Parser

**A lightweight, powerful Python CLI argument parser with a modern API and rich terminal features. Completely different from argparse with unique naming, advanced constraints, and beautiful styling.**

## 🎯 Why CliParse?

CliParse is **not** a copy of argparse - it's a complete redesign with a unique, intuitive API:

| Feature | argparse | CliParse |
|---------|----------|----------|
| **Main Class** | `ArgumentParser` | `CliApp` |
| **Define** | `add_argument()` | `define_param()` / `define_flag()` |
| **Types** | String types ("int", "float") | `ParamType` enum |
| **Constraints** | Very limited | Rich: forbid, require, custom |
| **Colors** | ❌ | ✅ ANSI colors |
| **Emojis** | ❌ | ✅ Visual indicators |
| **Transformers** | Limited | Full support |
| **Learning Curve** | Steep | Gentle |
| **Dependencies** | 0 | 0 |

## ✨ Key Features

✅ **Distinct API** - Not a copy, unique naming and structure  
✅ **Type Safety** - `ParamType` enum prevents typos  
✅ **Advanced Constraints** - Dependencies, conflicts, custom validation  
✅ **Rich Terminal Features** - Colors, emojis, organized groups  
✅ **Transformer Functions** - Custom type conversion  
✅ **Environment Variable Fallback** - Automatic env var support  
✅ **Parameter Groups** - Organize related parameters  
✅ **Multi-Value Support** - Accept multiple values  
✅ **Zero Dependencies** - Pure Python stdlib only  
✅ **Production Ready** - Fully tested and documented  

## 🚀 Quick Start

### Installation
```python
from cliparse import CliApp, ParamType
```

### One-Minute Example
```python
from cliparse import CliApp, ParamType

app = CliApp(name="hello", version="1.0.0")

app.define_param("name", required=True)
app.define_param("--count", short="c", param_type=ParamType.INTEGER, default=1)
app.define_flag("verbose", short="v")

config = app.parse()
print(f"Hello {config['name']}!" * config['count'])
```

Run: `python hello.py Alice -c 3 -v`

### Advanced Example
```python
from cliparse import CliApp, ParamType, ValidationError

app = CliApp(name="processor", version="2.0.0")

# Input file
app.define_param("input_file", required=True, param_type=ParamType.PATH)

# Processing group
app.create_group("Processing", "Control processing behavior")
app.define_param("--format", param_type=ParamType.CHOICE,
                 choices=["json", "csv", "xml"], default="json")
app.define_param("--threads", short="t", param_type=ParamType.INTEGER, default=4)

# Flags
app.define_flag("verbose", short="v")
app.define_flag("quiet", short="q")

# Constraints
app.forbid_together("verbose", "quiet")

# Custom validation
def validate_config(config):
    if config['format'] == 'xml' and config['threads'] > 2:
        raise ValidationError("XML format only supports 1-2 threads")
    return True

app.add_constraint(validate_config)

# Parse and use
config = app.parse()
print(f"Processing {config['input_file']} as {config['format']} with {config['threads']} threads")
```

## 📚 Complete API Reference

### CliApp - Main Class

#### Constructor
```python
app = CliApp(
    name="myapp",              # Application name
    version="1.0.0",           # Version string
    description="My app",      # Help description
    auto_help=True,            # Auto add -h/--help
    enable_color=True          # Use colors
)
```

#### Methods

##### `define_param(name, **kwargs)`
Define a parameter (positional or optional).

```python
app.define_param(
    name,                         # "filename" (positional) or "--output" (optional)
    aliases=(),                   # Alternative names
    short="o",                    # Short flag like "-o"
    param_type=ParamType.STRING,  # Type of value
    required=False,               # Must be provided
    help_text="",                 # Help description
    default=None,                 # Default value
    choices=None,                 # Allowed values
    validator=None,               # Custom validation function
    transformer=None,             # Transform input
    env_var=None,                 # Environment variable fallback
    multi=False,                  # Accept multiple values
    hidden=False                  # Hide from help
)
```

Examples:
```python
# Positional parameter
app.define_param("filename", required=True)

# Optional with short flag
app.define_param("--output", short="o")

# With type
app.define_param("--count", param_type=ParamType.INTEGER)

# With choices
app.define_param("--format", param_type=ParamType.CHOICE, 
                 choices=["json", "csv", "xml"])

# With default
app.define_param("--threads", param_type=ParamType.INTEGER, default=4)

# With validator
def validate_port(value):
    if not (1 <= value <= 65535):
        raise ValueError("Port must be 1-65535")
    return True

app.define_param("--port", param_type=ParamType.INTEGER, validator=validate_port)

# With transformer (custom conversion)
from pathlib import Path
app.define_param("--input", transformer=lambda v: Path(v))

# Multi-value
app.define_param("--include", multi=True)  # Can use multiple times

# Environment variable fallback
app.define_param("--api-key", env_var="API_KEY")
```

##### `define_flag(name, **kwargs)`
Define a boolean flag.

```python
app.define_flag(
    name,              # "verbose" or "--debug"
    aliases=(),        # Alternative names
    short="v",         # Short flag like "-v"
    help_text="",      # Help description
    default=False,     # Default value
    hidden=False       # Hide from help
)
```

Examples:
```python
app.define_flag("verbose", short="v")
app.define_flag("quiet", short="q")
app.define_flag("debug")
```

##### `create_group(name, description="")`
Create an organizational group for parameters.

```python
app.create_group("Processing", "Data processing options")
# Subsequent define_param/define_flag calls belong to this group
app.define_param("--format", ...)
app.define_param("--threads", ...)

app.create_group("Output", "Output options")
app.define_param("--output", ...)
```

##### Constraint Methods

**`forbid_together(*param_names)`** - Parameters cannot be used together
```python
app.forbid_together("verbose", "quiet")
app.forbid_together("--dev", "--prod")
```

**`require_one_of(*param_names)`** - At least one required
```python
app.require_one_of("--input-file", "--input-dir")
```

**`require_if(trigger, required)`** - Conditional requirement
```python
app.require_if("--encrypt", "--key-file")  # If encrypt, need key-file
```

**`add_constraint(validator)`** - Custom constraint
```python
def my_constraint(config):
    if config['threads'] > 4 and config.get('memory') < 8:
        raise ValidationError("High thread count needs 8GB+ memory")
    return True

app.add_constraint(my_constraint)
```

##### Output Methods

**`parse(args=None)`** - Parse arguments
```python
config = app.parse()                    # Parse sys.argv
config = app.parse(["file.txt", "-v"])  # Parse specific args
```

Returns: `dict` with parameter values  
Raises: `ValidationError` on validation failure

**`show_help()`** - Display colored help
```python
app.show_help()
```

**`get_help_text()`** - Get help as string
```python
help_str = app.get_help_text()
```

### ParamType Enum

Type system for type-safe parameters:

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

### Exceptions

**`ValidationError`** - Validation failed
```python
from cliparse import ValidationError

try:
    config = app.parse()
except ValidationError as e:
    print(f"Invalid arguments: {e}")
```

## 🎨 Output Examples

### Help Output (with colors)
```
➤ PROCESSOR v2.0.0
  Advanced data processor

USAGE:
  processor [OPTIONS] input_file

OPTIONS:
  input_file                     Input file to process
  -o, --output                   Output file

Processing:
  -f, --format                   Output format
  -t, --threads                  Worker threads

⚙️  CONFIGURATION
📄 Input:     data.csv
📤 Output:    result.json
⚡ Threads:   4
✅ Validated!
```

## 🔴 Common Patterns

### Pattern 1: Input/Output Files
```python
app.define_param("input", required=True, param_type=ParamType.PATH)
app.define_param("--output", short="o", param_type=ParamType.PATH)

config = app.parse()
input_path = config['input']
output_path = config.get('output')
```

### Pattern 2: Processing Options
```python
app.create_group("Processing", "Processing settings")
app.define_param("--format", param_type=ParamType.CHOICE,
                 choices=["json", "csv", "xml"])
app.define_param("--threads", param_type=ParamType.INTEGER, default=4)
app.define_flag("parallel")
```

### Pattern 3: Verbosity Levels
```python
app.define_flag("quiet", short="q")
app.define_flag("verbose", short="v")

app.forbid_together("quiet", "verbose")

config = app.parse()
if config['quiet']:
    level = "quiet"
elif config['verbose']:
    level = "verbose"
else:
    level = "normal"
```

### Pattern 4: Mutually Exclusive Options
```python
app.create_group("Source", "Data source")
app.define_param("--local-dir")
app.define_param("--remote-url")
app.define_param("--s3-bucket")

app.require_one_of("--local-dir", "--remote-url", "--s3-bucket")
```

### Pattern 5: Dependent Options
```python
app.define_flag("encrypt")
app.define_param("--key-file")

app.require_if("encrypt", "--key-file")

config = app.parse()
if config['encrypt']:
    key = config['key_file']  # Guaranteed to exist
```

### Pattern 6: Environment Variables
```python
app.define_param("--api-key", env_var="API_KEY")
app.define_param("--api-url", env_var="API_URL", 
                 default="https://api.example.com")

config = app.parse()
# Can come from CLI or environment variables
```

### Pattern 7: Multi-Value Parameters
```python
app.define_param("--include", multi=True)

config = app.parse()
# With: program --include a.txt --include b.txt --include c.txt
# Result: config['include'] = ['a.txt', 'b.txt', 'c.txt']
```

### Pattern 8: Custom Type Conversion
```python
from pathlib import Path
from datetime import datetime

def to_path(value):
    path = Path(value)
    if not path.exists():
        raise ValueError(f"File not found: {value}")
    return path

def parse_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"Invalid date: {value}")

app.define_param("--input", transformer=to_path)
app.define_param("--since", transformer=parse_date)
```

## 📋 Real-World Examples

### Example 1: File Converter
```python
from cliparse import CliApp, ParamType

app = CliApp(name="converter", version="1.0.0")

app.define_param("input_file", param_type=ParamType.PATH)
app.define_param("--output", short="o", param_type=ParamType.PATH)
app.define_param("--format", param_type=ParamType.CHOICE,
                 choices=["json", "csv", "xml"])
app.define_flag("verbose", short="v")

config = app.parse()

input_data = read_file(config['input_file'], config['format'])
if config.get('output'):
    write_file(config['output'], input_data)
else:
    print(input_data)
```

### Example 2: Data Processor
```python
app = CliApp(name="processor", version="2.0.0")

app.define_param("data_file", param_type=ParamType.PATH)

app.create_group("Processing", "Processing options")
app.define_param("--format", param_type=ParamType.CHOICE,
                 choices=["json", "csv", "xml"], default="json")
app.define_param("--threads", param_type=ParamType.INTEGER, default=4)
app.define_param("--batch-size", param_type=ParamType.INTEGER, default=1000)

app.create_group("Output", "Output options")
app.define_param("--output", short="o", param_type=ParamType.PATH)
app.define_flag("quiet", short="q")

app.forbid_together("quiet", "--output")

config = app.parse()

processor = DataProcessor(
    format=config['format'],
    threads=config['threads'],
    batch_size=config['batch_size']
)

result = processor.process(config['data_file'])

if config.get('output'):
    write_result(config['output'], result)
```

### Example 3: Deployment Tool
```python
app = CliApp(name="deployer", version="3.0.0")

app.create_group("Target", "Deployment target")
app.define_flag("dev")
app.define_flag("staging")
app.define_flag("prod")

app.create_group("Options", "Deployment options")
app.define_flag("skip-tests")
app.define_flag("force", short="f")

app.require_one_of("dev", "staging", "prod")

def validate_force(config):
    if config['force'] and not config['dev']:
        raise ValidationError("Can only force deploy to dev")
    return True

app.add_constraint(validate_force)

config = app.parse()

target = "dev" if config['dev'] else ("staging" if config['staging'] else "prod")

if not config['skip_tests']:
    run_tests()

deploy(target, force=config['force'])
```

## 🔧 Advanced Features

### Custom Validators
```python
def validate_port(value):
    if not (1 <= value <= 65535):
        raise ValueError("Port must be 1-65535")
    return True

app.define_param("--port", validator=validate_port)
```

### Custom Transformers
```python
def to_int_list(value):
    return [int(x) for x in value.split(",")]

app.define_param("--numbers", transformer=to_int_list)
# Usage: --numbers 1,2,3,4,5
```

### Complex Constraints
```python
def validate_database_config(config):
    if config.get('db_type') == 'postgresql':
        if not config.get('db_port'):
            raise ValidationError("PostgreSQL requires --db-port")
        if config['db_port'] != 5432:
            raise ValidationError("PostgreSQL default port is 5432")
    return True

app.add_constraint(validate_database_config)
```

## ✅ Features Summary

### Parameters
- ✅ Positional and optional
- ✅ Required/optional
- ✅ Defaults
- ✅ Choices (validation)
- ✅ Multi-value
- ✅ Environment variable fallback
- ✅ Custom types via ParamType
- ✅ Custom transformers
- ✅ Custom validators
- ✅ Aliases/short flags
- ✅ Help text
- ✅ Grouping

### Flags
- ✅ Boolean flags
- ✅ Short forms (-v)
- ✅ Aliases
- ✅ Help text
- ✅ Defaults
- ✅ Grouping

### Constraints
- ✅ forbid_together
- ✅ require_one_of
- ✅ require_if
- ✅ Custom constraints
- ✅ Detailed error messages

### Output
- ✅ Colored help
- ✅ Emoji indicators
- ✅ Organized groups
- ✅ Clean dict output
- ✅ Structured errors

## 📈 Project Stats

- **Core Module**: 551 lines
- **Examples**: 2 working applications
- **Features**: 25+
- **Dependencies**: 0 (pure stdlib)
- **Python**: 3.6+

## 🎓 Learning Path

1. **Quick Start** - Read this README's "Quick Start"
2. **Examples** - Look at example files
3. **API Reference** - Read full API above
4. **Try It** - Build your first CLI app

## 🚀 Next Steps

1. Copy `cliparse.py` to your project
2. Import: `from cliparse import CliApp, ParamType`
3. Define your CLI with `app.define_param()` and `app.define_flag()`
4. Parse: `config = app.parse()`
5. Use the config dict!

## 📝 Notes

- **Python 3.6+** required (f-strings, type hints)
- **Zero dependencies** - pure Python stdlib
- **BSD-like license** - free to use and modify
- **Production-ready** - fully tested
- **Fully typed** - excellent IDE support

---

**CliParse** - Modern CLI parsing made simple.
