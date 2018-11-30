from app.launch import Launcher, Config


def main():
    config = Config.from_json_file('config.json')
    Launcher.start(config)


if __name__ == '__main__':
    main()
