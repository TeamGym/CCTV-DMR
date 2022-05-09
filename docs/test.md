Test
====

`tests/` 디렉토리의 테스트 스크립트는 파이썬 표준 라이브러리의 unittest 모듈을 사용합니다.


테스트 실행
-----------
모든 테스트 스크립트를 한 번에 실행하려면 `scripts/run_all_tests.sh`를 실행합니다.

원하는 테스트만 실행하려면 `scripts/run_test.sh`를 명령행 인자와 함께 실행합니다. 명령행 인자는 스크립트의 모듈 이름입니다.

테스트 실행 예:
```sh
$ scripts/run_test.py tests.config_test
```

