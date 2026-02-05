"""Block filtering and merging utilities."""
import numpy as np
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class BlockFilter:
    """Filter and merge OCR blocks based on quality metrics."""
    
    def __init__(
        self,
        min_area: int = 5000,
        min_text_len: int = 15,
        min_score: float = 0.65
    ):
        """Initialize filter.
        
        Args:
            min_area: Minimum bounding box area in pixels
            min_text_len: Minimum text length in characters
            min_score: Minimum confidence score
        """
        self.min_area = min_area
        self.min_text_len = min_text_len
        self.min_score = min_score
    
    def filter_and_merge(self, blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter noisy blocks and merge adjacent text blocks.
        
        Args:
            blocks: List of block dictionaries from OCR
            
        Returns:
            Filtered and merged block list
        """
        filtered = []
        i = 0
        
        while i < len(blocks):
            block = blocks[i]
            label = block.get("block_label", block.get("label", "unk"))
            score = block.get("block_score") or block.get("score", 1.0)
            bbox = block.get("block_bbox") or block.get("coordinate")
            text = block.get("block_content", "")
            
            # Filter by confidence score
            if score < self.min_score:
                i += 1
                continue
            
            # Filter by area and text length
            if bbox is not None:
                if isinstance(bbox, np.ndarray):
                    bbox = bbox.flatten().tolist()
                area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1]) if len(bbox) >= 4 else 0
                if area < self.min_area and len(text) < self.min_text_len:
                    i += 1
                    continue
            
            # Try to merge with previous text block
            if filtered and label in ("text", "paragraph") and \
               filtered[-1].get("block_label", "") in ("text", "paragraph"):
                prev = filtered[-1]
                prev_bbox = prev.get("block_bbox") or prev.get("coordinate")
                
                if prev_bbox and len(prev_bbox) >= 4 and len(bbox) >= 4:
                    # Merge if blocks are vertically close
                    if abs(prev_bbox[1] - bbox[1]) < 50 and abs(prev_bbox[3] - bbox[1]) < 100:
                        prev["block_content"] = (prev.get("block_content", "") + " " + text).strip()
                        # Update bbox to encompass both blocks
                        prev_bbox[0] = min(prev_bbox[0], bbox[0])
                        prev_bbox[1] = min(prev_bbox[1], bbox[1])
                        prev_bbox[2] = max(prev_bbox[2], bbox[2])
                        prev_bbox[3] = max(prev_bbox[3], bbox[3])
                        i += 1
                        continue
            
            filtered.append(block)
            i += 1
        
        logger.debug(f"Filtered {len(blocks)} → {len(filtered)} blocks")
        return filtered