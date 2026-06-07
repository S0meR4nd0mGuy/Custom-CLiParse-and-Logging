"""
Advanced example using CliParse.
Demonstrates all major features of the modern CLI parser.
"""
import cliparse
from cliparse import CliApp, ParamType, ValidationError
import sys


def main():
    # Create application
    app = CliApp(
        name="datamunger",
        version="2.1.0",
        description="Advanced data processing and transformation tool",
        enable_color=True
    )
    
    # Main parameters
    app.define_param("input_file", required=True, help_text="File to process")
    app.define_param("--output", short="o", help_text="Output destination (default: stdout)")
    
    # Processing group
    app.create_group("Processing Options", "Control how data is processed")
    app.define_param("--format", short="f", param_type=ParamType.CHOICE,
                     choices=["json", "csv", "xml", "parquet"],
                     default="json", help_text="Output format")
    app.define_param("--encoding", default="utf-8", help_text="Text encoding")
    app.define_param("--batch-size", short="b", param_type=ParamType.INTEGER,
                     default=1000, help_text="Process batch size")
    
    # Performance group
    app.create_group("Performance", "Optimize processing speed")
    app.define_param("--threads", short="t", param_type=ParamType.INTEGER,
                     default=1, choices=[1, 2, 4, 8, 16],
                     help_text="Worker threads")
    app.define_param("--cache-size", param_type=ParamType.INTEGER,
                     default=100, help_text="Cache size in MB")
    app.define_flag("parallel", short="p", help_text="Enable parallel processing")
    
    # Validation group
    app.create_group("Validation", "Data validation options")
    app.define_flag("strict", short="s", help_text="Strict validation mode")
    app.define_flag("skip_errors", help_text="Continue on errors")
    app.define_param("--max-errors", short="e", param_type=ParamType.INTEGER,
                     default=-1, help_text="Maximum errors before stopping (-1 = unlimited)")
    
    # Output group
    app.create_group("Output", "Control output generation")
    app.define_flag("verbose", short="v", help_text="Detailed output")
    app.define_flag("quiet", short="q", help_text="Minimal output")
    app.define_flag("colored", help_text="Colored output (default: auto)")
    app.define_param("--log-file", help_text="Write logs to file")
    
    # Advanced features
    app.create_group("Advanced", "Expert options")
    app.define_param("--config", env_var="MUNGER_CONFIG",
                     help_text="Configuration file (or MUNGER_CONFIG env var)")
    app.define_param("--define", short="d", multi=True, help_text="Define variables")
    app.define_flag("dry_run", help_text="Simulate without making changes")
    app.define_flag("debug", help_text="Debug mode")
    
    # Add constraints
    app.forbid_together("quiet", "verbose")  # Can't use both
    app.forbid_together("quiet", "log_file")  # Quiet conflicts with logging
    
    # Custom validator
    def validate_batch_size(config):
        batch = config.get('batch_size', 1000)
        if batch < 1 or batch > 1000000:
            raise ValidationError("Batch size must be between 1 and 1,000,000")
        return True
    
    app.add_constraint(validate_batch_size)
    
    # Parse arguments
    try:
        config = app.parse()
    except ValidationError as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)
    
    # Display configuration
    print("\n" + "=" * 70)
    print("⚙️  DATA MUNGER CONFIGURATION")
    print("=" * 70 + "\n")
    
    print(f"📄 Input:              {config['input_file']}")
    print(f"📤 Output:             {config.get('output', '(stdout)')}")
    print(f"📊 Format:             {config['format']}")
    print(f"🔤 Encoding:           {config['encoding']}")
    print(f"📦 Batch Size:         {config['batch_size']:,}")
    
    print()
    print(f"⚡ Performance Settings:")
    print(f"  • Threads:           {config['threads']}")
    print(f"  • Cache Size:        {config['cache_size']} MB")
    print(f"  • Parallel:          {'Yes ✓' if config['parallel'] else 'No'}")
    
    print()
    print(f"✔️  Validation Settings:")
    print(f"  • Strict Mode:       {'Yes ✓' if config['strict'] else 'No'}")
    print(f"  • Skip Errors:       {'Yes ✓' if config['skip_errors'] else 'No'}")
    print(f"  • Max Errors:        {config['max_errors'] if config['max_errors'] > 0 else 'Unlimited'}")
    
    print()
    print(f"🎯 Output Settings:")
    print(f"  • Verbose:           {'Yes ✓' if config['verbose'] else 'No'}")
    print(f"  • Quiet:             {'Yes ✓' if config['quiet'] else 'No'}")
    print(f"  • Colored:           {'Yes ✓' if config['colored'] else 'No'}")
    if config.get('log_file'):
        print(f"  • Log File:          {config['log_file']}")
    
    print()
    print(f"🔧 Advanced:")
    if config.get('config'):
        print(f"  • Config File:       {config['config']}")
    if config.get('define'):
        print(f"  • Variables:         {', '.join(config['define'])}")
    print(f"  • Dry Run:           {'Yes ✓' if config['dry_run'] else 'No'}")
    print(f"  • Debug:             {'Yes ✓' if config['debug'] else 'No'}")
    
    print("\n" + "=" * 70)
    print("✅ Configuration validated and ready to process!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
