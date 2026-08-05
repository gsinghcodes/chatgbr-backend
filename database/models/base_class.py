from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        # Grabs primary keys dynamically
        pks = ", ".join(
            f"{k}={v!r}" for k, v in self.__dict__.items() if not k.startswith("_")
        )
        return f"<{class_name}({pks})>"

    pass
