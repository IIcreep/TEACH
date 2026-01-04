from __future__ import annotations

from sqlalchemy import create_engine, ForeignKey, String, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user_account"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)

    # 一对多：一个用户多个邮箱
    addresses: Mapped[list[Address]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"User(id={self.id}, name={self.name!r})"


class Address(Base):
    __tablename__ = "address"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(200), nullable=False)

    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"), nullable=False)
    user: Mapped[User] = relationship(back_populates="addresses")

    def __repr__(self) -> str:
        return f"Address(id={self.id}, email={self.email!r}, user_id={self.user_id})"


def main() -> None:
    # Engine 是入口（连接池 + 方言 + DBAPI） :contentReference[oaicite:4]{index=4}
    engine = create_engine("sqlite+pysqlite:///demo.db", echo=True)

    # 建表（仅 demo：生产环境建议用 Alembic 迁移来管理） :contentReference[oaicite:5]{index=5}
    Base.metadata.create_all(engine)

    # 写入：用事务块包起来（成功自动 commit，异常自动 rollback） :contentReference[oaicite:6]{index=6}
    with Session(engine) as session:
        with session.begin():
            u1 = User(name="alice")
            u1.addresses = [Address(email="alice@example.com"), Address(email="a@work.com")]
            session.add(u1)

    # 查询：2.x 推荐用 select()（ORM 也用 Core 风格查询） :contentReference[oaicite:7]{index=7}
    with Session(engine) as session:
        stmt = select(User).where(User.name == "alice")
        alice = session.scalars(stmt).one()
        print("Loaded:", alice)
        print("Emails:", [a.email for a in alice.addresses])

    # 更新
    with Session(engine) as session:
        with session.begin():
            alice = session.scalars(select(User).where(User.name == "alice")).one()
            alice.name = "Alice"

    # 删除
    with Session(engine) as session:
        with session.begin():
            alice = session.scalars(select(User).where(User.name == "Alice")).one()
            session.delete(alice)


if __name__ == "__main__":
    main()
