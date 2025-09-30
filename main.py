from system.system import System
from access import DBModV1, SearcherModV1, AnalyzerModV1


def main():
    System(
        [
            DBModV1('./example/db_yay.db', './example/db_yay.json')
        ],
        [
            AnalyzerModV1
        ],
        SearcherModV1
    ).run(constants=['pi', 'EulerGamma'])


if __name__ == '__main__':
    main()
