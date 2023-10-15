import json
import sys
import requests

def main():
    # Set the URL of the registry you want to use
    registry_url = 'https://registry.npmjs.org/'

    # Get the path to the package-lock.json file from the command-line arguments
    if len(sys.argv) != 2:
        print('Usage: npm-fixer /path/to/package-lock.json')
        sys.exit(1)
    lockfile_path = sys.argv[1]

    # Load the package-lock.json file
    with open(lockfile_path, 'r') as f:
        lockfile = json.load(f)

    # Loop over each package in the packages section of the lockfile
    for package_key in lockfile['packages']:
        # Ignore the empty key & local packages
        if package_key == "" or not "node_modules/" in package_key:
            continue

        package = lockfile['packages'][package_key]
        package_name = package.get("name") or package_key.split("node_modules/")[-1]

        # Check if the package is missing resolved and integrity fields
        noResolved = 'resolved' not in package
        noIntegrity = 'integrity' not in package
        noLink = 'link' not in package
        if noResolved or (noIntegrity and noLink):
            # Get the package version from the lockfile
            version = package['version']

            # Fetch the package metadata from the registry
            response = requests.get(f"{registry_url + package_name}/{version}")
            if response.status_code == 200:
                package_data = response.json()
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
                print(f"foo {registry_url + package_name}/{version}")
                print(f"Status code: {response.status_code}.")

    # Save the updated package-lock.json file
    with open(lockfile_path, 'w') as f:
        json.dump(lockfile, f, indent=2)




if __name__ == "__main__":
    main()



# Local Variables:
# mode: python-ts
# End:
