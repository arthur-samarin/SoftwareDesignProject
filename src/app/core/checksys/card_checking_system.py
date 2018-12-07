import json

from app.core import LanguageRegistry, Game, Language, GameOutcome
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

        # Save solutions
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
                self.clients[0] = self.start_solution(s1_file, l1, 0, lf1)
                self.clients[1] = self.start_solution(s2_file, l2, 1, lf2)

                return self.start_game(game)

    @staticmethod
    def __compile(file: str, language: Language) -> bool:
        compile_command = language.get_compile_command(file)
        if compile_command:
            with open(os.path.join(os.path.dirname(file), 'compile.log'), 'wb') as clog:
                return_code = subprocess.call(compile_command, stdout=clog, stderr=clog, cwd=os.path.dirname(file))
            return return_code == 0
        else:
            return True

    def start_solution(self, file: str, language: Language, id, log_file):
        run_command = language.get_run_command(file)
        process = subprocess.Popen(run_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=log_file)

        initData = {}
        initData['state'] = 'init'
        initData['gameData'] = self.get_initial_data(id)

        self.send_data(id, initData)
        return process


    def send_data(self, id, data):
        self.clients[id].stdin.write(json.dumps(data).encode())
        self.clients[id].stdin.flush()

    def read_data(self, id):
        return json.loads(self.clients[id].stdout.readline())

    def start_game(self, game):
        final_result = None
        id = 0
        answer = {"state": "move", "gameData": {"cardsOnTable": []}}
        self.send_data(id, answer)
        while (True):
            data = self.read_data(id)
            result = self.handle_player_move(id, data)
            if result == {}:
                result = self.check_win()
                answer["state"] = "end"
                answer["gameData"] = result
                self.send_data(0, result)
                self.send_data(1, result)
                final_result = result
                break

            answer = {}
            answer['state'] = 'wait'
            answer['gameData'] = result
            self.send_data(id, result)
            answer['state'] = 'move'
            self.send_data(1 - id, result)

        outcome = GameOutcome.TIE
        if result["win_id"] == 0:
            outcome = GameOutcome.FIRST_WIN
        elif result["win_id"] == 1:
            outcome = GameOutcome.SECOND_WIN
            
        return GameVerdict(GameOutcome.FIRST_WIN, GameOutcomeReason.OK)

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
    with open('test.py', 'rb') as f:
        bytes = f.read()
    src1 = SourceCode('testFromBytes.py', bytes, "py")
    src2 = src1

    game = Game('Cards', 'Cards')
    lr = LanguageRegistry.from_languages([
        PythonLanguage()
    ])

    impl = CheckSystemImpl(lr, 'rd')
    impl.evaluate(game, '1', SourceCode('test.py', src1, 'python3'), '2', SourceCode('test2.py', src2, 'python3'))
