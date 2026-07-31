# Week 12 Final Project Facts

## Project Information

- Project name: CESPPL FieldVision Platform
- Number of classes: 10
- GitHub repository: https://github.com/anuhya901-cell/cesppl-fieldvision-platform
- Live Streamlit URL: https://cesppl-fieldvision-platform-gtpf8kowghde9na7kugdgb.streamlit.app/
- Recommended Python version: 3.11

## Dataset Information

- Expected image count from mentor: 4144
- Actual raw files found: 4179
- Processed images after deduplication: 3616
- Train images: 2530
- Validation images: 543
- Test images: 543

## Final Model Information

- Final selected backbone: EfficientNetB0
- Input image size: 224 × 224 pixels
- Dropout: 0.3
- Optimizer: Adam
- Learning rate:  0.001 (1e-3)
- Class weighting used: yes
- Fine-tuning used: yes
- Final model file: models/final_model.keras

## Final Results

- Best validation accuracy: 95.40%
- Final test accuracy: 95.03%
- Final macro-F1: 93.20%
- Final test loss:
- Selected experiment name:  run_07_canonical

## Per-Class Results

|     class                  | Precision    | Recall    | F1-score   | Support |
|---                         |---:          |---:       |---:        |---:     |
| BIN LIFTING                | 1.000        | 1.000     | 1.000      | 25      |
| BIN WASHING                | 0.923        | 0.980     | 0.950      | 49      |
| GATE MEETING               | 0.962        | 0.944     | 0.953      | 54      |
| LFC                        | 0.875        | 0.700     | 0.778      | 20      |
| MANUAL BEACH CLEANING      | 0.966        | 0.995     | 0.980      | 199     |  
| MECHANICAL SWEEPING        | 1.000        | 0.926     | 0.962      | 27      |
| MECHANIZED BEACH CLEANING  | 0.968        | 0.968     | 0.968      | 31      |
| PRIMARY COLLECTION         | 0.842        | 1.000     | 0.914      | 16      |  
| ROAD SWEEPING              | 0.923        | 0.923     | 0.923      | 78      |
| SECONDARY VEHICLES         | 0.949        | 0.841     | 0.892      | 44      |

## Important Confusion Pairs

- LFC → ROAD SWEEPING (3 samples)
- LFC → MANUAL BEACH CLEANING (2 samples)
- ROAD SWEEPING → BIN WASHING (2 samples)
- ROAD SWEEPING → LFC (2 samples)
- SECONDARY VEHICLES → BIN WASHING (2 samples)
- SECONDARY VEHICLES → MANUAL BEACH CLEANING (2 samples)

## Final Files Available

- Model card: MODEL_CARD.md
- Data card: README.md
- Dashboard specification: DASHBOARD_SPEC.md
- Final report: FINAL_REPORT.md
- Confusion matrix image: final_results/confusion_matrix.png
- Class imbalance chart: class_imbalance_chart.png
- Dashboard screenshot: dashboard_screenshot.png
- Dashboard GIF: dashboard_demo.gif