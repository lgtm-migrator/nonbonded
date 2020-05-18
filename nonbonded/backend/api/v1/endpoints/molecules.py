from fastapi import APIRouter

from starlette.responses import Response

from nonbonded.library.utilities.molecules import smiles_to_image
from nonbonded.library.utilities.molecules import url_string_to_smiles

router = APIRouter()


@router.get("/{smiles}/image")
async def get_molecule_image(smiles: str):

    smiles = url_string_to_smiles(smiles)

    svg_content = smiles_to_image(smiles)
    svg_response = Response(svg_content, media_type="image/svg+xml")

    return svg_response
