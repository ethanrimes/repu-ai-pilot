# backend/src/core/conversation/utils/response_parser.py

import re
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from langchain.schema import BaseMessage

from src.shared.utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class ParsedVehicleInfo:
    """Parsed vehicle information from user input"""
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    confidence: float = 0.0
    raw_input: str = ""

@dataclass
class ParsedPartRequest:
    """Parsed part request information"""
    part_type: Optional[str] = None
    specifications: Dict[str, Any] = None
    confidence: float = 0.0
    raw_input: str = ""

class ResponseParser:
    """Parser for extracting structured information from user responses"""
    
    def __init__(self):
        # Common Colombian vehicle makes
        self.colombian_makes = {
            "toyota": ["toyota", "toyotas"],
            "chevrolet": ["chevrolet", "chevy", "chevrolets"],
            "renault": ["renault", "renaults"],
            "hyundai": ["hyundai", "hyundais"],
            "kia": ["kia", "kias"],
            "nissan": ["nissan", "nissans"],
            "mazda": ["mazda", "mazdas"],
            "ford": ["ford", "fords"],
            "volkswagen": ["volkswagen", "vw", "volks"],
            "suzuki": ["suzuki", "suzukis"],
            "mitsubishi": ["mitsubishi", "mitsubishis"]
        }
        
        # Year patterns
        self.year_patterns = [
            r'\b(19[89]\d|20[0-3]\d)\b',  # 1980-2039
            r'\baño\s+(\d{4})\b',  # "año 2020"
            r'\bmodel\s+(\d{4})\b',  # "model 2020"
            r'\b(\d{4})\s*model\b',  # "2020 model"
        ]
        
        # Common brake part types
        self.brake_parts = {
            "pastillas": ["pastillas", "pastilla", "pads", "pad"],
            "discos": ["discos", "disco", "rotors", "rotor", "disc", "discs"],
            "calipers": ["calipers", "caliper", "pinzas", "pinza"],
            "liquido": ["liquido", "líquido", "fluid", "aceite"],
            "mangueras": ["mangueras", "manguera", "hoses", "hose"],
            "tambores": ["tambores", "tambor", "drums", "drum"]
        }
    
    def parse_vehicle_info(self, user_input: str) -> ParsedVehicleInfo:
        """Parse vehicle information from user input"""
        if not user_input or not user_input.strip():
            return ParsedVehicleInfo(raw_input=user_input)
        
        text = user_input.lower().strip()
        
        # Extract make
        make = self._extract_vehicle_make(text)
        
        # Extract year
        year = self._extract_year(text)
        
        # Extract model (everything else, simplified)
        model = self._extract_model(text, make, year)
        
        # Calculate confidence based on what we found
        confidence = 0.0
        if make:
            confidence += 0.4
        if year:
            confidence += 0.3
        if model:
            confidence += 0.3
        
        return ParsedVehicleInfo(
            make=make,
            model=model,
            year=year,
            confidence=confidence,
            raw_input=user_input
        )
    
    def parse_part_request(self, user_input: str) -> ParsedPartRequest:
        """Parse brake part request from user input"""
        if not user_input or not user_input.strip():
            return ParsedPartRequest(raw_input=user_input)
        
        text = user_input.lower().strip()
        
        # Extract part type
        part_type = self._extract_part_type(text)
        
        # Extract specifications (placeholder)
        specifications = self._extract_specifications(text)
        
        # Calculate confidence
        confidence = 0.8 if part_type else 0.2
        
        return ParsedPartRequest(
            part_type=part_type,
            specifications=specifications,
            confidence=confidence,
            raw_input=user_input
        )
    
    def _extract_vehicle_make(self, text: str) -> Optional[str]:
        """Extract vehicle make from text"""
        for canonical_make, variants in self.colombian_makes.items():
            for variant in variants:
                if variant in text:
                    logger.debug(f"Found vehicle make: {canonical_make}")
                    return canonical_make.title()
        return None
    
    def _extract_year(self, text: str) -> Optional[int]:
        """Extract year from text"""
        for pattern in self.year_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    year = int(match.group(1))
                    if 1980 <= year <= 2030:  # Reasonable range
                        logger.debug(f"Found year: {year}")
                        return year
                except ValueError:
                    continue
        return None
    
    def _extract_model(self, text: str, make: Optional[str], year: Optional[int]) -> Optional[str]:
        """Extract model from text (simplified)"""
        # Remove make and year from text to get model
        clean_text = text
        
        if make:
            clean_text = re.sub(make.lower(), '', clean_text)
        
        if year:
            clean_text = re.sub(str(year), '', clean_text)
        
        # Clean up and extract potential model
        words = clean_text.split()
        # Filter out common words
        stop_words = ['de', 'del', 'la', 'el', 'un', 'una', 'año', 'model', 'car', 'auto', 'vehículo']
        model_words = [word for word in words if word not in stop_words and len(word) > 2]
        
        if model_words:
            model = ' '.join(model_words).strip().title()
            if model:
                logger.debug(f"Found model: {model}")
                return model
        
        return None
    
    def _extract_part_type(self, text: str) -> Optional[str]:
        """Extract brake part type from text"""
        for canonical_part, variants in self.brake_parts.items():
            for variant in variants:
                if variant in text:
                    logger.debug(f"Found part type: {canonical_part}")
                    return canonical_part
        return None
    
    def _extract_specifications(self, text: str) -> Dict[str, Any]:
        """Extract part specifications from text (placeholder)"""
        specs = {}
        
        # Look for common specifications
        if "delantero" in text or "front" in text:
            specs["position"] = "front"
        elif "trasero" in text or "rear" in text:
            specs["position"] = "rear"
        
        if "ceramico" in text or "ceramic" in text:
            specs["material"] = "ceramic"
        elif "metalico" in text or "metallic" in text:
            specs["material"] = "metallic"
        
        return specs if specs else None
