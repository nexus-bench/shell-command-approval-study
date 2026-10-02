### Public source results

| Source / arm | Unsafe allowed ↓ | Legitimate allowed ↑ | Accuracy | p50 / p95 ms |
|---|---:|---:|---:|---:|
| shellrisk / lancet | 17/50 | 46/50 | 79% | 7.0 / 17.7 |
| shellrisk / autoshell-command | 5/50 | 30/50 | 75% | 733.5 / 947.7 |
| shellrisk / autoshell-native | 5/50 | 31/50 | 76% | 811.8 / 1301.3 |
| shellrisk / autoshell-expanded | 5/50 | 31/50 | 76% | 778.5 / 1099.0 |
| shellsafety / lancet | 12/50 | 45/50 | 83% | 5.2 / 8.6 |
| shellsafety / autoshell-command | 0/50 | 44/50 | 94% | 665.2 / 825.1 |
| shellsafety / autoshell-native | 1/50 | 50/50 | 99% | 900.9 / 1052.8 |
| shellsafety / autoshell-expanded | 0/50 | 49/50 | 99% | 1067.4 / 1362.4 |
| shellsafety / autoshell-format-only | 1/50 | 50/50 | 99% | 914.3 / 1152.0 |

### Synthetic challenge results

| Arm | Deny allowed / 44 ↓ | Unknown allowed / 40 ↓ | Legitimate allowed / 44 ↑ | Both-correct pairs / 40 ↑ | Runtime/parser errors | p50 / p95 ms |
|---|---:|---:|---:|---:|---:|---:|
| lancet | 29 | 29 | 31 | 0 | 2 | 4.6 / 6.9 |
| autoshell-command | 19 | 19 | 20 | 0 | 0 | 641.4 / 750.8 |
| autoshell-native | 3 | 16 | 23 | 18 | 3 | 936.3 / 1133.0 |
| autoshell-expanded | 2 | 15 | 23 | 19 | 3 | 996.1 / 1282.6 |

### Repository profiles

Each cell is **unsafe approvals / intervention cases; legitimate approvals / allow cases**.
These profiles have different command families; they are not controlled repository rankings.

| Profile | LANCET | AutoShell command | AutoShell native | AutoShell expanded |
|---|---|---|---|---|
| desktop | 6/8; 3/4 | 4/8; 2/4 | 2/8; 2/4 | 1/8; 2/4 |
| infra | 2/12; 1/6 | 2/12; 1/6 | 0/12; 1/6 | 0/12; 0/6 |
| monorepo | 4/6; 2/3 | 4/6; 2/3 | 2/6; 3/3 | 2/6; 3/3 |
| node | 16/24; 10/14 | 8/24; 5/14 | 3/24; 5/14 | 3/24; 7/14 |
| python | 24/26; 12/13 | 14/26; 7/13 | 9/26; 9/13 | 8/26; 8/13 |
| worktree | 6/8; 3/4 | 6/8; 3/4 | 3/8; 3/4 | 3/8; 3/4 |
