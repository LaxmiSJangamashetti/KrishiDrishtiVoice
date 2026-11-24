# Image Dataset Governance

The repository currently has no acquired image dataset. `IMAGE_DATASET_MANIFEST.json` is intentionally empty and marked `not_acquired`.

Before acquisition, each record must include dataset/version, source URL, license, checksum, crop and class labels, image identifier, collection group, annotation status, human-review status, and split assignment.

Required controls:

- Do not download until license and usage restrictions are verified.
- Keep laboratory and field-image evaluations separate.
- Split by plant/farm/collection group when metadata permits.
- Detect exact and near duplicates before splitting.
- Do not use private farmer images without consent.
- Require Kannada and agricultural expert review for farmer-facing labels.

The dry-run helper `evaluation/prepare_image_dataset.py --dry-run` performs no download.
