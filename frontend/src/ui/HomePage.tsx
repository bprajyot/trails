import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../state/AuthContext'

type Challenge = { id: number; slug: string; title: string; difficulty: 'easy'|'medium'|'hard' }

const HomePage: React.FC = () => {
  const { api } = useAuth()
  const [items, setItems] = useState<Challenge[]>([])

  useEffect(() => {
    api.get('/challenges').then(r => setItems(r.data))
  }, [api])

  return (
    <div>
      <h1 className="text-2xl font-semibold mb-4">Challenges</h1>
      <div className="grid gap-3">
        {items.map(c => (
          <Link key={c.id} to={`/challenge/${c.slug}`} className="p-4 bg-white border rounded hover:shadow">
            <div className="font-medium">{c.title}</div>
            <div className="text-sm text-gray-600 capitalize">{c.difficulty}</div>
          </Link>
        ))}
      </div>
    </div>
  )
}

export default HomePage