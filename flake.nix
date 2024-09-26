{
  description = "A very basic python flake template, providing a devshell.";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      supportedSystems =
        [ "aarch64-linux" "x86_64-linux" "aarch64-darwin" "x86_64-darwin" ];

      forAllSystems =
        nixpkgs.lib.genAttrs supportedSystems;

      nixpkgsFor =
        forAllSystems (system:
          import nixpkgs {
            inherit system;
          }
        );

      pyPkgs = system:
        nixpkgsFor.${system}.python310Packages;

      packageName = with builtins;
        head (match "^.*name[[:space:]]*=[[:space:]][\"]([^[:space:]]*)[\"][,].*$" (readFile ./setup.py));

      version = with builtins;
        head (match "^.*version[[:space:]]*=[[:space:]][\"]([^[:space:]]*)[\"][,].*$" (readFile ./setup.py));

      in
      {
        packages =
          forAllSystems (system:
            let
              pkgs =
                nixpkgsFor.${system};

            in
              {
                default = (pyPkgs system).buildPythonPackage {
                  pname = packageName;
                  inherit version;
                  src = ./.;
                  doCheck = false;

                  propagatedBuildInputs = [ (pyPkgs system).requests ];
                  meta = {
                    homepage = "https://github.com/jeslie0/npm-lockfile-fix";
                    description = "";
                    license = pkgs.lib.licenses.mit;
                  };
                };
              }
          );

        devShells =
          forAllSystems (system:
            let
              pkgs =
                nixpkgsFor.${system};
            in
              {
                default =
                  pkgs.mkShell {
                    packages = with pkgs;
                      [ python310Packages.python-lsp-server
                        python310Packages.rope
                        python310Packages.pyflakes
                        python310Packages.mccabe
                        python310Packages.pycodestyle
                        python310Packages.mypy
                        python310Packages.flake8
                        python310Packages.pylint

                      ];

                    inputsFrom =
                      [ self.packages.${system}.default ];
                  };
              }
          );
      };
}
