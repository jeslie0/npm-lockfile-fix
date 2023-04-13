import json
import sys
import requests

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
for package in lockfile['packages']:
    # Ignore the empty key
    if package == "":
        continue

    # Check if the package is missing resolved and integrity fields
    noResolved = 'resolved' not in lockfile['packages'][package]
    noIntegrity = 'integrity' not in lockfile['packages'][package]
    if noResolved or noIntegrity:
        # Get the package version from the lockfile
        version = lockfile['packages'][package]['version']

        # Remove the "node_modules/" prefix from the package name
        package_name = package.split("/")[-1]

        # Fetch the package metadata from the registry
        response = requests.get(registry_url + package_name)
        if response.status_code == 200:
            package_data = response.json()
            # Get the dist field for the specific version
            # of the package we care about
            dist = package_data['versions'][version]['dist']
            # Update the package entry in the lockfile with the
            # resolved and integrity values
            lockfile['packages'][package]['resolved'] = dist['tarball']
            lockfile['packages'][package]['integrity'] = dist['integrity']
            # Print a message indicating that the package was updated
            print(f"{package}@{version} updated.")
        else:
            # Print a message indicating that the package could not be fetched
            print(f"Could not fetch metadata for {package}@{version}.")
            print(f"foo {registry_url + package}")
            print(f"Status code: {response.status_code}.")

# Save the updated package-lock.json file
with open('package-lock.json', 'w') as f:
    json.dump(lockfile, f, indent=2)

# Local Variables:
# mode: python-ts
# End:
