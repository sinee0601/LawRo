# Firebase Setup Guide for LawRo Backend

This guide will walk you through setting up Firebase for the LawRo Unified Backend.

## Prerequisites

- Google Account
- Access to [Firebase Console](https://console.firebase.google.com/)

---

## Step 1: Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click **"Add project"** or **"Create a project"**
3. Enter project name: `lawro` (or your preferred name)
4. Enable/Disable Google Analytics (optional)
5. Click **"Create project"**

---

## Step 2: Enable Firebase Authentication

1. In Firebase Console, select your project
2. Click **"Authentication"** in the left sidebar
3. Click **"Get started"**
4. Enable sign-in methods:

### Email/Password Authentication
1. Click **"Email/Password"**
2. Enable **"Email/Password"**
3. Click **"Save"**

### Google Authentication
1. Click **"Google"**
2. Enable the provider
3. Enter your **Project support email**
4. Click **"Save"**
5. Note: You'll need to configure OAuth consent screen in Google Cloud Console

### Kakao Authentication (Custom Provider)
1. Go to [Kakao Developers](https://developers.kakao.com/)
2. Create an application
3. Get your **REST API Key** and **Client Secret**
4. In Firebase, you'll use custom authentication with Kakao tokens

### Naver Authentication (Custom Provider)
1. Go to [Naver Developers](https://developers.naver.com/apps/)
2. Create an application
3. Get your **Client ID** and **Client Secret**
4. In Firebase, you'll use custom authentication with Naver tokens

---

## Step 3: Create Firestore Database

1. In Firebase Console, click **"Firestore Database"**
2. Click **"Create database"**
3. Choose **"Start in production mode"** (we'll configure rules later)
4. Select location: **asia-northeast3 (Seoul)** or closest to your users
5. Click **"Enable"**

### Configure Firestore Security Rules

1. In Firestore, go to **"Rules"** tab
2. Replace with the following rules:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {

    // Helper function to check if user is authenticated
    function isAuthenticated() {
      return request.auth != null;
    }

    // Helper function to check if user owns the document
    function isOwner(userId) {
      return request.auth.uid == userId;
    }

    // Users collection
    match /users/{userId} {
      // Users can read/write their own profile
      allow read, write: if isAuthenticated() && isOwner(userId);
    }

    // Chat sessions collection
    match /chat_sessions/{sessionId} {
      // Users can manage their own chat sessions
      allow read, write: if isAuthenticated() && resource.data.user_id == request.auth.uid;
      allow create: if isAuthenticated();
    }

    // Chat messages collection
    match /chat_messages/{messageId} {
      // Users can manage their own chat messages
      allow read, write: if isAuthenticated() && resource.data.user_id == request.auth.uid;
      allow create: if isAuthenticated();
    }

    // Contract sessions collection
    match /contract_sessions/{contractId} {
      // Users can manage their own contract sessions
      allow read, write: if isAuthenticated() && resource.data.user_id == request.auth.uid;
      allow create: if isAuthenticated();
    }

    // Contract analysis collection
    match /contract_analysis/{analysisId} {
      // Users can manage their own contract analysis
      allow read, write: if isAuthenticated() && resource.data.user_id == request.auth.uid;
      allow create: if isAuthenticated();
    }
  }
}
```

3. Click **"Publish"**

---

## Step 4: Get Firebase Admin SDK Credentials

1. In Firebase Console, click the **gear icon** ⚙️ next to "Project Overview"
2. Click **"Project settings"**
3. Go to **"Service accounts"** tab
4. Click **"Generate new private key"**
5. Click **"Generate key"**
6. A JSON file will be downloaded - **KEEP THIS SECURE!**

### Save the credentials file:
1. Rename the downloaded file to `firebase-credentials.json`
2. Move it to your `backend/` directory:
   ```
   backend/
   ├── firebase-credentials.json  ← Place here
   ├── app/
   ├── .env
   └── ...
   ```

⚠️ **IMPORTANT**: Add `firebase-credentials.json` to your `.gitignore` to prevent committing sensitive data!

---

## Step 5: Get Firebase Web API Key

1. In Firebase Console, go to **"Project settings"** (gear icon)
2. Under **"General"** tab, scroll to **"Your apps"**
3. If you don't have a web app yet:
   - Click **"Add app"** and select the **web icon** (</>)
   - Register the app with a nickname (e.g., "LawRo Web")
   - You don't need to set up Firebase Hosting
4. Copy the **Web API Key** from the Firebase SDK configuration

It will look like this:
```javascript
const firebaseConfig = {
  apiKey: "AIza...your-api-key",  // ← This is your FIREBASE_API_KEY
  authDomain: "your-project.firebaseapp.com",
  projectId: "your-project-id",
  // ... other config
};
```

---

## Step 6: Configure Environment Variables

Edit your `backend/.env` file and fill in the Firebase configuration:

```bash
# Firebase Configuration
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
FIREBASE_PROJECT_ID=your-project-id           # From Firebase Console
FIREBASE_API_KEY=AIza...your-api-key          # From Firebase Web SDK config
```

### Finding your Project ID:
- In Firebase Console, click the gear icon → Project settings
- Under "General" tab, you'll see **"Project ID"**

---

## Step 7: Configure OAuth Providers (Optional)

### For Google OAuth:
Your Google OAuth is already configured through Firebase Authentication. No additional setup needed!

### For Kakao OAuth:
1. Get credentials from [Kakao Developers Console](https://developers.kakao.com/)
2. Add to `.env`:
   ```bash
   KAKAO_CLIENT_ID=your-kakao-rest-api-key
   KAKAO_CLIENT_SECRET=your-kakao-client-secret
   ```

### For Naver OAuth:
1. Get credentials from [Naver Developers](https://developers.naver.com/apps/)
2. Add to `.env`:
   ```bash
   NAVER_CLIENT_ID=your-naver-client-id
   NAVER_CLIENT_SECRET=your-naver-client-secret
   ```

---

## Step 8: Test Firebase Connection

1. Make sure your `.env` file is configured
2. Ensure `firebase-credentials.json` is in the `backend/` directory
3. Start the backend:

```bash
cd backend
python -m uvicorn app.main:app --reload
```

4. Check health endpoint:
```bash
curl http://localhost:8000/health
```

You should see:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "firebase": "healthy"
  }
}
```

---

## Step 9: Frontend Configuration (Next Step)

For the frontend to work with Firebase Authentication, you'll need to configure the Firebase SDK in your React app:

1. Install Firebase SDK in frontend:
```bash
cd frontend
npm install firebase
```

2. Create `frontend/src/config/firebase.js`:
```javascript
import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';

const firebaseConfig = {
  apiKey: "your-api-key",
  authDomain: "your-project.firebaseapp.com",
  projectId: "your-project-id",
  storageBucket: "your-project.appspot.com",
  messagingSenderId: "123456789",
  appId: "your-app-id"
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
```

3. Update authentication logic to use Firebase Auth instead of custom JWT

---

## Security Checklist

- [ ] `firebase-credentials.json` is in `.gitignore`
- [ ] Firestore security rules are configured
- [ ] Firebase API key is added to `.env`
- [ ] OAuth redirect URIs are configured (if using OAuth)
- [ ] Production: Enable App Check for additional security
- [ ] Production: Set up Firebase billing alerts

---

## Firestore Collections Structure

The backend will create these collections automatically:

```
firestore/
├── users/
│   └── {uid}/
│       ├── uid: string
│       ├── email: string
│       ├── full_name: string
│       ├── email_verified: boolean
│       ├── provider: string
│       ├── picture: string
│       ├── created_at: timestamp
│       └── updated_at: timestamp
│
├── chat_sessions/
│   └── {session_id}/
│       ├── session_id: string
│       ├── user_id: string
│       ├── created_at: timestamp
│       └── updated_at: timestamp
│
├── chat_messages/
│   └── {message_id}/
│       ├── session_id: string
│       ├── user_id: string
│       ├── role: string (user/assistant)
│       ├── content: string
│       └── timestamp: timestamp
│
├── contract_sessions/
│   └── {contract_id}/
│       ├── contract_id: string
│       ├── user_id: string
│       ├── language: string
│       ├── original_data: object
│       ├── corrected_data: object
│       ├── analysis_result: object
│       ├── created_at: timestamp
│       └── updated_at: timestamp
│
└── contract_analysis/
    └── {analysis_id}/
        ├── user_id: string
        ├── contract_id: string
        ├── analysis_result: object
        ├── language: string
        ├── created_at: timestamp
        └── updated_at: timestamp
```

---

## Troubleshooting

### Error: "Firebase not initialized"
- Check if `firebase-credentials.json` exists in the correct location
- Verify the file path in `.env` matches the actual file location
- Check file permissions (should be readable)

### Error: "Invalid Firebase credentials"
- Re-download the service account key from Firebase Console
- Ensure the JSON file is valid (not corrupted)
- Check that the project ID matches your Firebase project

### Error: "Permission denied" when accessing Firestore
- Check Firestore security rules
- Ensure user is authenticated (valid Firebase ID token)
- Verify the user ID in the request matches the document owner

### OAuth redirect issues
- Verify redirect URIs are configured in OAuth provider console
- Check that `FRONTEND_URL` in `.env` matches your actual frontend URL
- For production, use HTTPS

---

## Next Steps

After completing Firebase setup:

1. **Phase 1 Complete**: You now have authentication working
2. **Phase 2**: Integrate Chatbot Service (RAG + LangChain)
3. **Phase 3**: Integrate Contract Parser (OCR + GPT-4)

---

## Resources

- [Firebase Console](https://console.firebase.google.com/)
- [Firebase Auth Documentation](https://firebase.google.com/docs/auth)
- [Firestore Documentation](https://firebase.google.com/docs/firestore)
- [Firebase Admin SDK for Python](https://firebase.google.com/docs/admin/setup)
