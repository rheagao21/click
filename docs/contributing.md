# Contributing

This is a quick reference for Click-specific development
tasks. For setting up the development environment and the
general contribution workflow, see the Pallets [quick
reference](https://palletsprojects.com/contributing/quick/)
and the [detailed contributing
guide](https://palletsprojects.com/contributing/).

## Extra Test Environments

Click includes some extra test environments:

-   `tox r -e stress` runs stress tests for race conditions
    in Click's test runner.

    ```shell-session
    $ tox r -e stress
    ```

-   `tox r -e random` runs tests in parallel in a random
    order to detect test pollution.

    ```shell-session
    $ tox r -e random
    ```

-   The nightly workflow
    (`.github/workflows/nightly.yaml`) runs Flask's test
    suite against `main` and `stable` to catch downstream
    regressions.

## How Help Pages Are Generated

The default help option is an eager option. During parsing,
{meth}`Command.get_help_option` creates it with
{func}`click.help_option`. Its callback handles `--help` before the command's
callback runs. It calls {meth}`Context.get_help`, writes the returned string to
standard output, and exits successfully. Commands with `no_args_is_help=True`
take a different route through the internal `NoArgsIsHelpError`, but the
exception is initialized from the same {meth}`Context.get_help` result.

The rendering path after that is:

1. {meth}`Context.get_help` delegates to {meth}`Command.get_help`.
2. {meth}`Command.get_help` asks {meth}`Context.make_formatter` for a
   {class}`HelpFormatter`, passes it to {meth}`Command.format_help`, then
   returns the formatter's buffered value.
3. {meth}`Command.format_help` calls the section methods in display order:
   {meth}`~Command.format_usage`, {meth}`~Command.format_help_text`,
   {meth}`~Command.format_arguments`, {meth}`~Command.format_options`, and
   {meth}`~Command.format_epilog`.
4. The usage and parameter sections ask each parameter for its usage pieces or
   help record. {class}`Group` extends the options step with
   {meth}`Group.format_commands`, which gets each command's short help text.
5. The section methods write headings, paragraphs, and definition lists to
   {class}`HelpFormatter`. The formatter performs wrapping and indentation and
   accumulates the final text in memory.

This split determines where a change belongs. Change a parameter's usage or
help-record methods when only that parameter's representation is affected.
Change a command's section method when the contents or ordering of a section is
affected. Change {class}`HelpFormatter` when the low-level layout or wrapping
of all help output is affected. Keep the `--help` callback focused on triggering
and displaying generation rather than formatting it.

## Code Style

Avoid ternary expressions (`x if cond else y`): coverage
cannot measure both branches. Use an explicit `if`/`else`
block instead.

Do not add unnecessary dependencies. If a feature can be
implemented with the standard library, do not pull in an
external package for it.

## Formatting

Wrap lines in Markdown files at 80 characters.
