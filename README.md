# oldback-solitaire-sim

ポケモンカード旧裏の「ソリティア系デッキ」の再現・検証を目的にしたシミュレータです。  
手札/山札/ベンチ/トラッシュなどの状態遷移を扱い、ルールに従った合法手の列挙、ログ出力、目的達成度の評価、強化学習による方策学習までを一貫して実行できます。

## セットアップ

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## 強化学習の実行方法（必須）

本リポジトリには、`oldback_sim.learning.train_rl` をエントリポイントにした学習スクリプトが実装されています。

### 1) 学習実行

```bash
python -m oldback_sim.learning.train_rl \
  --deck decks/shining_raichu_v1.yaml \
  --opponent-deck decks/opponent_stub.yaml \
  --episodes 200 \
  --seed 0 \
  --lr 1e-3 \
  --out-model artifacts/rl_model.pt \
  --out-log artifacts/rl_train_log.jsonl
```

主な引数:
- `--deck`: 自分側デッキ YAML
- `--opponent-deck`: 相手側デッキ YAML
- `--episodes`: エピソード数
- `--seed`: 乱数シード
- `--lr`: 学習率
- `--out-model`: 学習済みモデルの保存先
- `--out-log`: 学習ログ（JSONL）の保存先
- `--init-model`: 既存チェックポイントを指定して継続学習（任意）

### 2) 学習済み方策の利用

`RLAgent` は `model_path` に保存済みチェックポイントを渡して利用します。`ActionEncoder` のテンプレートIDと行動マスクにより、合法手のみから選択される想定です。

## 手法の説明（必須）

この実装は、**マスク付き方策勾配（REINFORCE系の簡易更新）**を採用しています。

- 観測: `ObservationEncoder` でベクトル化
- 行動空間: `ActionEncoder` でテンプレートID化
- 合法手制約: `get_action_mask()` で不正手を無効化（logitsへ大きな負値を付与）
- 方策: 2層MLP（`Linear( obs_dim -> 128 -> 128 -> act_dim )` + ReLU）
- 損失: `-log π(a|s) * reward` を逐次更新
- 報酬: 進捗サブゴールの達成差分に基づく dense 報酬 + 終端ボーナス

報酬設計の要点:
- ステップペナルティ（無駄手の抑制）
- ハード達成条件の中間サブゴール達成で加点
- ソフト目標達成で加点
- 目的違反/違法手で大きな減点
- ハード成功時に終端ボーナス

※ 相手行動は現状、`opponent` の合法手先頭を選ぶ簡易ポリシーです（学習対象は self 側）。

## 実装されているゲームシステム（必須）

`oldback_sim.engine` / `oldback_sim.cards` を中心に、以下が実装されています。

- **状態管理**: 山札・手札・バトル場・ベンチ・トラッシュ・サイド相当のゾーン管理
- **初期化処理**: デッキ読み込み後のゲーム初期状態生成
- **ルール適用**: 現在状態に応じた合法行動の列挙
- **行動実行**: アクション適用と状態遷移
- **カード効果**: トレーナー/ポケモン/エネルギーの効果処理
- **観測生成**: エージェント用観測オブジェクトの生成
- **ログ**: イベントログ蓄積と目的進捗評価連携
- **目的評価**: Shining Raichu プランに基づく hard/soft 条件判定

また `experiments/` には、シミュレーション実行、失敗分析、分岐分析、デッキ比較、エージェント比較の補助スクリプトが含まれます。

## 実装されているテスト項目（必須）

`tests/` には以下の観点のテストが実装されています。

- **初期化/再現性**
  - 状態初期化の整合性
  - RNG シードによる再現性
- **デッキ/カード定義**
  - デッキ読み込みの妥当性
  - カード定義網羅の確認
- **ルール/行動**
  - 合法手列挙の妥当性
  - トレーナーカード使用処理
  - 個別トレーナー効果検証
- **目的関数/スコア**
  - objective モード挙動
  - 目標達成判定・スコアリング
- **レビュー要件回帰**
  - prompt 系要件（`prompt5`, `prompt6`, `prompt15`）の回帰確認

実行コマンド:

```bash
pytest -q
```

## 代表的な実験スクリプト

```bash
python -m oldback_sim.experiments.run_simulation
python -m oldback_sim.experiments.evaluate_agents
python -m oldback_sim.experiments.compare_decks
python -m oldback_sim.experiments.analyze_failures
python -m oldback_sim.experiments.branch_analysis
```

## ディレクトリ構成（抜粋）

- `src/oldback_sim/engine/`: ゲーム状態・ルール・シミュレータ
- `src/oldback_sim/cards/`: カード定義・効果処理
- `src/oldback_sim/agents/`: ランダム/ヒューリスティック/探索/RL エージェント
- `src/oldback_sim/learning/`: 環境・エンコーダ・報酬・学習/評価
- `src/oldback_sim/objectives/`: 目標定義・達成判定
- `tests/`: テストスイート
- `decks/`: デッキ定義
