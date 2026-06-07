"""
Simple example using CliParse - the modern CLI parser.
Shows minimal usage for basic CLI applications.
"""

import cliparse
from cliparse import CliApp, ParamType
import sys


def main():
    # Create app
    app = CliApp(
        name="greeter",
        version="1.0.0",
        description="A simple greeting application"
    )
    
    # Define parameters
    app.define_param("name", required=True, help_text="Person to greet")
    app.define_param("--count", short="c", param_type=ParamType.INTEGER, 
                    default=1, help_text="Number of times to greet")
    
    # Define flags
    app.define_flag("--verbose", short="v", help_text="Show details")
    app.define_flag("--uppercase", short="u", help_text="Use uppercase")
    
    # Parse
    config = app.parse()
    
    greeting = f"Hello, {config['name']}!"
    if config.get('uppercase'):
        greeting = greeting.upper()
    
    if config.get('verbose'):
        print(f"📢 Repeating greeting {config['count']} time(s)...\n")
    
    for i in range(config['count']):
        if config['count'] > 1:
            print(f"  [{i+1}] {greeting}")
        else:
            print(greeting)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Error: {e}", file=__import__('sys').stderr)
        sys.exit(1)
