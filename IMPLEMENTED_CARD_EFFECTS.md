# 実装済みカード効果一覧（レビュー用）

この文書は、`src/oldback_sim/cards/effects/*.py` と、アクション接続部 `src/oldback_sim/engine/{rules,simulator}.py` を読み、
**実際にエフェクト関数として実装されている内容**を整理したものです。

## トレーナーカード

- **professor_oak（オーキドはかせ）**: 手札をすべて捨てて7枚引く。
- **bill（マサキ）**: 2枚引く。
- **kurumi（クルミ）**: 2枚引いた後、指定2枚（既定は手札先頭2枚）を山札へ戻してシャッフル。
- **bills_teleporter（マサキの転送装置）**: コイントス成功で4枚引く（失敗なら0枚）。
- **pokemon_scoop_up（ポケモン回収）**: 対象ポケモンを手札に戻し、そのポケモンの付属カードをトラッシュ。
- **erika（エリカ）**: 自分/相手がそれぞれ指定枚数ドロー（既定3/3）。
- **sabrinas_gaze（ナツメの眼）**: お互い手札を山札へ戻してシャッフルし、元の手札枚数分引き直す。
- **sticky_gas（まきちらせベトベトガス）**: `goop_gas_active` を有効化（ポケモンパワーを封じる分岐あり）。
- **miniskirt（ミニスカート）**: お互い手札中のトレーナーを山札に戻してシャッフル。
- **impostor_professor_oak（にせオーキドはかせ）**: 相手のみ手札を山札に戻して7枚引き直す。
- **team_rocket_announcement（ロケット団参上）**: お互いのサイドを全公開扱いにするフラグを立てる。
- **pokemon_trader（ポケモン交換おじさん）**: 手札ポケモン1枚を山札へ戻し、山札ポケモン1枚を手札へ。
- **etiquette（礼儀作法）**: 山札から基本ポケモン1枚を手札へ取り、山札シャッフル。
- **recycle（リサイクル）**: コイントス成功時、トラッシュの指定カード1枚を山札トップへ。
- **warp_point（ワープポイント）**: 相手→自分の順に、ベンチがいれば指定インデックスでバトル場入れ替え。

## エネルギーカード

- **water_energy（水エネルギー）**: 指定ポケモンへ水1個分として付与。
- **full_heal_energy（なんでもなおし配合エネルギー）**: 指定ポケモンへ無色1個分として付与。

## ポケモン由来の効果ID（攻撃/ポケモンパワー）

- **thunder_squall**: 相手バトル場40ダメージ。さらに相手ベンチ1体に `water_energy_count * 10` ダメージ（抵抗力無視フラグ）。
- **lightning_slash**: コイン表なら40ダメージ＋相手ベンチ全員10、裏なら30ダメージ＋自分へ10。
- **water_slash**: 相手バトル場へ50 + `extra_water * 10` ダメージ（抵抗力無視フラグ）。
- **great_transform**: 成功時、Dittoの変身先を `transform_target::*` フラグに記録。失敗時は解除。
- **eneene**: 使用元をきぜつ扱いにし、相手がサイド1枚取得。指定対象に選択色2個分の特殊エネルギーを付与。
- **electric_shock**: 相手バトル場へ10ダメージ、コイン表でマヒ付与。
- **group_spark**: 場の `voltorb` 文字列を含む枚数を数え、20 + 10×枚数ダメージ。
- **mischief**: 自分のサイド1枚と山札トップを交換。
- **bite**: 相手バトル場へ20ダメージ。
- **engage**: 指定フラグに応じて、自分/相手が手札を戻して4枚引き直す。
- **hidden_power**: 相手バトル場へ10ダメージ。
- **scare**: 相手のトレーナー使用をターン終了まで禁止。
- **darkness**: 相手バトル場へ10ダメージ、コイン表でこんらん付与。
- **electricity**: 相手バトル場へ50ダメージ、コイン裏で自分へ10ダメージ。

## カードIDと効果IDの接続（重要）

- アタック実行は `simulator.py` で `thundersquall -> thunder_squall`、`scare -> scare`、`tackle -> bite` に接続。
- したがって通常攻撃 `tackle` を持つ扱いのポケモンは、実装上すべて **bite（20ダメージ）** を使う。
- ルール側では、
  - `shining_raichu` の攻撃IDは `thundersquall`
  - `gastly_expansion_sheet` の攻撃IDは `scare`
  - それ以外は `tackle`
 となる。
- ポケモンパワーは、
  - `ditto_expansion_sheet` が `great_transform`
  - `electrode_base` が `eneene`
 で生成される。

## レビュー観点（実装を読む限りの注意点）

- `great_transform` の分岐が同一ファイル内に重複しており、後半分岐は到達しない（前半で `return`）。
- `eneene` の色許可値が `ENERGY_COLORS` では `darkness` だが、行動生成側は `dark` を候補にしており不一致。
- `sticky_gas` で立てるフラグ名は `goop_gas_active` だが、ルール側チェックは `sticky_gas_active` を参照しており不一致。
