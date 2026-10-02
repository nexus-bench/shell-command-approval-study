# Extension results

Counts describe these fixtures and policies, not real-world failure rates.

| Run | Set/split | N | Useful allow | Deny approved | Unresolved ask approved | Resolved ask approved | Errors | p50 ms |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| inspect-consistency | evidence-v3/dev | 18 | 6 | 0 | 0 | 0 | 0 | 4121 |
| inspect-v3 | evidence-v3/dev | 24 | 6 | 0 | 0 | 0 | 0 | 4329 |
| inspect-v3 | evidence-v3/test | 24 | 6 | 0 | 0 | 0 | 0 | 4457 |
| prefetch-diagnostic | evidence-v3/dev | 24 | 6 | 2 | 0 | 6 | 0 | 4202 |
| prefetch-diagnostic | evidence-v3/test | 24 | 6 | 0 | 0 | 6 | 0 | 4263 |
| qwen-code-v3 | evidence-v3/dev | 24 | 6 | 6 | 10 | 0 | 0 | 6089 |
| qwen-code-v3 | evidence-v3/test | 24 | 6 | 6 | 8 | 0 | 2 | 6084 |
| qwen-code-v3 | legacy-v2/dev | 36 | 14 | 10 | 12 | 0 | 0 | 6057 |
| qwen-code-v3 | legacy-v2/test | 36 | 12 | 12 | 12 | 0 | 0 | 6036 |
| secguard-full-adversarial-recorded† | adversarial/diagnostic | 12 | 6 | 4 | 2 | 0 | 0 | 174 |
| secguard-full-public-recorded† | shellrisk/reference | 100 | 47 | 49 | 0 | 0 | 0 | 176 |
| secguard-full-public-recorded† | shellsafety/reference | 100 | 46 | 42 | 0 | 0 | 0 | 173 |
| secguard-full-v3-recorded† | evidence-v3/dev | 24 | 6 | 6 | 12 | 0 | 0 | 168 |
| secguard-full-v3-recorded† | evidence-v3/test | 24 | 6 | 6 | 12 | 0 | 0 | 163 |
| secguard-full-v3-recorded† | legacy-v2/dev | 36 | 14 | 10 | 12 | 0 | 0 | 165 |
| secguard-full-v3-recorded† | legacy-v2/test | 36 | 12 | 12 | 12 | 0 | 0 | 169 |
| secguard-native-model-adversarial-recorded | adversarial/diagnostic | 12 | 6 | 4 | 2 | 0 | 0 | 173 |
| secguard-native-model-public-recorded | shellrisk/reference | 100 | 50 | 50 | 0 | 0 | 0 | 177 |
| secguard-native-model-public-recorded | shellsafety/reference | 100 | 50 | 49 | 0 | 0 | 0 | 174 |
| secguard-native-model-v3-recorded | evidence-v3/dev | 24 | 6 | 6 | 12 | 0 | 0 | 172 |
| secguard-native-model-v3-recorded | evidence-v3/test | 24 | 6 | 6 | 12 | 0 | 0 | 175 |
| secguard-native-model-v3-recorded | legacy-v2/dev | 36 | 14 | 10 | 12 | 0 | 0 | 173 |
| secguard-native-model-v3-recorded | legacy-v2/test | 36 | 12 | 12 | 12 | 0 | 0 | 170 |
| secguard-release-adversarial-verified | adversarial/diagnostic | 12 | 6 | 4 | 2 | 0 | 0 | 6 |
| secguard-release-public-verified | shellrisk/reference | 100 | 47 | 49 | 0 | 0 | 0 | 6 |
| secguard-release-public-verified | shellsafety/reference | 100 | 46 | 43 | 0 | 0 | 0 | 6 |
| secguard-release-v3 | evidence-v3/dev | 24 | 6 | 6 | 12 | 0 | 0 | 7 |
| secguard-release-v3 | evidence-v3/test | 24 | 6 | 6 | 12 | 0 | 0 | 7 |
| secguard-release-v3 | legacy-v2/dev | 36 | 14 | 10 | 12 | 0 | 0 | 7 |
| secguard-release-v3 | legacy-v2/test | 36 | 12 | 12 | 12 | 0 | 0 | 8 |
| single-v3 | evidence-v3/dev | 24 | 6 | 2 | 0 | 0 | 0 | 4182 |
| single-v3 | evidence-v3/test | 24 | 6 | 0 | 0 | 0 | 0 | 4222 |
| two-stage-v3 | evidence-v3/dev | 24 | 6 | 2 | 12 | 0 | 0 | 8408 |
| two-stage-v3 | evidence-v3/test | 24 | 6 | 0 | 9 | 0 | 0 | 8434 |

† All classifier responses were collected, but the native process failed during teardown. See run-status.json and the run’s shutdown.txt. Teardown failures are not safety verdicts.
