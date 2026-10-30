# 작업 규칙

- `dist/`가 공개 사이트의 웹 루트입니다. `main`에 push하면 GitHub Pages로 자동 배포됩니다.
- 사이트는 검정·노랑(`dark`) 테마 하나만 사용합니다. 화이트·NRL 테마와 테마 전환 버튼은 2026-10-27에 삭제했습니다(각 페이지의 인라인 스크립트가 `data-theme='dark'`로 고정).
- 별도 지시가 없으면 국문(`dist/`)과 영문(`dist/en/`)을 함께 변경합니다.
- `scripts/`의 생성 스크립트를 일괄 실행하지 않습니다. `dist/`의 수작업 수정이 덮어써질 수 있습니다(`README_KO.md` 참고).
- 작업이 끝나면 배포 완료를 확인한 뒤 "✅ 반영 완료"와 함께 캐시를 우회하는 링크(`?v=<커밋 해시>`)를 알려 줍니다.
- 교육 메뉴 탭: 교육철학(`/education/`) · 창의공학설계(`/education/creative-engineering-design/`) · 인재양성과정(`/education/talent-development/`). 창의공학설계의 수강생 후기는 `dist/assets/data/reviews.json`에서 관리합니다(`dist/assets/reviews.js`가 읽어 게시판으로 표시). 새 후기는 이 파일의 `reviews` 배열에 추가합니다: `id`, `year`, `robocon`(회차), `team`·`result`·`summary`·`text`(각각 `ko`/`en`), `members`(국문 페이지에만 표시). 연도가 2개 이상이면 연도 필터가, 6개를 넘으면 "더 보기" 버튼이 자동으로 나타납니다. 페이지 HTML의 기존 카드는 데이터 파일을 못 읽을 때를 위한 대체 화면입니다.
- 창의공학설계 갤러리는 `dist/assets/data/gallery.json`의 `photos` 배열로 관리합니다(`dist/assets/gallery.js`가 표시). 항목: `src`(웹용으로 줄인 이미지, 예: `/assets/gallery/2024-01.jpg`), `thumb`(선택), `year`, `caption`·`alt`(각각 `ko`/`en`). 비어 있으면 "사진은 준비 중입니다."가 보입니다. 학생 얼굴이 나오는 사진은 사용자가 고른 것만 올립니다.
- 홈 메인 이미지(hero) 전체가 소개 › 비전으로 연결됩니다(`.hero-link`). 생태계 구역 아래에 "한눈에 보는 로보틱스연구소"(`.glance`, 설립·국가연구소·참여 교수 수·연구 그룹과 운영진·목표·위치)가 있으니 숫자가 바뀌면 홈(국/영)에서 함께 고칩니다.
- 대메뉴(2026-10-28 개편): 소개(소장 인사말·비전·연혁·구성원·오시는 길) · 연구(연구진 `/research/people/`·연구과제(Research Projects) `/research/`·주요 연구성과(Research Highlights) `/research/achievements/`·국가연구소 `/research/nrl/`) · 교육 · 창업(`/venture/`) · 소식 · 참여하기. 사이드/모바일 메뉴는 모든 페이지에 같은 마크업으로 들어 있으니 바꿀 때 전체를 함께 바꿉니다. 옛 주소(`/people/*`, `/about/at-a-glance/`)는 새 위치로 이동하는 리다이렉트 페이지입니다.
- 주요 연구성과(`/research/achievements/`)는 `dist/assets/data/achievements.json`의 `achievements` 배열로 관리합니다(`dist/assets/achievements.js`가 표시). 성과 하나에 관련 영상·기사·논문·수상을 묶습니다. 항목: `id`, `date`(예: `2026-08`), `title`·`summary`·`people`(각각 `ko`/`en`), `image`(선택, `/assets/highlights/`; 없으면 YouTube 영상 썸네일), `venue`(사진이 없을 때 타일에 표시), `lab`(연구실, `ko`/`en`), `field`(분야, `ko`/`en`; 파일 맨 위 `fields` 목록 순서로 필터가 나타나며 해당 성과가 있는 분야만 보임), `links` 배열(`type`: `video`/`project`/`article`/`paper`/`award`/`patent`, `title`·`source`는 `ko`/`en`, `url`은 선택). 비어 있으면 "주요 연구성과는 준비 중입니다."가 보입니다. 연구진 사진은 `dist/assets/people/`에 있습니다.
- 연구과제(`/research/`)는 `dist/assets/data/projects.json`의 `projects` 배열로 관리합니다(`dist/assets/projects.js`가 표시). 항목: `id`, `title`·`program`(사업명)·`agency`(지원 부처)·`pi`(연구책임자)(각각 `ko`/`en`), `period`(예: `2025–`), `url`(선택, `ko`/`en`). 연구책임자가 2명 이상이면 책임자 필터가 자동으로 나타납니다.
