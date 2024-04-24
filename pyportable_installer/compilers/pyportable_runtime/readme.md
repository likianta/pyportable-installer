
## The naming rule in this directory

-   `py{version}_{platform}`

    -   `version`: e.g. `38`, `39`, `310`, `311`, `312`.
    -   `platform`: there are 3 values: `linux`, `mac`, `win`.

for example:

-   py38_linux
-   py38_mac
-   py38_win
-   py311_linux
-   py311_mac
-   py311_win

## How to build by yourself

prepares:

- python 3.8+
- poetry (for the following instructions)

```sh
git clone https://github.com/likianta/pyportable-crypto.git
cd pyportable-crypto
poetry install --no-root

poetry run python -m pyportable_crypto -h
poetry run python -m pyportable_crypto deploy-compiled-binary -h
poetry run python -m pyportable_crypto deploy-compiled-binary $secret_key $dist_dir
#   $secret_key: you can pass any string as you like, but it is better to be
#       as long and random as possible.
#   $dist_dir: e.g. './dist/compiled/py311_mac'
#       make sure the directory's parent path exists.
```
