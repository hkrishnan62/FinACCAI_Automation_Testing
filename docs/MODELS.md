# Model files

The repository previously contained large model files (`.safetensors`). These are now tracked using Git LFS and should not be committed directly.

If you need the models locally, fetch them via LFS after cloning:

1. git clone https://github.com/hkrishnan62/FinACCAI_Automation_Testing.git
2. cd FinACCAI_Automation_Testing
3. git lfs install
4. git lfs pull

Alternatively, download the models from the external storage (S3 or Hugging Face) if provided by the project maintainers.

**Note:** Because history was rewritten to migrate the files to LFS, existing clones should re-clone the repository to avoid inconsistencies.
