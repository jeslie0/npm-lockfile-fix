import json
import requests
import argparse

# Set the URL of the registry
REGISTRY_URL = 'https://registry.npmjs.org/'


def my_print(string: str, use_cout: bool):
    """Print string only when use_cout is false"""
    if not use_cout:
        print(string)


def get_lockfile_json(lockfile_path: str, use_cout):
    """Take a filepath to a json file and return the json as a python object"""
    my_print(lockfile_path, use_cout)
    with open(lockfile_path, 'r') as f:
        lockfile_json = json.load(f)

    return lockfile_json


def loop_through_packages(
        packages: json,
        only_without_resolved: bool,
        use_cout: bool
) -> None:
    """Loop over each package in the packages section of the lockfile"""

    # Establish a session to allow a connection to the same host to persist.
    session = requests.Session()

    for package_key in packages:
        # Ignore the empty key & local packages
        if package_key == "" or "node_modules/" not in package_key:
            continue

        package: json = packages[package_key]
        package_name: str = package.get("name") or package_key.split("node_modules/")[-1]

        # Check if the package is missing resolved and integrity fields
        no_resolved: bool = 'resolved' not in package
        no_integrity: bool = 'integrity' not in package
        noLink: bool = 'link' not in package

        # Define whether or not the json should be updated. Normally,
        # we update the json if there is no resolved, or noIntegrity
        # and noLink.
        should_update: bool = no_resolved or (no_integrity and noLink)
        if only_without_resolved:
            should_update = no_resolved or (no_integrity and noLink and no_resolved)

        if should_update:
            # Get the package version from the lockfile
            version: str = package['version']

            # Fetch the package metadata from the registry
            response = session.get(f"{REGISTRY_URL + package_name}/{version}")
            if response.status_code == 200:
                package_data: json = response.json()
                # Get the dist field for the specific version
                # of the package we care about
                dist = package_data['dist']
                # Update the package entry in the lockfile with the
                # resolved and integrity values
                package['resolved'] = dist['tarball']
                package['integrity'] = dist['integrity']
                # Print a message indicating that the package was updated
                my_print(f"{package_key}@{version} updated.", use_cout)
            else:
                # Print a message indicating that the package could not be fetched
                my_print(f"Could not fetch metadata for {package_key}@{version}.", use_cout)
                my_print(f"foo {REGISTRY_URL + package_name}/{version}", use_cout)
                my_print(f"Status code: {response.status_code}.", use_cout)


def save_json(data: json, path: str, indent: int) -> None:
    """Write the json data to given file path."""
    with open(path, 'w') as f:
        json.dump(data, f, indent=indent)


def make_parser():
    parser = argparse.ArgumentParser(
        prog='npm-lockfile-fix',
        description='Add missing integrity and resolved fields to a package-lock.json file. By default this will modify the specified file.',
    )

    parser.add_argument(
        "filename",
        help="the package-lock.json file to patch"
    )
    parser.add_argument(
        "-r",
        action='store_true',
        help='only patch dependencies without a resolve field'
    )
    parser.add_argument(
        "-o", "--output",
        action="store_const",
        help="leave input file unmodified and output to specified file"
    )
    parser.add_argument(
        "--cout",
        action="store_true",
        help="leave input file unmodified and output to stdout"
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="number of spaces to indent output with"
    )

    return parser
