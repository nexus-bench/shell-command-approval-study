| Model / decision / set | Safe or legitimate approved | Deny approved | Unknown approved | Errors | p50 / p95 ms |
|---|---:|---:|---:|---:|---:|
| modernbert/allow/public/shellrisk | 43/50 | 17/50 | 0/0 | 0 | 66.80 / 98.25 |
| modernbert/allow/public/shellsafety | 13/50 | 10/50 | 0/0 | 0 | 62.20 / 81.31 |
| modernbert/allow/v2/dev | 6/14 | 6/10 | 6/12 | 0 | 63.34 / 73.15 |
| modernbert/allow/v2/test | 6/12 | 6/12 | 6/12 | 0 | 62.05 / 101.54 |
| modernbert/allow/adversarial/diagnostic | 0/6 | 0/4 | 0/2 | 0 | 69.13 / 72.38 |
| kestrel/allow/public/shellrisk | 50/50 | 0/50 | 0/0 | 0 | 0.07 / 0.23 |
| kestrel/allow/public/shellsafety | 40/50 | 34/50 | 0/0 | 0 | 0.03 / 0.09 |
| kestrel/allow/v2/dev | 10/14 | 10/10 | 10/12 | 0 | 0.02 / 0.04 |
| kestrel/allow/v2/test | 10/12 | 10/12 | 10/12 | 0 | 0.02 / 0.06 |
| kestrel/allow/adversarial/diagnostic | 4/6 | 2/4 | 2/2 | 0 | 0.02 / 0.04 |
| secguard/allow/public/shellrisk | 50/50 | 50/50 | 0/0 | 0 | 537.74 / 744.67 |
| secguard/allow/public/shellsafety | 50/50 | 49/50 | 0/0 | 0 | 536.47 / 687.20 |
| secguard/label_allow/public/shellrisk | 50/50 | 50/50 | 0/0 | 0 | 537.74 / 744.67 |
| secguard/label_allow/public/shellsafety | 50/50 | 49/50 | 0/0 | 0 | 536.47 / 687.20 |
| secguard/allow/v2/dev | 14/14 | 10/10 | 12/12 | 0 | 510.27 / 5862.83 |
| secguard/allow/v2/test | 12/12 | 12/12 | 12/12 | 0 | 602.73 / 987.91 |
| secguard/label_allow/v2/dev | 14/14 | 10/10 | 12/12 | 0 | 510.27 / 5862.83 |
| secguard/label_allow/v2/test | 12/12 | 12/12 | 12/12 | 0 | 602.73 / 987.91 |
| secguard/allow/adversarial/diagnostic | 6/6 | 4/4 | 2/2 | 0 | 528.42 / 559.09 |
| secguard/label_allow/adversarial/diagnostic | 6/6 | 4/4 | 2/2 | 0 | 528.42 / 559.09 |
