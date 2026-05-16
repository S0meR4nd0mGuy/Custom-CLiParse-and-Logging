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

#### Core Methods

**`define_param(name, **kwargs)`** - Define a parameter (positional or optional)

```python
app.define_param(
    name,                           # "filename" or "--output"
    aliases=(),                     # Alternative names
    short="o",                      # Short flag like "-o"
    param_type=ParamType.STRING,    # Type of value
    required=False,                 # Must be provided
    help_text="",                   # Help description
    default=None,                   # Default value
    choices=None,                   # Allowed values
    validator=None,                 # Custom validation function
    transformer=None,               # Transform input
    env_var=None,                   # Environment variable fallback
    multi=False,                    # Accept multiple values
    hidden=False                    # Hide from help
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

# Multi-value
app.define_param("--include", multi=True)

# Environment variable fallback
app.define_param("--api-key", env_var="API_KEY")
```

**`define_flag(name, **kwargs)`** - Define a boolean flag

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

**`create_group(name, description="")`** - Create a parameter group

```python
app.create_group("Processing", "Data processing options")
# Subsequent define_param/define_flag calls belong to this group
app.define_param("--format", ...)
app.define_param("--threads", ...)
```

#### Constraint Methods

**`forbid_together(*param_names)`** - Parameters cannot be used together
```python
app.forbid_together("verbose", "quiet")
```

**`require_one_of(*param_names)`** - At least one required
```python
app.require_one_of("--input-file", "--input-dir")
```

**`require_if(trigger, required)`** - Conditional requirement
```python
app.require_if("--encrypt", "--key-file")
```

**`add_constraint(validator)`** - Custom constraint function
```python
def my_constraint(config):
    if config['threads'] > 4 and config.get('memory') < 8:
        raise ValidationError("High threads needs 8GB+ memory")
    return True

app.add_constraint(my_constraint)
```

#### Output Methods

**`parse(args=None)`** - Parse arguments and return config dict
```python
config = app.parse()              # Parse sys.argv
config = app.parse(["file.txt"])  # Parse specific args
```

**`show_help()`** - Display colored help
```python
app.show_help()
```

**`get_help_text()`** - Get help as string
```python
help_str = app.get_help_text()
```

### ParamType Enum

Type-safe parameter types:

```python
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
    print(f"Invalid: {e}")
```

## 🔴 Common Patterns

### Input/Output Files
```python
app.define_param("input", required=True, param_type=ParamType.PATH)
app.define_param("--output", short="o", param_type=ParamType.PATH)

config = app.parse()
process_file(config['input'], config.get('output'))
```

### Processing Options
```python
app.create_group("Processing", "Processing settings")
app.define_param("--format", param_type=ParamType.CHOICE,
                 choices=["json", "csv", "xml"])
app.define_param("--threads", param_type=ParamType.INTEGER, default=4)
```

### Verbosity Levels
```python
app.define_flag("quiet", short="q")
app.define_flag("verbose", short="v")
app.forbid_together("quiet", "verbose")

config = app.parse()
```

### Mutually Exclusive Options
```python
app.define_param("--local-dir")
app.define_param("--remote-url")
app.define_param("--s3-bucket")
app.require_one_of("--local-dir", "--remote-url", "--s3-bucket")
```

### Dependent Options
```python
app.define_flag("encrypt")
app.define_param("--key-file")
app.require_if("encrypt", "--key-file")

config = app.parse()
if config['encrypt']:
    key = config['key_file']  # Guaranteed to exist
```

### Environment Variables
```python
app.define_param("--api-key", env_var="API_KEY")
app.define_param("--api-url", env_var="API_URL", 
                 default="https://api.example.com")
```

### Multi-Value Parameters
```python
app.define_param("--include", multi=True)

# Usage: program --include a.txt --include b.txt
# Result: config['include'] = ['a.txt', 'b.txt']
```

### Custom Type Conversion
```python
from pathlib import Path

def to_path(value):
    path = Path(value)
    if not path.exists():
        raise ValueError(f"File not found: {value}")
    return path

app.define_param("--input", transformer=to_path)
```

## 📋 Real-World Examples

### File Converter
```python
from cliparse import CliApp, ParamType

app = CliApp(name="converter", version="1.0.0")
app.define_param("input_file", param_type=ParamType.PATH)
app.define_param("--output", short="o", param_type=ParamType.PATH)
app.define_param("--format", param_type=ParamType.CHOICE,
                 choices=["json", "csv", "xml"])
app.define_flag("verbose", short="v")

config = app.parse()

input_data = read_file(config['input_file'])
if config.get('output'):
    write_file(config['output'], input_data)
else:
    print(input_data)
```

### Data Processor
```python
app = CliApp(name="processor", version="2.0.0")
app.define_param("data_file", param_type=ParamType.PATH)

app.create_group("Processing", "Processing options")
app.define_param("--format", param_type=ParamType.CHOICE,
                 choices=["json", "csv"], default="json")
app.define_param("--threads", param_type=ParamType.INTEGER, default=4)

app.create_group("Output", "Output options")
app.define_param("--output", short="o", param_type=ParamType.PATH)
app.define_flag("quiet", short="q")

app.forbid_together("quiet", "--output")

config = app.parse()

processor = DataProcessor(
    format=config['format'],
    threads=config['threads']
)
result = processor.process(config['data_file'])

if config.get('output'):
    write_result(config['output'], result)
```

## 🎨 Output Example

```
➤ PROCESSOR v2.0.0
  Advanced data processor

USAGE:
  processor [OPTIONS] input_file

OPTIONS:
  input_file                     Input file
  -o, --output                   Output file

Processing:
  -f, --format                   Output format
  -t, --threads                  Worker threads

✅ Configuration validated!
```

## 📈 Project Stats

- **Core Module**: 551 lines
- **Examples**: 2 working applications
- **Features**: 25+
- **Dependencies**: 0 (pure stdlib)
- **Python**: 3.6+

## 🎓 Quick Links

- **Example Files**: `example_cliparse_simple.py`, `example_cliparse_advanced.py`
- **Source Code**: `cliparse.py` (main module)
- **See Also**: Look at examples for more patterns

## 🚀 Getting Started

1. Copy `cliparse.py` to your project
2. Import: `from cliparse import CliApp, ParamType`
3. Create app: `app = CliApp(name="myapp")`
4. Define params: `app.define_param(...)`
5. Parse: `config = app.parse()`
6. Use config dict!

---

**CliParse** - Modern CLI parsing made simple.
