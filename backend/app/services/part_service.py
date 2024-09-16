from sqlalchemy.orm import Session, joinedload

from backend.app.models.product import Part


class PartService:
    def __init__(self, db: Session):
        self.db = db

    def get_parts(self, product_id: int):
        return (
            self.db.query(Part)
            .filter(Part.product_id == product_id)
            .options(joinedload(Part.options))
            .all()
        )
