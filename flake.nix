{
  description = "Add missing integrity and resolved fields to a package-lock.json file.";

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
        nixpkgsFor.${system}.python312Packages;

      packageName = with builtins;
        head (match "^.*name[[:space:]]*=[[:space:]]*[\"]([^[:space:]]*)[\"][,].*$" (readFile ./setup.py));

      version = with builtins;
        head (match "^.*version[[:space:]]*=[[:space:]]*[\"]([^[:space:]]*)[\"][,].*$" (readFile ./setup.py));

      in
      {
        packages =
          forAllSystems (system:
            let
              pkgs =
                nixpkgsFor.${system};
            in
              {

                default =
                  self.packages.${system}.npm-lockfile-fix;

                npm-lockfile-fix = (pyPkgs system).buildPythonPackage {
                  inherit version;
                  pname =
                    packageName;

                  src =
                    ./.;

                  doCheck =
                    false;

                  propagatedBuildInputs =
                    [ (pyPkgs system).requests ];

                  meta = {
                    homepage =
                      "https://github.com/jeslie0/npm-lockfile-fix";

                    description =
                      "Add missing integrity and resolved fields to a package-lock.json file.";

                    license =
                      pkgs.lib.licenses.mit;
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
                    packages = with pkgs.python312Packages;
                      [ python-lsp-server
                        rope
                        pyflakes
                        mccabe
                        pycodestyle
                        mypy
                        flake8
                        pylint
                      ];

                    inputsFrom =
                      [ self.packages.${system}.default ];
                  };
              }
          );
      };
}
