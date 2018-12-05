from sqlalchemy import Column, Integer, String, LargeBinary
from sqlalchemy.ext.declarative import declarative_base

from app.model import SourceCode, SolutionLink

import html

Base = declarative_base()


class Solution(Base):
    __tablename__ = 'solutions'

    id = Column(Integer, primary_key=True)
    creator_id = Column(Integer)
    name = Column(String)
    filename = Column(String)
    code = Column(LargeBinary)
    language_name = Column(String)
    game_name = Column(String)
    rating = Column(Integer)
    version = Column(Integer)

    @property
    def source_code(self) -> SourceCode:
        return SourceCode(self.filename, self.code, self.language_name)

    @source_code.setter
    def source_code(self, source_code: SourceCode) -> None:
        self.filename = source_code.filename
        self.code = source_code.code
        self.language_name = source_code.language_name

    @property
    def name_as_html(self) -> str:
        return html.escape(self.name) if self.name else '[без имени]'

    def create_link(self) -> SolutionLink:
        return SolutionLink(self.game_name, self.creator_id)
