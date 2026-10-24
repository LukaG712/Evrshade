'use client'

import { useEffect, useState } from 'react'
import { CheckCircle, XCircle, Loader } from 'lucide-react'
import { REPO_URL } from '@/lib/evershade'

interface WorkflowRun {
  id: number
  status: string
  conclusion: string | null
  html_url: string
  head_commit: { message: string }
}

export function BuildStatus() {
  const [run, setRun] = useState<WorkflowRun | null>(null)

  useEffect(() => {
    fetch('https://api.github.com/repos/LukaG712/Evershade/actions/runs?per_page=1')
      .then((res) => {
        if (!res.ok) return null
        return res.json()
      })
      .then((data: { workflow_runs: WorkflowRun[] } | null) => {
        if (data?.workflow_runs?.[0]) setRun(data.workflow_runs[0])
      })
      .catch(() => {})
  }, [])

  if (!run) return null

  const isPassing = run.conclusion === 'success'
  const isRunning = run.status === 'in_progress'

  return (
    <a
      href={run.html_url}
      target="_blank"
      rel="noreferrer"
      className="inline-flex items-center gap-1.5 rounded-full border border-border px-2.5 py-1 font-mono text-[11px] transition-colors hover:border-signal"
      title={run.head_commit.message}
    >
      {isRunning ? (
        <Loader className="size-3 animate-spin text-muted-foreground" />
      ) : isPassing ? (
        <CheckCircle className="size-3 text-signal" />
      ) : (
        <XCircle className="size-3 text-destructive" />
      )}
      <span className={isPassing ? 'text-signal-ink' : isRunning ? 'text-muted-foreground' : 'text-destructive'}>
        {isRunning ? 'Building' : isPassing ? 'Passing' : 'Failing'}
      </span>
    </a>
  )
}
