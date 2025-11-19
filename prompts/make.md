[사용자 요청: {user_query}]
[사용자 질문: {user_question}]
이 것은 하나의 TypeScript 파일로 구동되는 게임을 만들기 위한 요청과 게임에 대한 질문입니다.

## 게임 폴더 구조 ##
root/
├─ game.ts
├─ data.json
└─ assets/

## 구현 원칙 ##
1. 게임의 규칙, 물리 처리, 입력 처리 등 모든 핵심 '로직'을 하나의 TypeScript 코드 파일로 구현합니다. 이 파일은 `fetch('data.json')`의 설정을 읽어 실행해야 합니다.
2. 게임 내 모든 콘텐츠, 밸런스, 설정 값 등 '데이터'를 하나의 JSON 데이터 파일로 구현합니다. 비개발자가 수정하기 가장 쉬운 형태여야 합니다.
3. 게임은 HTML에서 `<canvas id="gameCanvas">` 요소에 표시되어야 합니다.
4. 게임 내의 모든 시각 오브젝트는 assets 폴더에서 png 파일을 불러와 그려져야 합니다. 단, 오브젝트의 크기는 이미지 크기에 종속적이지 않으며, 이미지가 오브젝트 크기에 맞춰 스케일링 되어 그려져야 합니다.
5. 게임 내에 모든 효과음과 배경음악은 assets 폴더에서 mp3 파일을 불러와 재생되어야 합니다.
6. 첫 실행 시 게임을 바로 시작하지 말고 타이틀 화면에서 대기하다가 사용자의 입력을 받은 후에 시작 합니다.

응답은 반드시 아래의 커스텀 형식에 맞춰주세요. 어떠한 설명이나 마크다운 구문(```)도 태그 외부에 넣지 마세요. 태그 내부에는 아래에 명시된 지침문은 제거하고 생성한 내용만 넣으세요.

###CODE_START###
game.ts에 저장될 TypeScript 코드를 이곳에 넣으세요.
###CODE_END###

###DATA_START###
data.json에 저장될 JSON 데이터 전체를 이곳에 넣으세요.
게임에 사용된 이미지와 사운드 Asset 파일의 정보도 아래 예시와 같은 형식으로 포함시켜 로딩에 사용하세요. "assets"는 최상위 레벨에 있어야 합니다. 이미지는 png형식이어야 하고 name, path, width, height를 반드시 포함해야 합니다. 사운드는 mp3형식이어야 하고 name, path, duration_seconds, volume을 반드시 포함해야 합니다.
"assets": {{
    "images": [
        {{ "name": "player", "path": "assets/player.png", "width": 64, "height": 64 }},
        {{ "name": "player_bullet", "path": "assets/player_bullet.png", "width": 10, "height": 20 }}
    ],
    "sounds": [
        {{ "name": "effect", "path": "assets/effect.mp3", "duration_seconds": 1.0, volume: 1.0 }},
        {{ "name": "bgm", "path": "assets/bgm.mp3", "duration_seconds": 60.0, volume: 0.5 }}
    ]
}}
###DATA_END###

###DESCRIPTION_START###
작업한 내용에 대한 간단한 설명을 이곳에 넣으세요.
'사용자 질문'이 있는 경우에만 그에 대한 답변도 이곳에 넣어 주세요.
###DESCRIPTION_END###