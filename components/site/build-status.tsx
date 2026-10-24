'use client'

import { CheckCircle, XCircle, Loader, GitBranch } from 'lucide-react'
import { useEffect, useState } from 'react'

type Status = 'success' | 'failure' | 'in_progress' | 'unknown'

interface BuildStatus {
  status: Status
  commitMessage: string
  commitSha: string
  workflowName: string
  updatedAt: string
}

const REPO_OWNER = 'LukaG712'
const REPO_NAME = 'Evershade'

export function BuildStatus() {
  const [build, setBuild] = useState<BuildStatus | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/actions/runs?per_page=1`)
      .then(res => res.json())
      .then(data => {
        if (data.workflow_runs && data.workflow_runs.length > 0) {
          const run = data.workflow_runs[0]
          let status: Status = 'unknown'
          if (run.conclusion === 'success') status = 'success'
          else if (run.conclusion === 'failure') status = 'failure'
          else if (run.status === 'in_progress' || run.status === 'queued') status = 'in_progress'

          setBuild({
            status,
            commitMessage: run.head_commit.message.split('\n')[0],
            commitSha: run.head_commit.id.slice(0, 7),
            workflowName: run.name,
            updatedAt: new Date(run.updated_at).toLocaleDateString('en-US', {
              month: 'short',
              day: 'numeric',
            }),
          })
        }
      })
      .catch(() => {
        // Silently fail — badge will remain hidden
      })
      .finally(() => setLoading(false))
  }, [])

  if (loading || build === null) return null

  const statusIcon = {
    success: <CheckCircle className="size-3.5 text-signal" aria-hidden="true" />,
    failure: <XCircle className="size-3.5 text-destructive" aria-hidden="true" />,
    in_progress: <Loader className="size-3.5 text-foreground/40 animate-spin" aria-hidden="true" />,
    unknown: <GitBranch className="size-3.5 text-muted-foreground" aria-hidden="true" />,
  }[build.status]

  const statusLabel = {
    success: 'Passing',
    failure: 'Failing',
    in_progress: 'Building',
    unknown: 'Unknown',
  }[build.status]

  return (
    <a
      href={`https://github.com/${REPO_OWNER}/${REPO_NAME}/actions/runs/${build.commitSha}`}
      target="_blank"
      rel="noreferrer"
      className="inline-flex items-center gap-2 rounded-sm border border-border px-2.5 py-1 text-xs text-muted-foreground transition-colors hover:border-foreground/20 hover:text-foreground"
      title={`${build.commitMessage} (${build.commitSha})`}
    >
      {statusIcon}
      <span>{statusLabel}</span>
      <span className="text-[10px] text-muted-foreground/60">{build.updatedAt}</span>
    </a>
  )
}
