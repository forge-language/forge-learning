# Forge 학습 빠른 시작

이 과정은 영어를 기본으로 제공하며 모든 강의에 한국어 설명과 과제가 있습니다.
웹 연습에서는 Forge를 JavaScript로 컴파일해 실행합니다. 터미널 연습은 설치한
Forge SDK를 사용합니다. 편집기의 LSP 기능은 별도로 설치하세요.

1. [SDK 설치 안내](https://github.com/forge-language/forge-platform#install)를
   따라 설치하거나 [소스 빌드](https://github.com/forge-language/forge#build-and-install)를 진행합니다.
2. `forge --help`가 실행되는지 확인합니다.
3. 이 저장소에서 다음 명령을 실행합니다.

```sh
python3 scripts/learn.py --language ko list
python3 scripts/learn.py --language ko show hello
python3 scripts/learn.py run hello
```

설치 경로가 `PATH`에 없으면 하위 명령 앞에 `--forge /설치/경로/forge`를 넣습니다.
강의 코드를 `practice.fg`에 복사해 수정하고 다음처럼 실행할 수 있습니다.

```sh
python3 scripts/learn.py run hello --file practice.fg
python3 scripts/learn.py run hello --file practice.fg --solution
```

첫 명령은 기본 예제 출력을 검사합니다. 두 번째 명령은 과제의 목표 출력을
검사합니다. 출력의 줄바꿈도 정확히 일치해야 합니다. `--file` 없이 `--solution`을
사용하면 참고 답안을 실행합니다. 먼저 직접 풀어 보세요.

Node.js가 설치되어 있으면 `--backend js`로 브라우저와 같은 백엔드를 연습할 수
있습니다. 네이티브 전용 네트워크·파일 API는 이 과정에 포함하지 않습니다.
현재 Forge는 실험적인 언어이며 완전한 타입·소유권 검사를 보장하지 않습니다.
`str_len`은 글자 수가 아니라 UTF-8 바이트 수를 반환합니다.

LSP 설치는 [language-server](https://github.com/forge-language/language-server)를
참고하세요. 편집기별 연결은 루트 README의 링크를 사용합니다.
