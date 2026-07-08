from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.database import get_session
from app.dependencies.auth import get_current_user
from app.models.db_models import UserDB
from app.schemas.match import (
    JobMatch,
    MatchRefreshSummary,
    StoredJobMatchListResponse,
)
from app.services.match_persistence import (
    generate_live_matches_for_user_profile,
    get_saved_matches_for_user_profile,
    refresh_matches_for_user_profile,
)


router = APIRouter(prefix="/matches", tags=["Matches"])


@router.post(
    "/profile/{profile_id}/refresh",
    response_model=MatchRefreshSummary,
)
def refresh_profile_matches(
    profile_id: int,
    session: Session = Depends(get_session),
    current_user: UserDB = Depends(get_current_user),
):
    return refresh_matches_for_user_profile(
        session=session,
        profile_id=profile_id,
        current_user=current_user,
    )


@router.get(
    "/profile/{profile_id}/saved",
    response_model=StoredJobMatchListResponse,
)
def get_saved_profile_matches(
    profile_id: int,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    min_score: float | None = Query(default=None, ge=0, le=100),
    session: Session = Depends(get_session),
    current_user: UserDB = Depends(get_current_user),
):
    return get_saved_matches_for_user_profile(
        session=session,
        profile_id=profile_id,
        current_user=current_user,
        limit=limit,
        offset=offset,
        min_score=min_score,
    )


@router.get("/profile/{profile_id}", response_model=list[JobMatch])
def get_live_matches_for_profile(
    profile_id: int,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    min_score: float | None = Query(default=None, ge=0, le=100),
    session: Session = Depends(get_session),
    current_user: UserDB = Depends(get_current_user),
):
    return generate_live_matches_for_user_profile(
        session=session,
        profile_id=profile_id,
        current_user=current_user,
        limit=limit,
        offset=offset,
        min_score=min_score,
    )