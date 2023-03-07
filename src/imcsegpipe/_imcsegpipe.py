import logging
import re
import shutil
from os import PathLike
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Union
from zipfile import ZipFile

import imageio
import numpy as np
import pandas as pd
import tifffile
import xtiff
from readimc import MCDFile, TXTFile
from readimc.data import Acquisition, Panorama, Slide

from .utils import AcquisitionMetadata, filter_hot_pixels, get_acquisition_ome_xml


def extract_zip_file(
    zip_file: Union[str, PathLike], dest_dir: Union[str, PathLike]
) -> None:
    with ZipFile(zip_file, allowZip64=True) as f:
        f.extractall(dest_dir)


def match_txt_files(
    mcd_files: Sequence[Union[str, PathLike]], txt_files: Sequence[Union[str, PathLike]]
) -> Dict[Union[str, PathLike], List[Path]]:
    unmatched_txt_files = list(txt_files)
    matched_txt_files: Dict[Union[str, PathLike], List[Path]] = {}
    for mcd_file in sorted(mcd_files, key=lambda x: Path(x).stem, reverse=True):
        matched_txt_files[mcd_file] = []
        i = 0
        while i < len(unmatched_txt_files):
            txt_file = unmatched_txt_files[i]
            if Path(txt_file).stem.startswith(Path(mcd_file).stem):
                matched_txt_files[mcd_file].append(Path(txt_file))
                unmatched_txt_files.remove(txt_file)
                i -= 1
            i += 1
    if len(unmatched_txt_files) > 0:
        unmatched_txt_file_names = [Path(f).name for f in unmatched_txt_files]
        logging.warning(
            "The following .txt files could not be matched to an .mcd file"
            f" and will be ignored: {unmatched_txt_file_names}"
        )
    return matched_txt_files


def extract_mcd_file(
    mcd_file: Union[str, PathLike],
    acquisition_dir: Union[str, PathLike],
    txt_files: Optional[Sequence[Union[str, PathLike]]] = None,
) -> pd.DataFrame:
    acquisition_origins = {}
    acquisition_is_valids = {}
    Path(acquisition_dir).mkdir(exist_ok=True)
    with MCDFile(mcd_file) as f_mcd:
        schema_xml_file = Path(acquisition_dir) / f"{Path(mcd_file).stem}_schema.xml"
        _extract_schema(f_mcd, schema_xml_file)
        for slide in f_mcd.slides:
            slide_stem = f"{Path(mcd_file).stem}_s{slide.id}"
            slide_img_file = Path(acquisition_dir) / f"{slide_stem}_slide.png"
            _extract_slide(f_mcd, slide, slide_img_file)
            for panorama in slide.panoramas:
                panorama_img_file = (
                    Path(acquisition_dir) / f"{slide_stem}_p{panorama.id}_pano.png"
                )
                _extract_panorama(f_mcd, panorama, panorama_img_file)
            for acquisition in slide.acquisitions:
                acquisition_img_file = (
                    Path(acquisition_dir)
                    / f"{slide_stem}_a{acquisition.id}_ac.ome.tiff"
                )
                acquisition_channels_file = acquisition_img_file.with_name(
                    acquisition_img_file.name[:-9] + ".csv"
                )
                acquisition_origin = "mcd"
                acquisition_is_valid = _extract_acquisition(
                    f_mcd, acquisition, acquisition_img_file, acquisition_channels_file
                )
                if not acquisition_is_valid and txt_files is not None:
                    acquisition_txt_files = [
                        txt_file
                        for txt_file in txt_files
                        if Path(txt_file).stem.endswith(f"_{acquisition.id}")
                    ]
                    if len(acquisition_txt_files) == 1:
                        txt_file = acquisition_txt_files[0]
                        logging.info(
                            f"Attempting to restore acquisition {acquisition.id} "
                            f"from file {Path(txt_file).name}"
                        )
                        with TXTFile(txt_file) as f_txt:
                            acquisition_origin = "txt"
                            acquisition_is_valid = _extract_acquisition_from_txt_file(
                                f_mcd,
                                f_txt,
                                acquisition,
                                acquisition_img_file,
                                acquisition_channels_file,
                            )
                    elif len(acquisition_txt_files) > 1:
                        acquisition_txt_file_names = [
                            Path(f).name for f in acquisition_txt_files
                        ]
                        logging.warning(
                            f"Multiple .txt files found for acquisition "
                            f"{acquisition.id} in {Path(mcd_file).name}: "
                            f"{acquisition_txt_file_names}"
                        )
                acquisition_origins[acquisition.id] = acquisition_origin
                acquisition_is_valids[acquisition.id] = acquisition_is_valid
        return _create_acquisition_metadata(
            f_mcd, acquisition_origins, acquisition_is_valids
        )


