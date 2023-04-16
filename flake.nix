{
  description = "A very basic python flake template, providing a devshell.";

  inputs = {
    nixpkgs.url = github:nixos/nixpkgs/nixos-unstable;
    flake-utils.url = github:numtide/flake-utils;
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        pyPkgs = pkgs.python310Packages;
        customPython = pkgs.python39.buildEnv.override {
          extraLibs = with pyPkgs; [
            ipython
            setuptools
            requests
          ];
        };
        packageName = with builtins; head (match "^.*name[[:space:]]*=[[:space:]][\"]([^[:space:]]*)[\"][,].*$" (readFile ./setup.py));
        version = with builtins; head (match "^.*version[[:space:]]*=[[:space:]][\"]([^[:space:]]*)[\"][,].*$" (readFile ./setup.py));
      in
      {

        packages.default = pyPkgs.buildPythonPackage {
          pname = packageName;
          inherit version;
          src = ./.;
          doCheck = false;

          propagatedBuildInputs = [ pyPkgs.requests ];
          meta = {
            homepage = "https://github.com/jeslie0/npm-lockfile-fix";
            description = "";
            license = pkgs.lib.licenses.mit;
          };
        };

        devShell = pkgs.mkShell {
          packages = with pkgs;
            [ python310Packages.python-lsp-server ];
          inputsFrom = [ self.packages.${system}.default ];
        };
      }
    );
}
