# Kannada Language Human Review

Status: `NEEDS_HUMAN_REVIEW`

This artifact identifies farmer-facing Kannada text and terminology requiring review. No claim of native-speaker validation is made.

## Existing Kannada prompts/templates

- `ಯಾವ ಭಾಗದಲ್ಲಿ ಸಮಸ್ಯೆ ಕಾಣಿಸುತ್ತಿದೆ?`
- `ಮಣ್ಣು ಒದ್ದೆಯೇ ಅಥವಾ ಒಣಗಿದೆಯೇ?`
- `ಎಲೆಗಳಲ್ಲಿ ಕಲೆ, ಕೀಟ ಅಥವಾ ಮುರುಕು ಕಾಣಿಸುತ್ತಿದೆಯೇ?`
- `ಎಷ್ಟು ಗಿಡಗಳಿಗೆ ಈ ಸಮಸ್ಯೆ ಇದೆ?`
- `ನಿಮ್ಮ ಟೊಮೆಟೋ ಗಿಡದ ಸಮಸ್ಯೆಯನ್ನು ಅರ್ಥಮಾಡಿಕೊಳ್ಳಲು ಇನ್ನಷ್ಟು ಮಾಹಿತಿ ಬೇಕಾಗಿದೆ.`
- `ಲಕ್ಷಣಗಳನ್ನು ಗಮನಿಸಿ ಮತ್ತು ಸ್ಪಷ್ಟವಾದ ಫೋಟೋಗಳನ್ನು ತೆಗೆದುಕೊಳ್ಳಿ.`
- `ಖಚಿತ ಕಾರಣ ತಿಳಿಯುವವರೆಗೆ ಔಷಧಿ ಅಥವಾ ರಸಗೊಬ್ಬರ ಪ್ರಮಾಣವನ್ನು ಬಳಸಬೇಡಿ.`

## Terminology for review

| Term/phrase | Current use | Reviewer outcome | Suggested correction | Notes |
|---|---|---|---|---|
| ಟೊಮೆಟೋ | crop name | pending |  | Check regional preference |
| ಹಳದಿ | yellowing | pending |  | Check symptom context |
| ಬಾಡುತ್ತ | wilting | pending |  | Check colloquial variants |
| ಒಣಗುತ್ತ | drying | pending |  | Check leaf versus whole-plant meaning |
| ಕಂದು ಕಲೆ | brown spots | pending |  | Check farmer comprehension |
| ಬಿಳಿ ಕೀಟ / ಬಿಳಿ ಹುಳು | whitefly observation | pending |  | Do not assume species from appearance alone |
| ಹಣ್ಣುಗಳಲ್ಲಿ ರಂಧ್ರ | fruit entry holes | pending |  | Check natural spoken wording |
| ಎಲೆಗಳಲ್ಲಿ ಗೆರೆ | leaf-miner trail observation | pending |  | Confirm non-diagnostic wording |

## Known limitations

Romanized Kannada such as `tomato ele haladi agtide` is not broadly supported. Code-mixed behavior is limited to reviewed patterns. Reviewers should mark wording as `correct`, `needs_correction`, `unnatural`, `ambiguous`, or `missing_regional_variant` without silently changing production text.
