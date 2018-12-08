import json

from app.core import LanguageRegistry, Game, Language, GameOutcome
from app.core.card_game import CardGame
from app.core.checksys import CheckingSystem, GameVerdict, GameOutcomeReason
from app.core.languages import CppLanguage, PythonLanguage
from app.model import SourceCode

import os
import subprocess


class CheckSystemImpl(CheckingSystem):
    def __init__(self, languages_registry: LanguageRegistry, dir_path: str):
        self.dir_path = os.path.abspath(dir_path)
        self.languages_registry = languages_registry
        self.clients = {}

    def evaluate(self, game: Game, id1: str, source1: SourceCode, id2: str, source2: SourceCode) -> GameVerdict:
        # Get language
        l1 = self.languages_registry.get_by_name(source1.language_name)
        l2 = self.languages_registry.get_by_name(source2.language_name)

        # Create directories
        s1_dir = os.path.join(self.dir_path, id1)
        s2_dir = os.path.join(self.dir_path, id2)
        os.makedirs(s1_dir, exist_ok=True)
        os.makedirs(s2_dir, exist_ok=True)
        s1_file = os.path.join(s1_dir, source1.filename)
        s2_file = os.path.join(s2_dir, source2.filename)
        s1_logfile = os.path.join(s1_dir, 'stderr.log')
        s2_logfile = os.path.join(s2_dir, 'stderr.log')

        with open(s1_file, 'wb') as f:
            f.write(source1.code)
        with open(s2_file, 'wb') as f:
            f.write(source2.code)

        # Compile solutions
        if not self.__compile(s1_file, l1):
            # CE
            return GameVerdict(GameOutcome.SECOND_WIN, GameOutcomeReason.CRASH)
        if not self.__compile(s2_file, l2):
            # CE
            return GameVerdict(GameOutcome.FIRST_WIN, GameOutcomeReason.CRASH)

        # Start solutions
        with open(s1_logfile, 'wb') as lf1:
            with open(s2_logfile, 'wb') as lf2:
                clients = {}
                clients[0] = self.start_solution(s1_file, l1, game, 0, lf1)
                clients[1] = self.start_solution(s2_file, l2, game, 1, lf2)

                for i in range(2):
                    initData = {}
                    initData['state'] = 'init'
                    initData['gameData'] = self.get_initial_data(game, i)

                    self.send_data(clients, i, initData)

                return self.start_game(clients, game)

    @staticmethod
    def __compile(file: str, language: Language) -> bool:
        compile_command = language.get_compile_command(file)
        if compile_command:
            with open(os.path.join(os.path.dirname(file), 'compile.log'), 'wb') as clog:
                return_code = subprocess.call(compile_command, stdout=clog, stderr=clog, cwd=os.path.dirname(file))
            return return_code == 0
        else:
            return True

    def start_solution(self, file: str, language: Language,game, id, log_file):
        run_command = language.get_run_command(file) + [str(id)]
        client = subprocess.Popen(run_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        return client


    def send_data(self, clients, id, data):
        clients[id].stdin.write((json.dumps(data) + '\n').encode())
        clients[id].stdin.flush()

    def read_data(self, clients, id):
        line = clients[id].stdout.readline()
        return json.loads(line)

    def start_game(self, clients, game):
        reason = GameOutcomeReason.OK
        final_result = None
        id = 0
        answer = {"state": "move", "gameData": None}
        self.send_data(clients, id, answer)
        while (True):
            data = self.read_data(clients, id)

            if not game.validate_move(id, data):
                reason = GameOutcomeReason.INVALID_MOVE
                break

            print('recieve: ', data)
            result = self.handle_player_move(game, id, data)
            if result == {}:
                result = self.check_win(game)
                answer["state"] = "end"
                answer["gameData"] = result
                self.send_data(clients, 0, answer)
                self.send_data(clients, 1, answer)
                final_result = result
                print('send: ', answer)
                break

            answer = {}
            answer['state'] = 'wait'
            answer['gameData'] = result
            self.send_data(clients, id, answer)
            answer['state'] = 'move'
            self.send_data(clients, 1 - id, answer)

            print('send: ', answer)
            id = 1 - id

        outcome = GameOutcome.TIE
        if result["win_id"] == 0:
            outcome = GameOutcome.FIRST_WIN
        elif result["win_id"] == 1:
            outcome = GameOutcome.SECOND_WIN

        return GameVerdict(outcome, reason)

    def get_initial_data(self, game, id):
        data = game.get_initial_data_for_player(id)
        return data

    def validate_move(self, game, id, data):
        return game.validate_move(id, data)

    def handle_player_move(self, game, id, data):
        return game.handle_player_move(id, data)

    def check_win(self, game):
        return game.check_win()

if __name__ == '__main__':
    bytes = None
    with open('strategy.py', 'rb') as f:
        bytes = f.read()

        game = CardGame()
    lr = LanguageRegistry.from_languages([
        PythonLanguage()
    ])

    impl = CheckSystemImpl(lr, 'rd')
    impl.evaluate(game, '1', SourceCode('testA.py', bytes, 'python3'), '2', SourceCode('testB.py', bytes, 'python3'))
