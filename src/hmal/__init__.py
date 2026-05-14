__version__ = '0.1.0-alpha'
__author__ = 'Guilherme G. Machado'
__zenodo_doi__ = '10.5281/zenodo.placeholder'

from .core.harmonic_protocol import HarmonicProtocol, RationalChannel
from .bioacoustics.vocalization_mapper import map_cetacean_vocalization, classify_vocalization
from .security import HChallengeResponse, JanusGateway, JanusCompatibilityMode

__all__ = [
    "HarmonicProtocol", "RationalChannel", 
    "map_cetacean_vocalization", "classify_vocalization",
    "HChallengeResponse", "JanusGateway", "JanusCompatibilityMode"
]
