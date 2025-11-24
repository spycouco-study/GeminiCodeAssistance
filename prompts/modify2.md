[사용자 요청: {user_query}]
[사용자 질문: {user_question}]
이 것은 하나의 TypeScript 파일로 구동되는 게임에 대한 수정 요청과 게임에 대한 질문입니다.

## 게임 폴더 구조

root/
├─ index.html
├─ game.ts
└─ data.json

## 현재의 game.ts 코드

{original_code}

## 현재의 data.json 데이터

{original_data}

## 구현 원칙

1. 게임의 규칙, 물리 처리, 입력 처리, UI 등 모든 핵심 '로직'을 하나의 TypeScript 코드 파일로 구현합니다. 이 파일은 `fetch('data.json')`의 설정을 읽어 실행해야 합니다.
2. 게임 내 모든 콘텐츠, 밸런스, 설정 값 등 '데이터'를 하나의 JSON 데이터 파일로 구현합니다. 비개발자가 수정하기 가장 쉬운 형태여야 합니다.
3. 게임은 하나의 `<canvas id="gameCanvas">` 요소에 모두 표시되어야 하며 index.html의 내용은 변경할 수 없습니다. 만약 HTML요소가 필요하다면 TypeScript에서 동적으로 생성하는 방법을 사용하세요.
4. 게임 내의 모든 시각 오브젝트는 assets 폴더에서 png 파일을 불러와 그려져야 합니다. 단, 오브젝트의 크기는 이미지 크기에 종속적이지 않으며, 이미지가 오브젝트 크기에 맞춰 스케일링 되어 그려져야 합니다.
5. 게임 내에 모든 효과음과 배경음악은 assets 폴더에서 mp3 파일을 불러와 재생되어야 합니다.
6. 첫 실행 시 게임을 바로 시작하지 말고 타이틀 화면에서 대기하다가 사용자의 입력을 받은 후에 시작 합니다.
7. 3D게임의 경우 HTML에 아래와 같이 관련 라이브러리를 CDN에서 가져오도록 모듈 맵핑(Module Mapping)을 정의하고 있습니다. TypeScript 코드에서 Three.js와 Cannon.js를 import하고 활용해 주세요.
   <script type="importmap">
   {{
   "imports": {{
   "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
   "three/": "https://cdn.jsdelivr.net/npm/three@0.160.0/",
   "three/examples/jsm/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/",
   "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/",
   "cannon-es": "https://cdn.jsdelivr.net/npm/cannon-es@0.20.0/dist/cannon-es.js"
   }}
   }}
   </script>

응답은 반드시 아래의 커스텀 형식에 맞춰주세요. 어떠한 설명이나 마크다운 구문(```)도 태그 외부에 넣지 마세요. 태그 내부에는 아래에 명시된 지침문은 제거하고 생성한 내용만 넣으세요.

###CODE_START###
game.ts에 저장될 TypeScript 코드를 이곳에 넣으세요. 만약 변경된 내용이 없다면 비워두세요.
###CODE_END###

###DATA_START###
data.json에 저장될 JSON 데이터 전체를 이곳에 넣으세요. 만약 변경된 내용이 없다면 비워두세요.
###DATA_END###

###DESCRIPTION_START###
작업한 내용에 대한 간단한 설명을 이곳에 넣으세요.
'사용자 질문'이 있는 경우에만 그에 대한 답변도 이곳에 넣어 주세요.
###DESCRIPTION_END###
