import numpy as np
import xtiff

from typing import Optional, Sequence
from xml.etree import ElementTree as ET


def get_ome_xml(
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
    size_c = img.shape[2]
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
        assert len(channel_fluors) == size_c
        channel_elems = element_tree.findall("./Image/Pixels/Channel")
        assert channel_elems is not None and len(channel_elems) == size_c
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
