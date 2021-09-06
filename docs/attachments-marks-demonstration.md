# Marks

## Marks Format

In "pyproject.json" it is:

```json
{
    "build": {
        "attachments": {
            "src_path_xxx_1": "asset",
            "src_path_xxx_2": "assets",
            "src_path_xxx_3": "only_folders",
            "src_path_xxx_4": "root_assets,compile",
            "src_path_xxx_5": "assets,compile,dist:lib/{name}",
            "...": "..."
        },
        "...": "..."
    },
    "...": "..."
}
```

After `pyportable_installer.main_flow.step1.indexing_paths.indexing_paths` processments, it becomes:

```python
conf = {
    "build": {
        "attachments": {
            "src_path_xxx_1": {
                "marks": ("asset",), 
                "path": ""
            },
            "src_path_xxx_2": {
                "marks": ("assets",), 
                "path": ""
            },
            "src_path_xxx_3": {
                "marks": ("only_folders",), 
                "path": ""
            },
            "src_path_xxx_4": {
                "marks": ("root_assets", "compile"), 
                "path": ""
            },
            "src_path_xxx_5": {
                "marks": ("assets", "compile"), 
                "path": "dst_root/lib/xxx_5"
            },
            ...: ...
        },
        ...: ...
    },
    ...: ...
}
```

The canonical struct can be found at `pyportable_installer.typehint.TAttachments`.

[TODO]

Available marks list:

Single marks:

- asset
- assets
- root_assets
- only_folder
- only_folders

Double marks:

- asset,compile
- assets,compile
- root_assets,compile

[TODO]
