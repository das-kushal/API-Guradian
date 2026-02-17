### React Frontend

- Upload Old Spec

- Upload New Spec

- Display:

   - Breaking Changes

    - Risk Score

    - AI Summary

    - Suggested Fixes

### Flask Backend

#### Endpoints:

| Endpoint     | Purpose | 
| ----------- | ----------- | 
| POST /upload |	Upload specs|
| POST /analyze |	Run diff + AI|
| GET /report/{id} |	Get analysis|



 

### Diff Engine (Non-AI Logic)

- You write logic to detect:

- Removed endpoints

- Method changes

- Required field changes

- Type changes



### AI Analyzer

#### Used for:

- Security review

- PII detection

- Semantic API review

- Documentation quality scoring

- Executive summary