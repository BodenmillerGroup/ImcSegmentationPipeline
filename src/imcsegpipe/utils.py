import re
from dataclasses import dataclass
from typing import List, Optional, Sequence
from xml.etree import ElementTree as ET

import numpy as np
import xtiff
from readimc import MCDFile
from readimc.data import Acquisition
from scipy.ndimage import maximum_filter


@dataclass
class AcquisitionMetadata:
    AcSession: str  # imctools
    slide_id: int  # imctools
    origin: str  # imctools
    source_path: str  # imctools
    id: int
    description: Optional[str]
    ablation_power: Optional[float]
    ablation_distance_between_shots_x: Optional[float]
    ablation_distance_between_shots_y: Optional[float]
    ablation_frequency: Optional[float]
    # AcquisitionROIID
    # OrderNumber
    signal_type: Optional[str]
    # DualCountStart
    # DataStartOffset
    # DataEndOffset
    start_timestamp: Optional[str]
    end_timestamp: Optional[str]
    # AfterAblationImageEndOffset
    # AfterAblationImageStartOffset
    # BeforeAblationImageEndOffset
    # BeforeAblationImageStartOffset
    roi_start_x_pos_um: Optional[float]
    roi_start_y_pos_um: Optional[float]
    roi_end_x_pos_um: Optional[float]
    roi_end_y_pos_um: Optional[float]
    movement_type: Optional[str]
    segment_data_format: Optional[str]
    # ValueBytes
    max_y: int
    max_x: int
    # PlumeStart
    # PlumeEnd
    template: Optional[str]
    profiling_type: Optional[str]
    has_before_ablation_image: bool  # imctools
    has_after_ablation_image: bool  # imctools
    is_valid: bool  # imctools

    def from_mcd_file_acquisition(
        f_mcd: MCDFile,
        acquisition: Acquisition,
        origin: str = "mcd",
        is_valid: bool = True,
    ) -> "AcquisitionMetadata":
        before_ablation_image_start_offset = acquisition.metadata.get(
            "BeforeAblationImageStartOffset"
        )
        before_ablation_image_end_offset = acquisition.metadata.get(
            "BeforeAblationImageEndOffset"
        )
        has_before_ablation_image = (
            before_ablation_image_start_offset is not None
            and before_ablation_image_end_offset is not None
            and int(before_ablation_image_start_offset)
            < int(before_ablation_image_end_offset)
        )
        after_ablation_image_start_offset = acquisition.metadata.get(
            "AfterAblationImageStartOffset"
        )
        after_ablation_image_end_offset = acquisition.metadata.get(
            "AfterAblationImageEndOffset"
        )
        has_after_ablation_image = (
            after_ablation_image_start_offset is not None
            and after_ablation_image_end_offset is not None
            and int(after_ablation_image_start_offset)
            < int(after_ablation_image_end_offset)
        )
        return AcquisitionMetadata(
            f_mcd.path.stem,
            acquisition.slide.id,
            origin,
            str(f_mcd.path.absolute()),
            acquisition.id,
            acquisition.description,
            float(acquisition.metadata.get("AblationPower") or "nan"),
            float(acquisition.metadata.get("AblationDistanceBetweenShotsX") or "nan"),
            float(acquisition.metadata.get("AblationDistanceBetweenShotsY") or "nan"),
            float(acquisition.metadata.get("AblationFrequency") or "nan"),
            acquisition.metadata.get("SignalType"),
            acquisition.metadata.get("StartTimeStamp"),
            acquisition.metadata.get("EndTimeStamp"),
            float(acquisition.metadata.get("ROIStartXPosUm") or "nan"),
            float(acquisition.metadata.get("ROIStartYPosUm") or "nan"),
            float(acquisition.metadata.get("ROIEndXPosUm") or "nan"),
            float(acquisition.metadata.get("ROIEndYPosUm") or "nan"),
            acquisition.metadata.get("MovementType"),
            acquisition.metadata.get("SegmentDataFormat"),
            int(acquisition.metadata["MaxY"]),
            int(acquisition.metadata["MaxX"]),
            acquisition.metadata.get("Template"),
            acquisition.metadata.get("ProfilingType"),
            has_before_ablation_image,
            has_after_ablation_image,
            is_valid,
        )


def get_acquisition_ome_xml(
    img: np.ndarray,
    image_name: Optional[str],
    channel_names: Optional[Sequence[str]],
    big_endian: bool,
    pixel_size: Optional[float],
    pixel_depth: Optional[float],
    channel_fluors: Optional[Sequence[str]] = None,
    xml_metadata: Optional[str] = None,
    **ome_xml_kwargs,
) -> ET.ElementTree:
    element_tree = xtiff.get_ome_xml(
        img,
        image_name,
        channel_names,
        big_endian,
        pixel_size,
        pixel_depth,
        **ome_xml_kwargs,
    )
    root_elem = element_tree.getroot()
    root_elem.set("Creator", "IMC Segmentation Pipeline")
    if channel_fluors is not None:
        assert len(channel_fluors) == img.shape[2]
        channel_elems = element_tree.findall("./Image/Pixels/Channel")
        assert channel_elems is not None and len(channel_elems) == img.shape[2]
        for channel_elem, channel_fluor in zip(channel_elems, channel_fluors):
            channel_elem.set("Fluor", channel_fluor)
    if xml_metadata is not None:
        structured_annot_elem = ET.SubElement(root_elem, "StructuredAnnotations")
        xml_annot_elem = ET.SubElement(structured_annot_elem, "XMLAnnotation")
        xml_annot_elem.set("ID", "Annotation:0")
        xml_annot_value_elem = ET.SubElement(xml_annot_elem, "Value")
        orig_metadata_elem = ET.SubElement(xml_annot_value_elem, "OriginalMetadata")
        orig_metadata_key_elem = ET.SubElement(orig_metadata_elem, "Key")
        orig_metadata_key_elem.text = "MCD-XML"
        orig_metadata_value_elem = ET.SubElement(orig_metadata_elem, "Value")
        orig_metadata_value_elem.text = xml_metadata
    return element_tree


def filter_hot_pixels(img: np.ndarray, thres: float) -> np.ndarray:
    kernel = np.ones((1, 3, 3), dtype=bool)
    kernel[0, 1, 1] = False
    max_neighbor_img = maximum_filter(img, footprint=kernel, mode="mirror")
    return np.where(img - max_neighbor_img > thres, max_neighbor_img, img)


def sort_channels_by_mass(channels: Sequence[str]) -> List[str]:
    return sorted(channels, key=lambda channel: int(re.sub("[^0-9]", "", channel) or 0))
