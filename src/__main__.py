import json
import sys
import requests

# Set the URL of the registry
REGISTRY_URL = 'https://registry.npmjs.org/'


def get_lockfile_json(lockfile_path: str):
    """Take a filepath to a json file and return the json as a python object"""
    print(lockfile_path)
    with open(lockfile_path, 'r') as f:
        lockfile_json = json.load(f)

    return lockfile_json


def loop_through_packages(packages: json) -> None:
    """Loop over each package in the packages section of the lockfile"""

    # Establish a session to allow a connection to the same host to persist.
    session = requests.Session()

    for package_key in packages:
        # Ignore the empty key & local packages
        if package_key == "" or "node_modules/" not in package_key:
            continue

        package: str = packages[package_key]
        package_name: str = package.get("name") or package_key.split("node_modules/")[-1]

        # Check if the package is missing resolved and integrity fields
        noResolved: bool = 'resolved' not in package
        noIntegrity: bool = 'integrity' not in package
        noLink: bool = 'link' not in package
        if noResolved or (noIntegrity and noLink):
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


def main():
    # Get the path to the package-lock.json file from the command-line arguments
    if len(sys.argv) != 2:
        print('Usage: npm-fixer /path/to/package-lock.json')
        sys.exit(1)
    lockfile_path = sys.argv[1]

    lockfile_json = get_lockfile_json(lockfile_path)

    loop_through_packages(lockfile_json['packages'])

    save_json(lockfile_json, lockfile_path)


if __name__ == "__main__":
    main()

# Local Variables:
# mode: python-ts
# End:
