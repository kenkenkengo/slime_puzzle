# Slime Puzzle

ぷるぷるスライムを操作して、伸ばして、分裂させて、ゴールを目指す2D物理パズルゲーム。

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Pygame](https://img.shields.io/badge/Pygame--CE-2.5+-green)
![pymunk](https://img.shields.io/badge/pymunk-6.6+-orange)

## 遊び方

| 操作 | 説明 |
|------|------|
| 左ドラッグ | スライムを引っ張って移動 |
| 右クリック | スライムを分裂 |
| 近づける | 分裂したスライムが自動で合体 |
| R | リスタート |
| ESC | レベル選択に戻る |
| Space | レベルクリア後、次のレベルへ |

## セットアップ

```bash
git clone git@github.com:kenkenkengo/slime_puzzle.git
cd slime_puzzle
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 起動

```bash
python run.py
```

## レベル

| # | 名前 | ポイント |
|---|------|----------|
| 1 | First Steps | ドラッグで隙間を越える |
| 2 | The Squeeze | 狭い通路を変形して通過 |
| 3 | Divide and Conquer | 分裂して壁の隙間を突破 |
| 4 | Spike Alley | スパイクを避けて足場を登る |
| 5 | The Gauntlet | 分裂・合体・回避の総合ステージ |

## 仕組み

- **ソフトボディ物理**: pymunkのバネ制約で繋がった粒子メッシュでスライムを表現
- **分裂**: クリック位置で粒子群を2つに分割し、それぞれ独立したスライムとして再構築
- **合体**: 一定時間近くにいると粒子を統合して1つのスライムに再構成
- **ハザード**: スパイクに触れた粒子は消滅。全粒子を失うと自動リスタート

## 技術スタック

- **Python 3.10+**
- **Pygame-CE** - 描画・入力・ゲームループ
- **pymunk** - 2D物理エンジン（Chipmunkラッパー）

## プロジェクト構成

```
src/
├── constants.py          # 定数・物理パラメータ
├── game.py               # メインゲームループ
├── physics/
│   ├── physics_world.py  # pymunk Space ラッパー
│   ├── slime_body.py     # ソフトボディスライム
│   └── slime_manager.py  # 分裂・合体管理
├── entities/
│   ├── terrain.py        # 地形
│   ├── goal_zone.py      # ゴールエリア
│   └── hazard.py         # スパイク等の障害物
├── input/
│   └── input_handler.py  # マウス操作
├── rendering/
│   ├── slime_renderer.py # スライム描画
│   ├── terrain_renderer.py
│   └── ui_renderer.py    # HUD・ボタン
├── levels/
│   ├── level_loader.py   # JSONレベル読み込み
│   └── level_data/       # レベル定義(JSON)
└── states/
    ├── state_machine.py  # ステート管理
    ├── menu_state.py     # タイトル画面
    ├── level_select_state.py
    └── play_state.py     # ゲームプレイ
```

## ライセンス

MIT