def create_analysis_stacks(
    acquisition_dir: Union[str, PathLike],
    analysis_dir: Union[str, PathLike],
    analysis_channels: Sequence[str],
    suffix: Optional[str] = None,
    hpf: Optional[float] = None,
) -> None:
    Path(analysis_dir).mkdir(exist_ok=True)
    for acquisition_img_file in Path(acquisition_dir).glob("[!.]*.ome.tiff"):
        acquisition_channels_file = acquisition_img_file.with_name(
            acquisition_img_file.name[:-9] + ".csv"
        )
        acquisition_img = tifffile.imread(acquisition_img_file)
        assert acquisition_img.ndim == 3
        acquisition_channels: pd.DataFrame = pd.read_csv(acquisition_channels_file)
        assert len(acquisition_channels.index) == acquisition_img.shape[0]
        analysis_channel_indices = [
            acquisition_channels["channel_name"].tolist().index(channel_name)
            for channel_name in analysis_channels
        ]
        analysis_img = acquisition_img[analysis_channel_indices]
        analysis_img_file = Path(analysis_dir) / (
            acquisition_img_file.name[:-9] + ".tiff"
        )
        if suffix is not None:
            analysis_img_file = analysis_img_file.with_name(
                analysis_img_file.name[:-5] + suffix + ".tiff"
            )
        analysis_channels_file = analysis_img_file.with_suffix(".csv")
        if hpf is not None:
            analysis_img = filter_hot_pixels(analysis_img, hpf)
        tifffile.imwrite(
            analysis_img_file, data=analysis_img.astype(np.uint16), imagej=True
        )
        with analysis_channels_file.open("w") as f:
            f.write("\n".join(analysis_channels))


def export_to_histocat(
    acquisition_dir: Union[str, PathLike],
    histocat_dir: Union[str, PathLike],
    mask_dir: Optional[Union[str, PathLike]] = None,
) -> None:
    Path(histocat_dir).mkdir(exist_ok=True)
    for acquisition_img_file in Path(acquisition_dir).glob("[!.]*.ome.tiff"):
        acquisition_channels_file = acquisition_img_file.with_name(
            acquisition_img_file.name[:-9] + ".csv"
        )
        acquisition_img = tifffile.imread(acquisition_img_file)
        assert acquisition_img.ndim == 3
        acquisition_channels: pd.DataFrame = pd.read_csv(acquisition_channels_file)
        assert len(acquisition_channels.index) == acquisition_img.shape[0]
        histocat_img_dir = Path(histocat_dir) / acquisition_img_file.name[:-9]
        histocat_img_dir.mkdir(exist_ok=True)
        for channel_index, row in acquisition_channels.iterrows():
            acquisition_channel_img: np.ndarray = acquisition_img[channel_index]
            channel_name = row["channel_name"]
            channel_label = row["channel_label"]
            if not pd.isnull(channel_label) and not channel_label:
                channel_label = re.sub("[^a-zA-Z0-9()]", "-", channel_label)
            tifffile.imwrite(
                histocat_img_dir
                / f"{channel_label or channel_name}_{channel_name}.tiff",
                data=acquisition_channel_img,
                imagej=True,
            )
        if mask_dir is not None:
            mask_files = list(
                Path(mask_dir).glob(f"[!.]{acquisition_img_file.name[:-9]}*_mask.tiff")
            )
            if len(mask_files) > 0:
                if len(mask_files) > 1:
                    logging.warning(
                        "Multiple mask files found for image "
                        f"{acquisition_img_file.name}: {mask_files}; "
                        "using the first one"
                    )
                shutil.copy2(mask_files[0], histocat_dir)


