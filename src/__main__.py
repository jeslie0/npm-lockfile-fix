import json
import requests
import argparse

# Set the URL of the registry
REGISTRY_URL = 'https://registry.npmjs.org/'


def get_lockfile_json(lockfile_path: str):
    """Take a filepath to a json file and return the json as a python object"""
    print(lockfile_path)
    with open(lockfile_path, 'r') as f:
        lockfile_json = json.load(f)

    return lockfile_json


def loop_through_packages(packages: json, onlyWithoutResolved: bool) -> None:
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
        noResolved: bool = 'resolved' not in package
        noIntegrity: bool = 'integrity' not in package
        noLink: bool = 'link' not in package

        # Define whether or not the json should be updated. Normally,
        # we update the json if there is no resolved, or noIntegrity
        # and noLink.
        shouldBeUpdated: bool = noResolved or (noIntegrity and noLink)
        if onlyWithoutResolved:
            shouldBeUpdated = (not noResolved) and noIntegrity and noLink

        if shouldBeUpdated:
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
                print(f"{package_key}@{version} updated.")
            else:
                # Print a message indicating that the package could not be fetched
                print(f"Could not fetch metadata for {package_key}@{version}.")
                print(f"foo {REGISTRY_URL + package_name}/{version}")
                print(f"Status code: {response.status_code}.")


def save_json(data: json, path: str) -> None:
    """Write the json data to given file path."""
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)


def makeParser():
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

    return parser


def main():
    args = makeParser().parse_args()

    lockfile_path = args.filename

    lockfile_json = get_lockfile_json(lockfile_path)

    loop_through_packages(lockfile_json['packages'], args.r)

    if args.cout:
        print(json.dumps(lockfile_json))
        return 0

    outpath = lockfile_path if args.output is None else args.output

    save_json(lockfile_json, outpath)

    return 0






if __name__ == "__main__":
    main()

# Local Variables:
# mode: python-ts
# End:
