import numpy as np
import pandas as pd

from os import PathLike
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Union


def match_txt_files(
    mcd_files: Sequence[Union[str, PathLike]], txt_files: Sequence[Union[str, PathLike]]
) -> Dict[Path, List[Path]]:
    pass  # TODO


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
