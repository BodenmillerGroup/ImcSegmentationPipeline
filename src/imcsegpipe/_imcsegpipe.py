import numpy as np
import pandas as pd

from os import PathLike
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Union


def match_txt_files(
    mcd_files: Sequence[Union[str, PathLike]], txt_files: Sequence[Union[str, PathLike]]
) -> Dict[Union[str, PathLike], List[Path]]:
    txt_files = list(txt_files)
    matched_txt_files = {}
    for mcd_file in sorted(mcd_files, key=lambda x: Path(x).stem, reverse=True):
        matched_txt_files[mcd_file] = []
        i = 0
        while i < range(len(txt_files)):
            txt_file = txt_files[i]
            if Path(txt_file).stem.startswith(Path(mcd_file).stem):
                matched_txt_files[mcd_file].append(Path(txt_file))
                txt_files.remove(txt_file)
                i -= 1
            i += 1
    return matched_txt_files


def extract_mcd_file(
    mcd_file: Union[str, PathLike],
    out_dir: Union[str, PathLike],
    txt_files: Optional[Sequence[Union[str, PathLike]]] = None,
    hpf: Optional[float] = None,
) -> pd.DataFrame:
    pass  # TODO


def create_analysis_stacks(
    in_dir: Union[str, PathLike],
    out_dir: Union[str, PathLike],
    channel_metals: Sequence[str],
    channel_mask: np.ndarray,
    suffix: str,
) -> None:
    pass


def export_to_histocat(
    img_dir: Union[str, PathLike], out_dir: Union[str, PathLike]
) -> None:
    pass  # TODO
