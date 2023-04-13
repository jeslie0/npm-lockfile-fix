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
            # Other python dependencies here
          ];
        };
        packageName = "npm-fixer";
      in
      {
        packages.${packageName} = pkgs.writers.writePython3Bin packageName {libraries = [pyPkgs.requests]; } (builtins.readFile ./src/main.py);

        defaultPackage = self.packages.${system}.${packageName};

        devShell = pkgs.mkShell {
          packages = with pkgs;
            [ python310Packages.python-lsp-server ];
          buildInputs = with pkgs;
            [ customPython ];
        };
      }
    );
}
