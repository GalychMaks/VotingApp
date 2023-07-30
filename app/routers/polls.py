from fastapi import APIRouter, status, Depends, HTTPException, Response
from sqlalchemy import func
from .. import schemas, models, oauth2
from sqlalchemy.orm import Session
from ..database import get_db
from typing import List

router = APIRouter(
    prefix="/polls",
    tags=["Polls"]
)


@router.get("/", response_model=List[schemas.GetPollResponse])
def get_polls(db: Session = Depends(get_db)):
    vote_counts_subquery = db.query(
        models.Answer.poll_id,
        models.Answer.title.label('title'),
        func.count(models.Vote.answer_id).label('vote_count')
    ).outerjoin(
        models.Vote,
        models.Vote.answer_id == models.Answer.id
    ).group_by(
        models.Answer.id
    ).subquery()

    results = db.query(
        models.Poll.id.label('poll_id'),
        models.Poll.owner_id,
        models.Poll.title.label('question'),
        models.Poll.created_at,
        func.json_agg(func.json_build_object('answer', vote_counts_subquery.c.title, 'count',
                                             vote_counts_subquery.c.vote_count)).label('answers')
    ).outerjoin(
        vote_counts_subquery,
        models.Poll.id == vote_counts_subquery.c.poll_id
    ).group_by(
        models.Poll.id, models.Poll.title, models.Poll.owner_id, models.Poll.created_at
    ).all()

    results_as_dict = [row._asdict() for row in results]

    return results_as_dict


@router.get("/{poll_id}", response_model=schemas.GetPollResponse)
def get_poll(poll_id: int, db: Session = Depends(get_db)):
    vote_counts_subquery = db.query(
        models.Answer.poll_id,
        models.Answer.title.label('title'),
        func.count(models.Vote.answer_id).label('vote_count')
    ).outerjoin(
        models.Vote,
        models.Vote.answer_id == models.Answer.id
    ).group_by(
        models.Answer.id
    ).subquery()

    results = db.query(
        models.Poll.id.label('poll_id'),
        models.Poll.owner_id,
        models.Poll.title.label('question'),
        models.Poll.created_at,
        func.json_agg(func.json_build_object('answer', vote_counts_subquery.c.title, 'count',
                                             vote_counts_subquery.c.vote_count)).label('answers')
    ).outerjoin(
        vote_counts_subquery,
        models.Poll.id == vote_counts_subquery.c.poll_id
    ).group_by(
        models.Poll.id, models.Poll.title, models.Poll.owner_id, models.Poll.created_at
    ).filter(models.Poll.id == poll_id).first()

    results_as_dict = results._asdict()

    return results_as_dict


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.GetPollResponse)
def create_poll(poll: schemas.CreatePoll,
                db: Session = Depends(get_db),
                current_user: schemas.TokenData = Depends(oauth2.get_current_user)):
    new_poll = models.Poll(owner_id=current_user.id, title=poll.question)
    db.add(new_poll)
    db.commit()
    db.refresh(new_poll)

    answers = [models.Answer(poll_id=new_poll.id, title=answer) for answer in poll.answers]

    db.add_all(answers)
    db.commit()

    return_value = {
        'poll_id': new_poll.id,
        'owner_id': new_poll.owner_id,
        'question': new_poll.title,
        'created_at': new_poll.created_at,
        'answers': [{'answer': answer, 'count': 0} for answer in poll.answers]
    }

    return return_value


# @router.put("/{poll_id}", response_model=None)
# def update_poll(poll_id: int, db: Session = Depends(get_db)):
#     pass
#

@router.delete("/{poll_id}")
def delete_poll(poll_id: int,
                db: Session = Depends(get_db),
                current_user: schemas.TokenData = Depends(oauth2.get_current_user)):
    poll_query = db.query(models.Poll).filter(models.Poll.id == poll_id)

    poll = poll_query.first()

    if poll is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Poll with id: {poll_id} was not found")

    if poll.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform request action")

    poll_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
