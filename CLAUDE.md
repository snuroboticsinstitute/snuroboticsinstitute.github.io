# 작업 규칙

- `dist/`가 공개 사이트의 웹 루트입니다. `main`에 push하면 GitHub Pages로 자동 배포됩니다.
- 모든 변경은 두 테마(화이트·NRL `light`, 검정·노랑 `dark`)에 똑같이 적용하고, 두 테마 모두 화면으로 확인합니다. 테마는 같은 HTML에 `html[data-theme=...]` CSS(`dist/assets/themes.css`)로 적용되며 `?theme=dark` / `?theme=light`로 열 수 있습니다.
- 별도 지시가 없으면 국문(`dist/`)과 영문(`dist/en/`)을 함께 변경합니다.
- `scripts/`의 생성 스크립트를 일괄 실행하지 않습니다. `dist/`의 수작업 수정이 덮어써질 수 있습니다(`README_KO.md` 참고).
