import { initializeApp } from 'firebase/app'
import { getDatabase, connectDatabaseEmulator } from 'firebase/database'

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  databaseURL: import.meta.env.VITE_FIREBASE_DATABASE_URL,
}

const app = initializeApp(firebaseConfig)
export const db = getDatabase(app)

if (import.meta.env.VITE_USE_FIREBASE_EMULATOR === 'true') {
  try {
    connectDatabaseEmulator(db as any, '127.0.0.1', 9000)
  } catch {}
}