import React, { useEffect, useMemo, useRef, useState } from 'react'
import { useParams } from 'react-router-dom'
import Editor from '@monaco-editor/react'
import { useAuth } from '../state/AuthContext'
import { onValue, ref } from 'firebase/database'
import { db } from '../firebase'

const languageToMonaco = (lang: string) => lang === 'node' ? 'javascript' : lang

const ChallengePage: React.FC = () => {
  const { slug } = useParams()
  const { api, user } = useAuth()
  const [challenge, setChallenge] = useState<any>(null)
  const [language, setLanguage] = useState<'python'|'node'|'cpp'>('python')
  const [code, setCode] = useState<string>('')
  const [submissionId, setSubmissionId] = useState<number | null>(null)
  const [results, setResults] = useState<any | null>(null)

  useEffect(() => {
    api.get(`/challenges/${slug}`).then(r => {
      setChallenge(r.data.challenge)
      const starter = r.data.challenge.starter_code || {}
      setCode(starter['python'] || '')
    })
  }, [api, slug])

  useEffect(() => {
    if (!submissionId) return
    const submissionRef = ref(db, `/submissions/${submissionId}`)
    const off = onValue(submissionRef, (snap) => setResults(snap.val()))
    return () => off()
  }, [submissionId])

  function changeLanguage(next: 'python'|'node'|'cpp') {
    setLanguage(next)
    const starter = challenge?.starter_code || {}
    setCode(starter[next] || code)
  }

  async function submit() {
    if (!user) return alert('Login required')
    const res = await api.post('/submissions', {
      challengeSlug: slug,
      language,
      code,
    })
    setSubmissionId(res.data.submissionId)
    setResults({ status: 'queued' })
  }

  return (
    <div>
      {!challenge ? (
        <div>Loading...</div>
      ) : (
        <div className="grid gap-4">
          <div className="bg-white border rounded p-4">
            <div className="flex justify-between items-center">
              <div>
                <h1 className="text-xl font-semibold">{challenge.title}</h1>
                <div className="text-sm text-gray-600 capitalize">{challenge.difficulty}</div>
              </div>
              <div className="flex items-center gap-2">
                <select value={language} onChange={e => changeLanguage(e.target.value as any)} className="border rounded p-1">
                  <option value="python">Python</option>
                  <option value="node">Node.js</option>
                  <option value="cpp">C++</option>
                </select>
                <button className="bg-green-600 text-white px-3 py-1 rounded" onClick={submit}>Submit</button>
              </div>
            </div>
            <p className="mt-3 whitespace-pre-wrap text-gray-800">{challenge.description}</p>
          </div>
          <div className="grid md:grid-cols-2 gap-4">
            <div className="bg-white border rounded">
              <Editor height="500px" language={languageToMonaco(language)} value={code} onChange={(v) => setCode(v || '')} theme="vs-dark" options={{ fontSize: 14 }} />
            </div>
            <div className="bg-white border rounded p-4">
              <h2 className="font-semibold mb-2">Results</h2>
              {!results ? (
                <div className="text-gray-500">No submission yet.</div>
              ) : (
                <div className="text-sm">
                  <div>Status: <span className="font-medium">{results.status}</span></div>
                  {Array.isArray(results.results) && (
                    <div className="mt-2 grid gap-2">
                      {results.results.map((r: any) => (
                        <div key={r.testCaseId} className={`p-2 border rounded ${r.passed ? 'border-green-500' : 'border-red-500'}`}>
                          <div>Test #{r.testCaseId}: {r.passed ? 'Passed' : 'Failed'}</div>
                          <div>Runtime: {r.runtimeMs} ms</div>
                          {!r.passed && (<pre className="bg-gray-50 p-2 mt-1 overflow-x-auto whitespace-pre-wrap">{r.output}</pre>)}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ChallengePage