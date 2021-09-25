"""Console script for lowpolify."""
import sys
import click

from lowpolify import lowpolify


@click.command()
@click.argument('image', type=click.Path(exists=True))
def main(image):
    """Console script for lowpolify."""
    lowpolify(image)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
