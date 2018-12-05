from app.core import GamesRegistry, LanguageRegistry
from app.core.checksys import CheckingSystem
from app.dao import Database
from app.dao.solutions_dao import SolutionsDao


class Components:
    def __init__(self, database: Database = None, solutions_dao: SolutionsDao = None,
                 games_registry: GamesRegistry = None, languages_registry: LanguageRegistry = None,
                 checking_system: CheckingSystem = None):
        self.database = database
        self.solutions_dao = solutions_dao
        self.games_registry = games_registry
        self.languages_registry = languages_registry
        self.checking_system = checking_system
