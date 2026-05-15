# CliParse Usage Guide & Recipes

Complete guide with patterns and recipes for using CliParse in your applications.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Common Patterns](#common-patterns)
3. [Validation & Constraints](#validation--constraints)
4. [Advanced Recipes](#advanced-recipes)
5. [Real-World Examples](#real-world-examples)
6. [Troubleshooting](#troubleshooting)

## Getting Started

### Basic Structure

Every CliParse application follows this pattern (Please not that those flags (and patterns) are just examples, feel free to experiment around!):

```python
from cliparse import CliApp, ParamType

# 1. Create app
app = CliApp(name="myapp", version="1.0.0", description="My app")

# 2. Define parameters and flags
app.define_param("filename", required=True)
app.define_flag("verbose", short="v")

# 3. Parse arguments
config = app.parse()

# 4. Use the config dict
print(f"Processing {config['filename']}")
if config['verbose']:
    print("Verbose mode enabled")
```

### Parameter Naming

- **Positional**: `app.define_param("filename")` → `config['filename']`
- **Optional**: `app.define_param("--output")` → `config['output']` (dashes removed)
- **Hyphens to underscores**: `--max-threads` → `config['max_threads']`
- **Flags**: `app.define_flag("verbose")` → `config['verbose']`

## Common Patterns

### Pattern 1: Input/Output Files

```python
app = CliApp(name="converter")

# Input file (required)
app.define_param("input", required=True, param_type=ParamType.PATH,
                help_text="Input file to process")

# Output file (optional, defaults to stdout)
app.define_param("--output", short="o", param_type=ParamType.PATH,
                help_text="Output file (default: stdout)")

config = app.parse()

input_path = config['input']
output_path = config.get('output')  # May be None

if output_path:
    with open(output_path, 'w') as f:
        f.write("result")
else:
    print("result")
```

### Pattern 2: Processing Configuration

```python
app = CliApp(name="processor")

# Create a group for all processing options
app.create_group("Processing", "Data processing settings")

app.define_param("--format", param_type=ParamType.CHOICE,
                choices=["json", "csv", "xml"], default="json")

app.define_param("--threads", short="t", param_type=ParamType.INTEGER,
                default=4, help_text="Number of worker threads")

app.define_param("--batch-size", short="b", param_type=ParamType.INTEGER,
                default=1000)

app.define_flag("parallel", short="p", help_text="Enable parallel mode")

config = app.parse()

# Access with proper naming
format_type = config['format']
num_threads = config['threads']
batch = config['batch_size']
is_parallel = config['parallel']
```

### Pattern 3: Verbosity Levels

```python
app = CliApp(name="tool")

app.define_flag("quiet", short="q", help_text="No output")
app.define_flag("verbose", short="v", help_text="Detailed output")
app.define_flag("very_verbose", short="vv", help_text="Very detailed")

# Constraint: Can't use multiple verbosity flags
app.forbid_together("quiet", "verbose")
app.forbid_together("quiet", "very_verbose")
app.forbid_together("verbose", "very_verbose")

config = app.parse()

if config['quiet']:
    level = 0
elif config['very_verbose']:
    level = 2
elif config['verbose']:
    level = 1
else:
    level = 0
```

### Pattern 4: Mutually Exclusive Options

```python
app = CliApp(name="syncer")

app.create_group("Source", "Where to sync from")
app.define_param("--local-dir", help_text="Local directory")
app.define_param("--remote-url", help_text="Remote URL")
app.define_param("--s3-bucket", help_text="S3 bucket")

# Constraint: Choose exactly one source
app.require_one_of("--local-dir", "--remote-url", "--s3-bucket")

config = app.parse()

if config.get('local_dir'):
    source = config['local_dir']
elif config.get('remote_url'):
    source = config['remote_url']
else:
    source = config['s3_bucket']
```

### Pattern 5: Dependent Options

```python
app = CliApp(name="secure")

app.define_flag("encrypt", help_text="Enable encryption")
app.define_param("--key-file", help_text="Encryption key file")

# Constraint: If --encrypt, then --key-file required
app.require_if("encrypt", "--key-file")

config = app.parse()

if config['encrypt']:
    key = config['key_file']  # Guaranteed to exist
```

### Pattern 6: Multi-Value Parameters

```python
app = CliApp(name="bundler")

# Accept multiple input files
app.define_param("--include", short="i", multi=True,
                help_text="Files to include (can use multiple times)")

config = app.parse()

# config['include'] is a list
for file in config['include']:
    print(f"Including: {file}")
```

Usage: `python bundler.py -i file1.txt -i file2.txt -i file3.txt`

## Validation & Constraints

### Built-In Constraints

#### forbid_together()

Parameters cannot be used together:

```python
app.forbid_together("--dev", "--prod")
app.forbid_together("--quiet", "--verbose")
```

#### require_one_of()

At least one parameter must be provided:

```python
app.require_one_of("--input", "--stdin")
app.require_one_of("--format-json", "--format-csv", "--format-xml")
```

#### require_if()

If one is provided, another is required:

```python
app.require_if("--enable-ssl", "--cert-file")
app.require_if("--use-cache", "--cache-dir")
```

### Custom Validators

Validator functions validate individual parameter values:

```python
def validate_port(value):
    """Validate port is in valid range."""
    try:
        port = int(value)
    except ValueError:
        raise ValidationError(f"Port must be a number, got: {value}")
    
    if not (1 <= port <= 65535):
        raise ValidationError(f"Port must be 1-65535, got: {port}")
    
    return True

app.define_param("--port", validator=validate_port)
```

### Custom Constraints

Constraint functions validate the entire configuration:

```python
def validate_memory_settings(config):
    """Validate memory settings are consistent."""
    if config['threads'] > 4 and not config.get('memory_gb'):
        raise ValidationError(
            "Must specify --memory-gb when using > 4 threads"
        )
    
    if config.get('memory_gb') and config['memory_gb'] < config['threads']:
        raise ValidationError(
            "Memory GB must be >= number of threads"
        )
    
    return True

app.add_constraint(validate_memory_settings)
```

### Validation with Error Handling

```python
from cliparse import ValidationError
import sys

app = CliApp(name="myapp")
# ... define parameters ...

try:
    config = app.parse()
except ValidationError as e:
    print(f"❌ Invalid arguments: {e}", file=sys.stderr)
    print("\nRun with --help for usage information", file=sys.stderr)
    sys.exit(1)

# Process with valid config
# ...
```

## Advanced Recipes

### Recipe 1: Custom Type Conversion

```python
from pathlib import Path
from datetime import datetime
from cliparse import ParamType

app = CliApp(name="analyzer")

# Path with validation
def to_existing_path(value):
    path = Path(value)
    if not path.exists():
        raise ValidationError(f"Path does not exist: {value}")
    return path

app.define_param("--input", transformer=to_existing_path)

# Date parsing
def parse_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        raise ValidationError(f"Date must be YYYY-MM-DD, got: {value}")

app.define_param("--since", transformer=parse_date)

config = app.parse()
input_path: Path = config['input']
since_date: datetime = config['since']
```

### Recipe 2: Environment Variables with Defaults

```python
app = CliApp(name="api_client")

app.define_param("--api-key", env_var="API_KEY",
                help_text="API key (or API_KEY env var)")
app.define_param("--api-url", env_var="API_URL",
                default="https://api.example.com",
                help_text="API endpoint")

config = app.parse()

# If not provided on CLI, comes from env var or default
api_key = config['api_key']  # Could be from --api-key or $API_KEY
api_url = config['api_url']  # Could be from env var or default
```

### Recipe 3: Conditional Processing

```python
app = CliApp(name="deployer")

app.create_group("Deploy Target", "Where to deploy")
app.define_flag("dev", help_text="Deploy to development")
app.define_flag("staging", help_text="Deploy to staging")
app.define_flag("prod", help_text="Deploy to production")

app.require_one_of("dev", "staging", "prod")

app.create_group("Deploy Options", "How to deploy")
app.define_flag("skip_tests", help_text="Skip test suite")
app.define_flag("force", short="f", help_text="Force deploy")

# Only allow force on dev
def validate_force(config):
    if config['force'] and not config['dev']:
        raise ValidationError("--force only allowed for --dev deployment")
    return True

app.add_constraint(validate_force)

config = app.parse()

# Conditional processing
target = "dev" if config['dev'] else ("staging" if config['staging'] else "prod")

if not config['skip_tests']:
    print("Running tests...")

if config['force']:
    print("Force deploying...")

print(f"Deploying to {target}...")
```

### Recipe 4: Configuration File + CLI Override

```python
import json
from pathlib import Path

app = CliApp(name="processor")

app.define_param("--config", param_type=ParamType.PATH,
                help_text="Configuration file (JSON)")
app.define_param("--threads", short="t", param_type=ParamType.INTEGER,
                help_text="Override config threads")

config = app.parse()

# Load configuration
final_config = {}

if config.get('config'):
    with open(config['config']) as f:
        final_config = json.load(f)

# CLI arguments override config file
if config.get('threads'):
    final_config['threads'] = config['threads']

# Use merged configuration
threads = final_config.get('threads', 4)
```

### Recipe 5: Subcommand-like Behavior

```python
app = CliApp(name="cli")

# First positional parameter acts like subcommand
app.define_param("action", required=True, 
                param_type=ParamType.CHOICE,
                choices=["start", "stop", "restart", "status"])

# Optional parameters work for all actions
app.define_param("--service", required=True)
app.define_flag("force", short="f")

config = app.parse()

action = config['action']
service = config['service']

if action == "start":
    print(f"Starting {service}")
elif action == "stop":
    print(f"Stopping {service}")
elif action == "restart":
    print(f"Restarting {service}")
    if config['force']:
        print("  (force)")
elif action == "status":
    print(f"Status of {service}")
```

## Real-World Examples

### Example 1: Data Processing Tool

```python
from cliparse import CliApp, ParamType, ValidationError
import sys

app = CliApp(
    name="datapro",
    version="2.0.0",
    description="Professional data processing tool"
)

# Data source
app.define_param("input", required=True, param_type=ParamType.PATH)
app.define_param("--output", param_type=ParamType.PATH)

# Processing
app.create_group("Processing", "How to process data")
app.define_param("--format", param_type=ParamType.CHOICE,
                choices=["json", "csv", "xml", "parquet"], default="json")
app.define_param("--encoding", default="utf-8")
app.define_param("--batch", short="b", param_type=ParamType.INTEGER, default=1000)

# Performance
app.create_group("Performance", "Optimization")
app.define_param("--threads", short="t", param_type=ParamType.INTEGER, default=4)
app.define_flag("parallel", short="p")

# Output
app.create_group("Output", "Output settings")
app.define_flag("verbose", short="v")
app.define_flag("quiet", short="q")

# Constraints
app.forbid_together("verbose", "quiet")

def validate_config(config):
    if config['batch'] < 1:
        raise ValidationError("Batch size must be > 0")
    if config['threads'] < 1 or config['threads'] > 64:
        raise ValidationError("Threads must be 1-64")
    return True

app.add_constraint(validate_config)

try:
    config = app.parse()
except ValidationError as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)

print(f"Processing {config['input']}")
print(f"  Format: {config['format']}")
print(f"  Threads: {config['threads']}")
if config['output']:
    print(f"  Output: {config['output']}")
```

### Example 2: API Client Configuration

```python
from cliparse import CliApp, ParamType, ValidationError
import sys

app = CliApp(name="api-client", version="1.0.0")

# Required
app.define_param("--endpoint", required=True,
                help_text="API endpoint URL")
app.define_param("--api-key", env_var="API_KEY", required=True,
                help_text="API key (or API_KEY env var)")

# Optional
app.define_param("--timeout", param_type=ParamType.INTEGER, default=30)
app.define_flag("verify-ssl", default=True)

# Request options
app.create_group("Request", "HTTP request options")
app.define_param("--method", param_type=ParamType.CHOICE,
                choices=["GET", "POST", "PUT", "DELETE"], default="GET")
app.define_param("--content-type", default="application/json")

# Debug
app.create_group("Debug", "Debugging options")
app.define_flag("verbose", short="v")
app.define_flag("dry-run", help_text="Show request without sending")

try:
    config = app.parse()
except ValidationError as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)

# Use configuration
client_config = {
    'endpoint': config['endpoint'],
    'api_key': config['api_key'],
    'timeout': config['timeout'],
    'verify_ssl': config['verify_ssl'],
    'method': config['method'],
    'content_type': config['content_type'],
    'verbose': config['verbose'],
    'dry_run': config['dry_run'],
}

print("API Client Configuration:")
for key, value in client_config.items():
    print(f"  {key}: {value}")
```

## Troubleshooting

### Q: How do I get help?

```bash
python myapp.py --help
```

Help is automatically generated from your parameter definitions.

### Q: Parameters are case-sensitive?

No, parameter names are normalized:
- `--My-Param` becomes `config['my_param']`
- Dashes are converted to underscores
- Case is lowercased

### Q: How do I make a parameter truly optional?

Don't set `required=True`:

```python
app.define_param("--output")  # Optional, None if not provided
```

### Q: How do I set a default value?

Use the `default` parameter:

```python
app.define_param("--threads", param_type=ParamType.INTEGER, default=4)
```

If not provided, `config['threads']` will be `4`.

### Q: How do I get a list of values?

Use `multi=True`:

```python
app.define_param("--include", multi=True)

# Usage: python myapp.py --include file1 --include file2 --include file3
# Result: config['include'] = ['file1', 'file2', 'file3']
```

### Q: Can I use both short and long forms?

Yes:

```python
app.define_param("--verbose", short="v")

# Both work:
# python myapp.py --verbose
# python myapp.py -v
```

### Q: How do I validate file paths?

```python
from pathlib import Path

def to_existing_path(value):
    path = Path(value)
    if not path.exists():
        raise ValidationError(f"Path does not exist: {value}")
    return path

app.define_param("--input", transformer=to_existing_path)
```

### Q: How do I disable colors?

```python
from cliparse import Color

Color.disable()

# Or per-app:
app = CliApp(enable_color=False)
```

### Q: Error message is unclear?

Provide custom error messages in validators:

```python
def validate_port(value):
    try:
        port = int(value)
    except ValueError:
        raise ValidationError(
            f"Port must be a number between 1 and 65535, got: {value}"
        )
    
    if not (1 <= port <= 65535):
        raise ValidationError(
            f"Port {port} is out of valid range (1-65535)"
        )
    
    return True
```

## Next Steps

- Check out the example files for complete working code
- Read the main API documentation in README_CLIPARSE.md
- Experiment with different parameter combinations
- Build your own CLI tools!
