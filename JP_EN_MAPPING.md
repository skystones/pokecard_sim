# 日本語 ↔ 英語（プログラム上の表記）対応表

この表は、シミュレータ実装で使うID（`id` / `effect_id`）と日本語名の対応を、レビューしやすい形でまとめたものです。

## 1) カード名（日本語が左）

| 日本語 | 英語（プログラム上の表記） |
|---|---|
| ひかるライチュウ | `shining_raichu` |
| ひかるカブトプス | `shining_kabutops` |
| メタモン | `ditto_expansion_sheet` |
| マルマイン | `electrode_base` |
| ビリリダマ | `voltorb_expansion_sheet` |
| コラッタ | `rattata_team_rocket` |
| アンノーンE | `unown_e_pf2` |
| ゴース | `gastly_expansion_sheet` |
| オーキドはかせ | `professor_oak` |
| マサキ | `bill` |
| クルミ | `kurumi` |
| マサキの転送装置 | `bills_teleporter` |
| ポケモン回収 | `pokemon_scoop_up` |
| エリカ | `erika` |
| ナツメの眼 | `sabrinas_gaze` |
| まきちらせベトベトガス | `sticky_gas` |
| ミニスカート | `miniskirt` |
| にせオーキドはかせ | `impostor_professor_oak` |
| ロケット団参上 | `team_rocket_announcement` |
| ポケモン交換おじさん | `pokemon_trader` |
| 礼儀作法 | `etiquette` |
| リサイクル | `recycle` |
| ワープポイント | `warp_point` |
| 水エネルギー | `water_energy` |
| なんでもなおし配合エネルギー | `full_heal_energy` |

## 2) 効果名（日本語が左）

> 注: 効果IDは実装上の識別子です。カードIDと同名のものもあります。

| 日本語（効果の呼び名） | 英語（プログラム上の表記） |
|---|---|
| オーキドはかせ効果 | `professor_oak` |
| マサキ効果 | `bill` |
| クルミ効果 | `kurumi` |
| マサキの転送装置効果 | `bills_teleporter` |
| ポケモン回収効果 | `pokemon_scoop_up` |
| エリカ効果 | `erika` |
| ナツメの眼効果 | `sabrinas_gaze` |
| まきちらせベトベトガス効果 | `sticky_gas` |
| ミニスカート効果 | `miniskirt` |
| にせオーキドはかせ効果 | `impostor_professor_oak` |
| ロケット団参上効果 | `team_rocket_announcement` |
| ポケモン交換おじさん効果 | `pokemon_trader` |
| 礼儀作法効果 | `etiquette` |
| リサイクル効果 | `recycle` |
| ワープポイント効果 | `warp_point` |
| 水エネルギー付与効果 | `water_energy` |
| なんでもなおし配合エネルギー効果 | `full_heal_energy` |
| サンダースコール | `thunder_squall` |
| いなずまぎり | `lightning_slash` |
| ウォータースラッシュ | `water_slash` |
| すごいへんしん | `great_transform` |
| エネエネ | `eneene` |
| でんきショック | `electric_shock` |
| みんなでスパーク | `group_spark` |
| わるふざけ | `mischief` |
| かみつく | `bite` |
| ENGAGE | `engage` |
| めざめるパワー | `hidden_power` |
| こわがらせる | `scare` |
| あんこく | `darkness` |
| でんげき | `electricity` |


## 3) ルール用語（日本語が左）

| 日本語（ルール用語） | 英語（プログラム上の表記） |
|---|---|
| 手札 | `hand` |
| 山札 | `deck` |
| トラッシュ | `discard` |
| サイド | `prizes` |
| バトル場 | `active` |
| ベンチ | `bench` |
| ターン終了 | `end_turn` |
| 手札からバトル場に出す | `set_active_from_hand` |
| 手札からベンチに出す（たね） | `bench_basic_from_hand` |
| 手札から進化 | `evolve_from_hand` |
| トレーナーを使う | `play_trainer` |
| エネルギーをつける | `attach_energy` |
| にげる | `retreat` |
| 効果で入れ替える | `switch_by_effect` |
| 特殊能力を使う | `use_pokemon_power` |
| ワザを使う | `use_attack` |
| 手札から選ぶ | `choose_card_from_hand` |
| 山札から選ぶ | `choose_card_from_deck` |
| トラッシュから選ぶ | `choose_card_from_discard` |
| 場のポケモンを選ぶ | `choose_pokemon_in_play` |
| サイドを取る | `choose_prize` |
| トラッシュするエネルギーを選ぶ | `choose_energy_to_discard` |
| エネルギータイプを選ぶ | `choose_energy_type` |
