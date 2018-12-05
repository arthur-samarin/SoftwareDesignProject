import threading
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker, scoped_session
from typing import Iterator


class Database:
    def __init__(self, url: str):
        self.engine = create_engine(url, echo=True)
        session_factory = sessionmaker(bind=self.engine)
        self.session_source = scoped_session(session_factory)
        self.thread_local_data = threading.local()

    @contextmanager
    def tx(self) -> Iterator[Session]:
        if getattr(self.thread_local_data, 'in_tx', None) is None:
            self.thread_local_data.in_tx = False

        s: Session = self.session_source()

        if not self.thread_local_data.in_tx:
            self.thread_local_data.in_tx = True
            try:
                yield s
                s.commit()
            except Exception:
                s.rollback()
                raise
            finally:
                self.thread_local_data.in_tx = False
        else:
            # Transaction is already started
            yield s

    def setup(self) -> None:
        with self.tx() as s:
            sqls = [
                """
            CREATE TABLE IF NOT EXISTS solutions(
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
                creator_id INTEGER NOT NULL,
                name TEXT NULL, 
                filename TEXT NOT NULL, 
                code BYTES NOT NULL, 
                language_name TEXT NOT NULL, 
                game_name TEXT NOT NULL,
                rating INTEGER NULL,
                version INTEGER NOT NULL 
            );""",
                """CREATE UNIQUE INDEX IF NOT EXISTS solutions_creator_id_game_name_unique 
                          ON solutions (creator_id, game_name);"""
            ]
            for sql in sqls:
                s.execute(sql)
