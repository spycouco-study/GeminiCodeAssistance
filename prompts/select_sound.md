[필요 사운드 에셋 정보: {sound_asset_info}]
당신은 '필요 사운드 에셋 정보'를 읽고 보유 사운드 리스트에서 각 에셋에 맞는 사운드 파일을 골라서 반환해야 합니다.

## BGM 보유 리스트

```
[BGM]_8bit_[62s]_bgm_loop, [BGM]_8bit_[75s]_slowdrum - Track 01 (cave), [BGM]_8bit_[96s]_wef, [BGM]_Action_Rock_[102s]_sweet-life-luxury-chill-438146, [BGM]_Action_Rock_[111s]_dont-talk-315229, [BGM]_Action_Rock_[113s]_running-night-393139, [BGM]_Action_Rock_[115s]_gorila-315977, [BGM]_Action_Rock_[132s]_jungle-waves-drumampbass-electronic-inspiring-promo-345013, [BGM]_Action_Rock_[152s]_eona-emotional-ambient-pop-351436, [BGM]_Action_Rock_[161s]_tell-me-what-379638, [BGM]_Action_Rock_[16284s]_2023년 사랑받은 인기팝송 100곡 모두 해석해버리기 ｜ PLAYLIST, [BGM]_Action_Rock_[168s]_Purple Sax, [BGM]_Action_Rock_[169s]_Dwayne Johnson - You're Welcome (from Moana⧸Official Video), [BGM]_Action_Rock_[243s]_Video Music, [BGM]_Action_Rock_[72s]_[브금대통령] (장난⧸엉뚱⧸Comic) Ready To Nap [무료음악⧸브금⧸Royalty Free Music], [BGM]_Action_Rock_[81s]_why, [BGM]_Action_Rock_[81s]_[S] PH Descend, [BGM]_Action_Rock_[96s]_untitled, [BGM]_Action_Rock_[96s]_vlog-beat-background-349853, [BGM]_Action_Rock_[97s]_so-fresh-315255, [BGM]_Action_Rock_[99s]_deep-abstract-ambient_snowcap-401656, [BGM]_Casual_[74s]_future-design-344320, [BGM]_Cyberpunk_[128s]_sandbreaker-379630, [BGM]_Sad_Piano_[107s]_retro-lounge-389644, [BGM]_Sad_Piano_[117s]_groovy-vibe-427121, [BGM]_Sad_Piano_[139s]_cascade-breathe-future-garage-412839, [BGM]_Sad_Piano_[192s]_slowpiano, [BGM]_Sad_Piano_[264s]_[무료BGM] 엉뚱하고 귀여운 브금 🎈 Curious baby, [BGM]_Sad_Piano_[303s]_[무료BGM 모음] 귀엽고 밝은 배경음악 모음💾, [BGM]_Sad_Piano_[359s]_[무료BGM] 귀여운 봄 느낌 브금 🌷 신나는 봄산책, [BGM]_Sad_Piano_[72s]_weird vid music, [BGM]_Village_[125s]_the-last-point-beat-electronic-digital-394291, [BGM]_Village_[140s]_experimental-cinematic-hip-hop-315904, [BGM]_Village_[219s]_starfield_romance1, [BGM]_Village_[224s]_the_budding_of_consciousness, [BGM]_Village_[236s]_hype-drill-music-438398
```

## SFX 보유 리스트

```
[SFX]*Break_Obj_metalPot1, [SFX]_Comm_sfx_06b, [SFX]_Control_you_lose, [SFX]_Destruct_book_03, [SFX]_Device*판타지 마법*bgm_loop, [SFX]_Die_creature_roar_02, [SFX]_Eco_fw_05, [SFX]_Env_Change_bang_03, [SFX]_Explosion_cannon_02, [SFX]_Footstep_stones_02, [SFX]_Gauge_7, [SFX]_Gear_metal_02, [SFX]_General_Click_coin_sfx, [SFX]_Gimmick_doorClose_1, [SFX]_Hit_spell_01, [SFX]_Life_6, [SFX]_Machine*퍼즐-힐링_bgm_loop, [SFX]_Magic_sfx_18b, [SFX]_Melee_knifeSlice, [SFX]_Move_Obj_spell_fire_03, [SFX]_Negative_jingles_SAX10, [SFX]_Phys_Hit_impactPlate_medium_000, [SFX]_Positive_jingles_PIZZI02, [SFX]_Ranged_Hit_retro_explosion_04, [SFX]_Ranged_synth_laser_07, [SFX]_Shout_war_reloading, [SFX]_Special_Click_synth_misc_05, [SFX]_Special_Move_synth_misc_01, [SFX]_Status_Hit_spell_fire_02, [SFX]_Structure_doorOpen_1, [SFX]_System_mission_completed, [SFX]_Text_Log_switch_003, [SFX]_Water_impactGlass_medium_000, [SFX]_Weather_jingles_STEEL07, [SFX][1s]_game_over voice
```

반환은 아래 예시와 같은 JSON형식으로 해주세요.
{{
    "match_result":[
        {{
            "file_name":str,
            "match_item":str
        }},  
 {{
            "file_name":str,
            "match_item":str
        }}
]
}}
