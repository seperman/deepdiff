import click
import sys
from pprint import pprint
from deepdiff.diff import (
    DeepDiff,
    CUTOFF_DISTANCE_FOR_PAIRS_DEFAULT,
    CUTOFF_INTERSECTION_FOR_PAIRS_DEFAULT,
    logger
)
from deepdiff.serialization import load_path_content


@click.group()
def deepdiff_cli():
    """A simple command line tool."""
    pass


# cutoff_intersection_for_pairs=CUTOFF_INTERSECTION_FOR_PAIRS_DEFAULT,

@deepdiff_cli.command()
@click.argument('t1', type=click.Path(exists=True, resolve_path=True))
@click.argument('t2', type=click.Path(exists=True, resolve_path=True))
@click.option('--cutoff-distance-for-pairs', required=False, default=CUTOFF_DISTANCE_FOR_PAIRS_DEFAULT, type=float, show_default=True)
@click.option('--cutoff-intersection-for-pairs', required=False, default=CUTOFF_INTERSECTION_FOR_PAIRS_DEFAULT, type=float, show_default=True)
@click.option('--cache-size', required=False, default=0, type=int, show_default=True)
@click.option('--cache-tuning-sample-size', required=False, default=0, type=int, show_default=True)
@click.option('--cache-purge-level', required=False, default=1, type=click.IntRange(0, 2), show_default=True)
@click.option('--exclude-paths', required=False, type=str, show_default=False, multiple=True)
@click.option('--exclude-regex-paths', required=False, type=str, show_default=False, multiple=True)
@click.option('--get-deep-distance', is_flag=True, show_default=True)
@click.option('--ignore-order', is_flag=True, show_default=True)
@click.option('--ignore-string-type-changes', is_flag=True, show_default=True)
@click.option('--ignore-numeric-type-changes', is_flag=True, show_default=True)
@click.option('--ignore-type-subclasses', is_flag=True, show_default=True)
@click.option('--ignore-string-case', is_flag=True, show_default=True)
@click.option('--ignore-nan-inequality', is_flag=True, show_default=True)
@click.option('--include-private-variables', is_flag=True, show_default=True)
@click.option('--log-frequency-in-sec', required=False, default=0, type=int, show_default=True)
@click.option('--max-passes', required=False, default=10000000, type=int, show_default=True)
@click.option('--max_diffs', required=False, default=None, type=int, show_default=True)
@click.option('--number-format-notation', required=False, type=click.Choice(['f', 'e'], case_sensitive=True), show_default=True, default="f")
@click.option('--progress-logger', required=False, type=click.Choice(['info', 'error'], case_sensitive=True), show_default=True, default="info")
@click.option('--report-repetition', is_flag=True, show_default=True)
@click.option('--significant-digits', required=False, default=None, type=int, show_default=True)
@click.option('--truncate-datetime', required=False, type=click.Choice(['second', 'minute', 'hour', 'day'], case_sensitive=True), show_default=True, default=None)
@click.option('--verbose-level', required=False, default=1, type=click.IntRange(0, 2), show_default=True)
def diff(
    *args, **kwargs
):
    kwargs['ignore_private_variables'] = not kwargs.pop('include_private_variables')
    kwargs['progress_logger'] = logger.info if kwargs['progress_logger'] == 'info' else logger.error
    t1_path = kwargs.pop("t1")
    t2_path = kwargs.pop("t2")
    try:
        kwargs['t1'] = load_path_content(t1_path)
    except Exception as e:
        sys.exit(str(f"Error when loading t1: {e}"))

    try:
        kwargs['t2'] = load_path_content(t2_path)
    except Exception as e:
        sys.exit(str(f"Error when loading t2: {e}"))

    try:
        diff = DeepDiff(**kwargs)
    except Exception as e:
        sys.exit(str(e))
    pprint(diff, indent=2)
