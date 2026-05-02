from typing import Any
from datetime import date

from sqlalchemy import MetaData, Integer, String, Date, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


ix_naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
ix_metadata_obj = MetaData(naming_convention=ix_naming_convention)

class pickModelBase(DeclarativeBase):
    __abstract__ = True
    metadata = ix_metadata_obj
    
    def setValue(self, field: str, value: Any):
        """
        Set a value for a field in the model instance.
        :param field: The name of the field to set.
        :param value: The value to set for the field.
        """
        setattr(self, field, value)
    
    def getValue(self, field: str) -> Any:
        """
        Get the value of a field in the model instance.
        :param field: The name of the field to get.
        :return: The value of the field.
        """
        return getattr(self, field, None)


class picklist(pickModelBase):
    __tablename__ = 'picklist'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    status: Mapped[str] = mapped_column(String, default='')
    finishDate: Mapped[date] = mapped_column(Date, nullable=True)
    priority: Mapped[str] = mapped_column(String, default='')
    PartNumber: Mapped[str] = mapped_column(String, nullable=False)
    PKNumber: Mapped[str] = mapped_column(String, nullable=False)
    WONumber: Mapped[str] = mapped_column(String, nullable=False)
    Requestor: Mapped[str] = mapped_column(String, default='')
    intQty: Mapped[int] = mapped_column(Integer, nullable=False)
    remainQty: Mapped[int] = mapped_column(Integer, nullable=True)
    salesOrder: Mapped[str] = mapped_column(String, default='')
    owner: Mapped[str] = mapped_column(String, default='')
    notes: Mapped[str] = mapped_column(String, default='')

    __table_args__ = (
        UniqueConstraint('PartNumber', 'PKNumber', name='uix_part_pk'),
    )

class L6L10Parts(pickModelBase):
    __tablename__ = 'L6L10Parts'

    PartNumber: Mapped[str] = mapped_column(String, primary_key=True)

class IMSUpdate(pickModelBase):
    __tablename__ = 'IMSUpdate'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    status: Mapped[str] = mapped_column(String, nullable=True)
    PartNumber: Mapped[str] = mapped_column(String, nullable=False)
    PKNumber: Mapped[str] = mapped_column(String, nullable=False)
    WONumber: Mapped[str] = mapped_column(String, nullable=False)
    remainQty: Mapped[int] = mapped_column(Integer, nullable=False)

