# How to Build Runtime Binary

```sh
git clone https://github.com/likianta/pyportable-crypto.git
cd pyportable-crypto
poetry install --no-root

poetry run -m pyportable_crypto -h
poetry run -m pyportable_crypto deploy-compiled-binary -h
poetry run -m pyportable_crypto deploy-compiled-binary $secret_key $dist_dir
#   $secret_key: you can put any string as you like, but it is better to be
#       long enough.
#   $dist_dir: e.g. './dist/compiled_binaries/py311-win'
```
