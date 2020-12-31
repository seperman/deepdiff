import click
import sys
from pprint import pprint
from deepdiff.diff import (
    DeepDiff,
    CUTOFF_DISTANCE_FOR_PAIRS_DEFAULT,
    CUTOFF_INTERSECTION_FOR_PAIRS_DEFAULT,
    logger
)
from deepdiff import Delta, DeepSearch, extract as deep_extract
from deepdiff.serialization import load_path_content, save_content_to_path


@click.group()
def cli():
    """A simple command line tool."""
    pass  # pragma: no cover.


@cli.command()
@click.argument('t1', type=click.Path(exists=True, resolve_path=True))
@click.argument('t2', type=click.Path(exists=True, resolve_path=True))
@click.option('--cutoff-distance-for-pairs', required=False, default=CUTOFF_DISTANCE_FOR_PAIRS_DEFAULT, type=float, show_default=True)
@click.option('--cutoff-intersection-for-pairs', required=False, default=CUTOFF_INTERSECTION_FOR_PAIRS_DEFAULT, type=float, show_default=True)
@click.option('--cache-size', required=False, default=0, type=int, show_default=True)
@click.option('--cache-tuning-sample-size', required=False, default=0, type=int, show_default=True)
@click.option('--cache-purge-level', required=False, default=1, type=click.IntRange(0, 2), show_default=True)
@click.option('--create-patch', is_flag=True, show_default=True)
@click.option('--exclude-paths', required=False, type=str, show_default=False, multiple=True)
@click.option('--exclude-regex-paths', required=False, type=str, show_default=False, multiple=True)
@click.option('--get-deep-distance', is_flag=True, show_default=True)
@click.option('--group-by', required=False, type=str, show_default=False, multiple=False)
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
    """
    DeepDiff

    Deep Difference of dictionaries, iterables, strings and other objects. It will recursively look for all the changes.
    """
    kwargs['ignore_private_variables'] = not kwargs.pop('include_private_variables')
    kwargs['progress_logger'] = logger.info if kwargs['progress_logger'] == 'info' else logger.error
    create_patch = kwargs.pop('create_patch')
    t1_path = kwargs.pop("t1")
    t2_path = kwargs.pop("t2")
    t1_extension = t1_path.split('.')[-1]
    t2_extension = t2_path.split('.')[-1]

    for name, t_path, t_extension in [('t1', t1_path, t1_extension), ('t2', t2_path, t2_extension)]:
        try:
            kwargs[name] = load_path_content(t_path, file_type=t_extension)
        except Exception as e:
            sys.exit(str(f"Error when loading {name}: {e}"))

    # if (t1_extension != t2_extension):
    if t1_extension in {'csv', 'tsv'}:
        kwargs['t1'] = [dict(i) for i in kwargs['t1']]
    if t2_extension in {'csv', 'tsv'}:
        kwargs['t2'] = [dict(i) for i in kwargs['t2']]

    if create_patch:
        # Disabling logging progress since it will leak into stdout
        kwargs['log_frequency_in_sec'] = 0

    try:
        diff = DeepDiff(**kwargs)
    except Exception as e:  # pragma: no cover.  No need to test this.
        sys.exit(str(e))  # pragma: no cover.  No need to test this.

    if create_patch:
        try:
            delta = Delta(diff)
        except Exception as e:
            sys.exit(f"Error when loading the patch (aka delta): {e}")

        # printing into stdout
        sys.stdout.buffer.write(delta.dumps())
    else:
        pprint(diff, indent=2)


@cli.command()
@click.argument('path', type=click.Path(exists=True, resolve_path=True))
@click.argument('delta_path', type=click.Path(exists=True, resolve_path=True))
@click.option('--backup', '-b', is_flag=True, show_default=True)
def patch(
    path, delta_path, backup
):
    try:
        delta = Delta(delta_path=delta_path)
    except Exception as e:
        sys.exit(str(f"Error when loading the patch (aka delta) {delta_path}: {e}"))

    extension = path.split('.')[-1]

    try:
        content = load_path_content(path, file_type=extension)
    except Exception as e:
        sys.exit(str(f"Error when loading {path}: {e}"))

    result = delta + content

    try:
        save_content_to_path(result, path, file_type=extension, keep_backup=backup)
    except Exception as e:
        sys.exit(str(f"Error when saving {path}: {e}"))


# def get_stdin(ctx, param, value):
#     """
#     https://stackoverflow.com/a/45845513/1497443
#     """
#     if not value and not click.get_text_stream('stdin').isatty():
#         return click.get_text_stream('stdin').read().strip()
#     else:
#         return value


#                  obj,
#                  item,
#                  exclude_paths=OrderedSet(),
#                  exclude_regex_paths=OrderedSet(),
#                  exclude_types=OrderedSet(),
#                  verbose_level=1,
#                  case_sensitive=False,
#                  match_string=False,


@cli.command()
@click.argument('item', required=True, type=str)
@click.argument('path', type=click.Path(exists=True, resolve_path=True))
@click.option('--ignore-case', '-i', is_flag=True, show_default=True)
@click.option('--exact-match', is_flag=True, show_default=True)
@click.option('--exclude-paths', required=False, type=str, show_default=False, multiple=True)
@click.option('--exclude-regex-paths', required=False, type=str, show_default=False, multiple=True)
@click.option('--verbose-level', required=False, default=1, type=click.IntRange(0, 2), show_default=True)
def grep(item, path, **kwargs):
    kwargs['case_sensitive'] = not kwargs.pop('ignore_case')
    kwargs['match_string'] = kwargs.pop('exact_match')

    try:
        content = load_path_content(path)
    except Exception as e:
        sys.exit(str(f"Error when loading {path}: {e}"))

    try:
        result = DeepSearch(content, item, **kwargs)
    except Exception as e:
        sys.exit(str(f"Error when running deep search on {path}: {e}"))
    pprint(result, indent=2)


@cli.command()
@click.argument('path_inside', required=True, type=str)
@click.argument('path', type=click.Path(exists=True, resolve_path=True))
def extract(path_inside, path):
    """
    Deep Extract
    """
    try:
        content = load_path_content(path)
    except Exception as e:
        sys.exit(str(f"Error when loading {path}: {e}"))

    try:
        result = deep_extract(content, path_inside)
    except Exception as e:
        sys.exit(str(f"Error when running deep search on {path}: {e}"))
    pprint(result, indent=2)