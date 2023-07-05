import os

from typing import List, Dict
from pathlib import Path

from modules import shared, scripts
from preload import default_ddp_path, default_onnx_path
from tagger.preset import Preset
from tagger.interrogator import Interrogator, DeepDanbooruInterrogator, WaifuDiffusionInterrogator

preset = Preset(Path(scripts.basedir(), 'presets'))

interrogators: Dict[str, Interrogator] = {}


def refresh_interrogators() -> List[str]:
    global interrogators
    interrogators = {
        'wd14-vit-v2': WaifuDiffusionInterrogator(
            'wd14-vit-v2',
            repo_id='SmilingWolf/wd-v1-4-vit-tagger-v2',
            revision='v2.0'
        ),
        'wd14-convnext-v2': WaifuDiffusionInterrogator(
            'wd14-convnext-v2',
            repo_id='SmilingWolf/wd-v1-4-convnext-tagger-v2',
            revision='v2.0'
        ),
        'wd14-swinv2-v2': WaifuDiffusionInterrogator(
            'wd14-swinv2-v2',
            repo_id='SmilingWolf/wd-v1-4-swinv2-tagger-v2',
            revision='v2.0'
        ),
        'wd14-vit-v2-git': WaifuDiffusionInterrogator(
            'wd14-vit-v2-git',
            repo_id='SmilingWolf/wd-v1-4-vit-tagger-v2'
        ),
        'wd14-convnext-v2-git': WaifuDiffusionInterrogator(
            'wd14-convnext-v2-git',
            repo_id='SmilingWolf/wd-v1-4-convnext-tagger-v2'
        ),
        'wd14-swinv2-v2-git': WaifuDiffusionInterrogator(
            'wd14-swinv2-v2-git',
            repo_id='SmilingWolf/wd-v1-4-swinv2-tagger-v2'
        ),
        'wd14-vit': WaifuDiffusionInterrogator(
            'wd14-vit',
            repo_id='SmilingWolf/wd-v1-4-vit-tagger'),
        'wd14-convnext': WaifuDiffusionInterrogator(
            'wd14-convnext',
            repo_id='SmilingWolf/wd-v1-4-convnext-tagger'
        ),
        #'Z3D-E621-convnext': WaifuDiffusionInterrogator(
        #    'Z3D-E621-convnext',
        #    model_path=r'SmilingWolf/wd-v1-4-convnext-tagger',
        #    tags_path=r''
        #),
    }

    # load deepdanbooru project
    os.makedirs(
        getattr(shared.cmd_opts, 'deepdanbooru_projects_path', default_ddp_path),
        exist_ok=True
    )
    os.makedirs(
        getattr(shared.cmd_opts, 'onnxtagger_path', default_onnx_path),
        exist_ok=True
    )

    for path in os.scandir(shared.cmd_opts.deepdanbooru_projects_path):
        if not path.is_dir():
            continue

        if not Path(path, 'project.json').is_file():
            continue

        interrogators[path.name] = DeepDanbooruInterrogator(path.name, path)
    #scan for onnx models as well
    for path in os.scandir(shared.cmd_opts.onnxtagger_path):
        if not path.is_dir():
            continue
        
        #if no file with the extension .onnx is found, skip. If there is more than one file with that name, warn. Else put it in model_path
        onnx_files = [x for x in os.scandir(path) if x.name.endswith('.onnx')]
        if len(onnx_files) == 0:
            print(f"Warning: {path} has no model, skipping")
            continue
        elif len(onnx_files) > 1:
            print(f"Warning: {path} has multiple models, skipping")
            continue
        model_path = Path(path, onnx_files[0].name)

        if not Path(path, 'tags-selected.csv').is_file():
            print(f"Warning: {path} has a model but no tags-selected.csv file, skipping")
            continue

        interrogators[path.name] = WaifuDiffusionInterrogator(path.name,model_path=model_path, tags_path=Path(path, 'tags-selected.csv'))

    return sorted(interrogators.keys())


def split_str(s: str, separator=',') -> List[str]:
    return [x.strip() for x in s.split(separator) if x]
