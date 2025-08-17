import React, { useEffect, useState } from 'react'
import { useAuth } from '../state/AuthContext'

const SubmissionsPage: React.FC = () => {
  // For brevity, just a placeholder
  return (
    <div>
      <h1 className="text-2xl font-semibold mb-4">Your Submissions</h1>
      <div className="text-gray-600">Submit a solution from a challenge page to see live results here.</div>
    </div>
  )
}

export default SubmissionsPage