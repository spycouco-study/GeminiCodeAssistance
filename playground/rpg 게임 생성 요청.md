rpg 게임을 만들고 싶어. 플레이어가 전후좌우로 움직일 수 있고 스페이스바를 누르면 주변의 적을 공격하는거야. 아이템도 주워서 확보할 수 있어. 처음엔 마을에서 시작하고 밖으로 나가면 적들이 돌아다녀.

game.ts(311,5): error TS2564: Property 'currentMapData' has no initializer and is not definitely assigned in the constructor.
game.ts(313,5): error TS2564: Property 'width' has no initializer and is not definitely assigned in the constructor.
game.ts(314,5): error TS2564: Property 'height' has no initializer and is not definitely assigned in the constructor.
game.ts(370,5): error TS2564: Property 'player' has no initializer and is not definitely assigned in the constructor.
game.ts(373,5): error TS2564: Property 'map' has no initializer and is not definitely assigned in the constructor.
game.ts(383,9): error TS2322: Type 'CanvasRenderingContext2D | null' is not assignable to type 'CanvasRenderingContext2D'.
Type 'null' is not assignable to type 'CanvasRenderingContext2D'.

게임 데이터는 따로 분리하는게 낫지 않을까?

맵이 화면보다 커서 돌아다니는 맛이 있었으면 좋겠어. 지금은 너무 좁아.

마을 밖으로 나가는 통로가 하나뿐이었으면 좋겠어. 아랫쪽은 막혀있고 윗쪽만 뚫어줘. 그리고 윗쪽으로 나갔을때 마을 밖의 아랫쪽에서 시작해야 자연스러울 것 같아. 마찬가지로 마을 바깥에서 마을로 들어올때는 아랬쪽으로 들어가야겠지.

마을 바깥쪽으로 나가지지가 않고 마을 통로로 가면 다시 마을 시작점으로 이동해. 수정해줘.

적들이 플레이어와 겹쳐지지 않았으면 좋겠어. 그리고 플레이어의 에너지가 다 닳아도 죽지를 않아.

플레이어가 적과 겹쳐서 이동할 수 없었으면 좋겠어. 그리고 적들이 플레이어와 접촉한 상태로 플레이어 방향으로 공격하면 플레이어의 체력도 닳아야지. 그리고 플레이어의 체력이 0이되면 게임이 종료 되어야해.

마을 맵의 윗쪽을 통해 바깥으로 나가면 바깥 맵에서는 아랫쪽에서 시작하는게 자연스러운 것 같아. 반대로 바깥 맵아랫쪽을 통해 마을로 들어오면 마을 윗쪽에서 시작하는게 맞고.

바깥으로 나가는 순간 마을과 바깥쪽을 무한히 오가는 오류가 발생하는 것 같아.