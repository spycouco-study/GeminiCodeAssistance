[사용자 요청: {user_query}]
이 것은 하나의 TypeScript 파일로 구동되는 게임을 만들기 위한 요청입니다. 게임은 'gameCanvas'에 표시되어야 합니다. 게임 코드를 생성하고 간단히 설명도 해주세요. 응답은 반드시 아래의 커스텀 형식에 맞춰주세요. 어떠한 설명이나 마크다운 구문(```)도 태그 외부에 넣지 마세요. 태그 내부에는 아래에 명시된 지침문은 제거하고 생성한 내용만 넣으세요.

###CODE_START###
game.ts에 저장될 TypeScript 코드를 이곳에 넣으세요.
###CODE_END###

###DATA_START###
data.json에 저장될 JSON 데이터 전체를 이곳에 넣으세요.
###DATA_END###

###ASSET_LIST_START###
코드 안에 사용된 이미지 또는 사운드 Asset 파일이 있다면 아래와 같이 json형태로 넣어주세요.
{{
    "images": [
        {{
            "file_name": "character_walk.png",
            "resolution": {{
                "width": 1024,
                "height": 512
            }}
        }}
    ],
    "sounds": [
        {{
            "file_name": "town_bgm.mp3",
            "duration_seconds": 1.0
        }}
    ]
}}
###ASSET_LIST_END###

###DESCRIPTION_START###
작업한 내용에 대한 간단한 설명을 이곳에 넣으세요.
###DESCRIPTION_END###