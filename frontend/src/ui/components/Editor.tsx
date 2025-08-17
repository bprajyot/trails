import React from 'react'
import Editor from '@monaco-editor/react'

const CodeEditor: React.FC<{ language: string; value: string; onChange: (v: string)=>void }> = ({ language, value, onChange }) => {
  return (
    <Editor height="500px" language={language} value={value} onChange={(v) => onChange(v || '')} theme="vs-dark" options={{ fontSize: 14 }} />
  )
}

export default CodeEditor