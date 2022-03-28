{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/21.11";

    flake-utils.url = "github:numtide/flake-utils";

    drastikbot.url = "github:olagood/drastikbot/v2.1";
    drastikbot.flake = false;
    drastikbot_modules.url = "github:olagood/drastikbot_modules/v2.1";
    drastikbot_modules.flake = false;
  };

  outputs = { self, nixpkgs, flake-utils, drastikbot, drastikbot_modules, ... }:
    let
      supportedSystems = with flake-utils.lib.system; [ x86_64-linux i686-linux aarch64-linux ];
    in {
      overlay = final: prev: {
        drastikbot = prev.python3Packages.buildPythonApplication rec {
          pname = "drastikbot";
          version = "v2.1";

          format = "other";

          srcs = [
            self
            drastikbot
            drastikbot_modules
          ];

          nativeBuildInputs = [ prev.makeWrapper ];

          phases = [ "installPhase" ]; # Removes all phases except installPhase

          installPhase = ''
            arr=($srcs)
            mkdir -p $out/irc/modules

            # install dailybuild_modules
            cp -r ''${arr[0]}/src/* $out/irc/modules

            # install drastikbot core
            cp -r ''${arr[1]}/src/* $out/

            # install drastikbot modules
            cp -r ''${arr[2]}/* $out/irc/modules

            # Patch ".bots" command to include reference to dailybuild_modules
            sed -i 's|\(http://drastik.org/drastikbot"\)|\1 " https://git.neet.dev/zuckerberg/dailybuild_modules"|' $out/irc/modules/information.py

            # Patch ".source" command to include reference to dailybuild_modules
            sed -i 's|\(https://github.com/olagood/drastikbot_modules\\x0F"\)|\1 " : \\x0311https://git.neet.dev/zuckerberg/dailybuild_modules\\x0F"|' $out/irc/modules/information.py

            # Patch ".wa" command so that the AppID does not need to be hardcoded into the source code of the program
            sed -i 's|AppID = "Enter your AppID here"|import pathlib\nimport os\nAppID = pathlib.Path(os.environ["WOLFRAM_ID_FILE"]).read_text()|' $out/irc/modules/wolframalpha.py

            mkdir -p $out/bin

            makeWrapper ${prev.python3}/bin/python3 $out/bin/drastikbot \
              --prefix PYTHONPATH : ${with prev.python3Packages; makePythonPath [requests beautifulsoup4]} \
              --add-flags "$out/drastikbot.py"
          '';
        };
      };

      nixosModule = self.nixosModules.service;

      nixosModules.install = { ... }: {
        nixpkgs.overlays = [ self.overlay ];
      };
      nixosModules.service = { config, pkgs, lib, ... }:
        with lib;
        let
          cfg = config.services.drastikbot;
        in {
          imports = [ self.nixosModules.install ];

          options.services.drastikbot = {
            enable = lib.mkEnableOption "enable drastikbot";
            user = lib.mkOption {
              type = lib.types.str;
              default = "drastikbot";
              description = ''
                The user drastikbot should run as
              '';
            };
            group = lib.mkOption {
              type = lib.types.str;
              default = "drastikbot";
              description = ''
                The group drastikbot should run as
              '';
            };
            dataDir = lib.mkOption {
              type = lib.types.str;
              default = "/var/lib/drastikbot";
              description = ''
                Path to the drastikbot data directory
              '';
            };
            wolframAppIdFile = lib.mkOption {
              type = lib.types.str;
              description = ''
                The file containing the Wolfram Alpha App ID
              '';
            };
          };

          config = lib.mkIf cfg.enable {
            users.users.${cfg.user} = {
                isSystemUser = true;
                group = cfg.group;
                home = cfg.dataDir;
                createHome = true;
            };
            users.groups.${cfg.group} = {};
            systemd.services.drastikbot = {
              enable = true;
              after = ["network.target"];
              wantedBy = ["multi-user.target"];
              serviceConfig.ExecStart = "${pkgs.drastikbot}/bin/drastikbot -c ${cfg.dataDir}";
              serviceConfig.User = cfg.user;
              serviceConfig.Group = cfg.group;
              preStart = ''
                mkdir -p ${cfg.dataDir}
                chown ${cfg.user} ${cfg.dataDir}
              '';
              environment.WOLFRAM_ID_FILE = "${cfg.wolframAppIdFile}";
            };
          };
        };
    } // flake-utils.lib.eachSystem supportedSystems (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          overlays = [ self.overlay ];
        };
        lib = pkgs.lib;

        nixosTest =
          with import (nixpkgs + "/nixos/lib/testing-python.nix") { inherit system; };
          simpleTest {
            machine = { config, pkgs, ... }: {
              imports = [ self.nixosModule ];

              virtualisation.memorySize = 256;

              services.drastikbot = {
                enable = true;
                wolframAppIdFile = "";
              };
            };

            testScript =
              let
                botConfig = pkgs.writeText "config.json" ''
                  {
                    "sys": {
                      "log_level": "debug"
                    },
                    "irc": {
                      "owners": [
                        "nobody"
                      ],
                      "connection": {
                        "network": "example.com",
                        "port": 6697,
                        "ssl": true,
                        "net_password": "",
                        "nickname": "drastikbotTest",
                        "username": "drastikbotTest",
                        "realname": "drastikbotTest",
                        "authentication": "sasl",
                        "auth_password": ""
                      },
                      "channels": {},
                      "modules": {
                        "load": [],
                        "global_prefix": ".",
                        "channel_prefix": {},
                        "blacklist": {},
                        "whitelist": {}
                      }
                    }
                  }
                '';
                setup = pkgs.writeShellScript "setup.sh" ''
                  set -x
                  mkdir -p /var/lib/drastikbot
                  cp ${botConfig} /var/lib/drastikbot/config.json
                  chown -R drastikbot /var/lib/drastikbot
                '';
              in ''
                machine.start()
                machine.wait_for_unit("multi-user.target")
                machine.succeed("${setup}")
                machine.systemctl("restart drastikbot") # restart with config added
                machine.wait_for_unit("drastikbot")
              '';
          };
      in rec {
        checks.build = packages.drastikbot;
        checks.install = nixosTest;

        packages.drastikbot = pkgs.drastikbot;
        defaultPackage = packages.drastikbot;

        apps.drastikbot = flake-utils.lib.mkApp { drv = packages.drastikbot; };
        defaultApp = apps.drastikbot;
      }
    );
}