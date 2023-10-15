from fastapi import APIRouter

from ...models.request_responce import MovieOut
from ...internal.rec import RecSysManager

router = APIRouter(prefix="/api/v1")
rec_manager = RecSysManager()


@router.get(
    "/general_recommendations/",
    tags=["Recommender System v1"],
    response_model=list[MovieOut],
)
async def general_recommendations(user_id: str):
    return await rec_manager.general_recommendations(user_id)


@router.get(
    "/similar_movie_recommendations/",
    tags=["Recommender System v1"],
    response_model=list[MovieOut],
)
async def similar_movie_recommendations(content_id: str):
    return await rec_manager.similar_movie_recommendations(content_id)
