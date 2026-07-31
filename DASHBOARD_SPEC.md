# 🖥️ Dashboard Specification

## 1. Purpose

The CESPPL FieldVision Platform dashboard provides a centralized interface for monitoring, classifying, browsing, and managing municipal field-operation images using AI.

---

## 2. Intended User

The dashboard is designed for administrators responsible for monitoring municipal field operations and reviewing uploaded field images.

---

## 3. Login Behaviour

- Secure administrator login
- Authorized access to dashboard features
- Session-based authentication

---

## 4. Dashboard Metrics

The dashboard displays:

- Total uploads
- Activity-wise image counts
- Upload trends
- Classification statistics
- Confidence information

---

## 5. Upload Workflow

1. Upload image
2. Image preprocessing
3. AI classification
4. Prediction display
5. Save record to SQLite database
6. Update dashboard statistics

---

## 6. Classification Output

Each prediction displays:

- Predicted class
- Confidence score
- Uploaded image
- Timestamp

---

## 7. Image Library

The Image Library allows administrators to:

- Browse uploaded images
- Search images
- Review prediction history
- View prediction details

---

## 8. Date Filtering

Users can filter uploaded records by date to review specific operational activities.

---

## 9. Class Reassignment

Administrators can update incorrect predictions to improve record accuracy.

---

## 10. ZIP Download

The dashboard supports downloading records and reports as ZIP archives.

---

## 11. SQLite Database Schema

Each record stores:

- Uploaded Image
- Predicted Class
- Final/Reassigned Class
- Confidence Score
- Timestamp

---

## 12. Image Naming Convention

Uploaded images retain unique filenames to prevent conflicts and ensure traceability.

---

## 13. Error Handling

The application handles:

- Invalid image uploads
- Unsupported file formats
- Prediction failures
- Database exceptions

---

## 14. Empty-State Behaviour

When no uploads exist, the dashboard displays an informative empty-state message instead of attempting to render empty charts.

---

## 15. Deployment Limitations

The application uses SQLite for local storage. When deployed on Streamlit Community Cloud, uploaded records may not persist after application restarts because the cloud filesystem is temporary.