def _extract_schema(mcd_file_handle: MCDFile, schema_xml_file: Path) -> bool:
    try:
        with schema_xml_file.open("w") as f:
            f.write(mcd_file_handle.schema_xml)
        return True
    except Exception as e:
        logging.error(
            f"Error reading schema XML from file {mcd_file_handle.path.name}: {e}"
        )
        return False


def _extract_slide(
    mcd_file_handle: MCDFile, slide: Slide, slide_img_file: Path
) -> bool:
    try:
        slide_img = mcd_file_handle.read_slide(slide)
        if slide_img is not None:
            imageio.imwrite(slide_img_file, slide_img, compress_level=1)
        return True
    except Exception as e:
        logging.error(
            f"Error reading slide {slide.id} from file {mcd_file_handle.path.name}: {e}"
        )
        return False


def _extract_panorama(
    mcd_file_handle: MCDFile, panorama: Panorama, panorama_img_file: Path
) -> bool:
    try:
        panorama_img = mcd_file_handle.read_panorama(panorama)
        imageio.imwrite(panorama_img_file, panorama_img, compress_level=1)
        return True
    except Exception as e:
        logging.error(
            f"Error reading panorama {panorama.id} "
            f"from file {mcd_file_handle.path.name}: {e}"
        )
        return False


def _extract_acquisition(
    mcd_file_handle: MCDFile,
    acquisition: Acquisition,
    acquisition_img_file: Path,
    acquisition_channels_file: Path,
) -> bool:
    try:
        acquisition_img = mcd_file_handle.read_acquisition(acquisition)
        _write_acquisition_image(
            mcd_file_handle,
            acquisition,
            acquisition_img,
            acquisition_img_file,
            acquisition_channels_file,
        )
        return True
    except Exception as e:
        logging.error(
            f"Error reading acquisition {acquisition.id} "
            f"from file {mcd_file_handle.path.name}: {e}"
        )
        return False


def _extract_acquisition_from_txt_file(
    mcd_file_handle: MCDFile,
    txt_file_handle: TXTFile,
    acquisition: Acquisition,
    acquisition_img_file: Path,
    acquisition_channels_file: Path,
) -> bool:
    try:
        acquisition_img = txt_file_handle.read_acquisition()
        _write_acquisition_image(
            mcd_file_handle,
            acquisition,
            acquisition_img,
            acquisition_img_file,
            acquisition_channels_file,
        )
        return True
    except Exception as e:
        logging.error(
            f"Error restoring acquisition {acquisition.id} "
            f"for file {mcd_file_handle.path.name} from file {txt_file_handle.path}: "
            f"{e}"
        )
        return False


def _write_acquisition_image(
    mcd_file_handle: MCDFile,
    acquisition: Acquisition,
    acquisition_img: np.ndarray,
    acquisition_img_file: Path,
    acquisition_channels_file: Path,
) -> None:
    channel_labels_or_names = [
        channel_label or channel_name
        for channel_name, channel_label in zip(
            acquisition.channel_names, acquisition.channel_labels
        )
    ]
    xtiff.to_tiff(
        acquisition_img,
        acquisition_img_file,
        ome_xml_fun=get_acquisition_ome_xml,
        channel_names=channel_labels_or_names,
        channel_fluors=acquisition.channel_names,
        xml_metadata=mcd_file_handle.schema_xml.replace("\r\n", ""),
    )
    pd.DataFrame(
        data={
            "channel_name": acquisition.channel_names,
            "channel_label": acquisition.channel_labels,
        }
    ).to_csv(acquisition_channels_file, index=False)


def _create_acquisition_metadata(
    mcd_file_handle: MCDFile,
    acquisition_origins: Dict[int, str],
    acquisition_is_valids: Dict[int, bool],
) -> pd.DataFrame:
    return pd.DataFrame(
        data=[
            AcquisitionMetadata.from_mcd_file_acquisition(
                mcd_file_handle,
                acquisition,
                origin=acquisition_origins[acquisition.id],
                is_valid=acquisition_is_valids[acquisition.id],
            )
            for slide in mcd_file_handle.slides
            for acquisition in slide.acquisitions
        ]
    )
