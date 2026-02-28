from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas
from .database import SessionLocal, engine
from sqlalchemy import or_
from collections import deque

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="BiteSpeed Identity Service")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/identify", response_model=schemas.IdentifyResponse)
def identify(request: schemas.IdentifyRequest, db: Session = Depends(get_db)):

    if not request.email and not request.phoneNumber:
        raise HTTPException(status_code=400, detail="Email or phoneNumber required")

    # -------------------------
    # STEP 1: NULL-safe matching
    # -------------------------
    filters = []
    if request.email:
        filters.append(models.Contact.email == request.email)
    if request.phoneNumber:
        filters.append(models.Contact.phoneNumber == request.phoneNumber)

    matches = db.query(models.Contact).filter(or_(*filters)).all()

    # -------------------------
    # STEP 2: New Customer
    # -------------------------
    if not matches:
        new_c = models.Contact(
            email=request.email,
            phoneNumber=request.phoneNumber,
            linkPrecedence="primary"
        )
        db.add(new_c)
        db.commit()
        db.refresh(new_c)

        return {
            "contact": {
                "primaryContactId": new_c.id,
                "emails": [new_c.email] if new_c.email else [],
                "phoneNumbers": [new_c.phoneNumber] if new_c.phoneNumber else [],
                "secondaryContactIds": []
            }
        }

    # -------------------------
    # STEP 3: Graph Traversal (BFS)
    # -------------------------
    visited = set()
    queue = deque(matches)

    while queue:
        contact = queue.popleft()

        if contact.id in visited:
            continue

        visited.add(contact.id)

        related = db.query(models.Contact).filter(
            or_(
                models.Contact.id == contact.linkedId,
                models.Contact.linkedId == contact.id
            )
        ).all()

        for r in related:
            if r.id not in visited:
                queue.append(r)

    cluster = db.query(models.Contact).filter(
        models.Contact.id.in_(visited)
    ).all()

    # -------------------------
    # STEP 4: Find True Primary (Oldest)
    # -------------------------
    primary = min(cluster, key=lambda x: x.createdAt)

    # -------------------------
    # STEP 5: Demote Other Primaries
    # -------------------------
    for contact in cluster:
        if contact.id != primary.id:
            contact.linkPrecedence = "secondary"
            contact.linkedId = primary.id

    db.commit()

    # -------------------------
    # STEP 6: Add Secondary If New Info
    # -------------------------
    existing_emails = {c.email for c in cluster if c.email}
    existing_phones = {c.phoneNumber for c in cluster if c.phoneNumber}

    new_info = False
    if request.email and request.email not in existing_emails:
        new_info = True
    if request.phoneNumber and request.phoneNumber not in existing_phones:
        new_info = True

    if new_info:
        new_secondary = models.Contact(
            email=request.email,
            phoneNumber=request.phoneNumber,
            linkedId=primary.id,
            linkPrecedence="secondary"
        )
        db.add(new_secondary)
        db.commit()
        db.refresh(new_secondary)
        cluster.append(new_secondary)

    # -------------------------
    # STEP 7: Build Response
    # -------------------------
    emails = []
    phones = []

    if primary.email:
        emails.append(primary.email)
    if primary.phoneNumber:
        phones.append(primary.phoneNumber)

    for c in cluster:
        if c.id == primary.id:
            continue
        if c.email and c.email not in emails:
            emails.append(c.email)
        if c.phoneNumber and c.phoneNumber not in phones:
            phones.append(c.phoneNumber)

    secondary_ids = [c.id for c in cluster if c.id != primary.id]

    return {
        "contact": {
            "primaryContactId": primary.id,
            "emails": emails,
            "phoneNumbers": phones,
            "secondaryContactIds": secondary_ids
        }
    }