# Data Leakage Forensic Report

## Conversation-Level Leakage
| Split Pair | Overlapping Conv IDs | Status |
|---|---|---|
| train_val | 0 | PASS |
| train_test | 0 | PASS |
| val_test | 0 | PASS |
| train_golden | 200 | FAIL |
| val_golden | 0 | PASS |
| test_golden | 0 | PASS |

## Message-Level Leakage
| Split Pair | Overlapping Messages | Status |
|---|---|---|
| train_val | 7 | FAIL |
| train_test | 4 | FAIL |
| val_test | 2 | FAIL |
| train_golden | 200 | FAIL |
| val_golden | 2 | FAIL |
| test_golden | 2 | FAIL |
