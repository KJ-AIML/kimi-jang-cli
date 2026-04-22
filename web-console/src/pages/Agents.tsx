import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Play, Pause, Settings } from 'lucide-react'
import { useState } from 'react'

interface Agent {
  id: string
  name: string
  role: 'coder' | 'reviewer'
  model: string
  status: 'idle' | 'working'
  cost_today: number
  cost_total: number
  yolo_mode: boolean
  max_cost_per_task: number
}

function Agents() {
  const queryClient = useQueryClient()
  const [showNewAgent, setShowNewAgent] = useState(false)
  const [newAgent, setNewAgent] = useState<{ name: string; role: 'coder' | 'reviewer' }>({ name: '', role: 'coder' })

  const { data: agents, isLoading } = useQuery<Agent[]>({
    queryKey: ['agents'],
    queryFn: async () => {
      const res = await fetch('/api/agents')
      if (!res.ok) throw new Error('Failed to fetch agents')
      return res.json()
    },
  })

  const createAgent = useMutation({
    mutationFn: async (agent: { name: string; role: 'coder' | 'reviewer' }) => {
      const res = await fetch('/api/agents', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(agent),
      })
      if (!res.ok) throw new Error('Failed to create agent')
      return res.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agents'] })
      setShowNewAgent(false)
      setNewAgent({ name: '', role: 'coder' })
    },
  })

  const updateStatus = useMutation({
    mutationFn: async ({ agentId, status }: { agentId: string; status: string }) => {
      const res = await fetch(`/api/agents/${agentId}/status`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status }),
      })
      if (!res.ok) throw new Error('Failed to update agent')
      return res.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agents'] })
    },
  })

  if (isLoading) {
    return (
      <div className="p-8">
        <div className="animate-pulse">
          <div className="h-8 bg-[var(--bg-tertiary)] rounded w-48 mb-8"></div>
          <div className="grid grid-cols-3 gap-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-48 bg-[var(--bg-tertiary)] rounded"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-2xl font-bold">Agents</h1>
        <button
          onClick={() => setShowNewAgent(true)}
          className="btn-primary flex items-center gap-2"
        >
          <Plus size={16} />
          New Agent
        </button>
      </div>

      {showNewAgent && (
        <div className="card mb-6">
          <div className="grid grid-cols-2 gap-4 mb-4">
            <input
              type="text"
              placeholder="Agent name..."
              value={newAgent.name}
              onChange={(e) => setNewAgent({ ...newAgent, name: e.target.value })}
              className="bg-[var(--bg-tertiary)] border border-[var(--border)] rounded-lg px-4 py-2"
            />
            <select
              value={newAgent.role}
              onChange={(e) => setNewAgent({ ...newAgent, role: e.target.value as 'coder' | 'reviewer' })}
              className="bg-[var(--bg-tertiary)] border border-[var(--border)] rounded-lg px-4 py-2"
            >
              <option value="coder">Code Writer</option>
              <option value="reviewer">Code Reviewer</option>
            </select>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => newAgent.name && createAgent.mutate(newAgent)}
              disabled={!newAgent.name || createAgent.isPending}
              className="btn-primary"
            >
              Create Agent
            </button>
            <button
              onClick={() => setShowNewAgent(false)}
              className="btn-secondary"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      <div className="grid grid-cols-3 gap-4">
        {agents?.map((agent) => (
          <div key={agent.id} className="card">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className={`w-3 h-3 rounded-full ${agent.status === 'working' ? 'bg-green-500' : 'bg-gray-500'}`} />
                <div>
                  <h3 className="font-semibold">{agent.name}</h3>
                  <p className="text-xs text-[var(--text-secondary)] capitalize">{agent.role}</p>
                </div>
              </div>
              <button className="text-[var(--text-secondary)] hover:text-white">
                <Settings size={16} />
              </button>
            </div>

            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-[var(--text-secondary)]">Model</span>
                <span>{agent.model}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[var(--text-secondary)]">Today</span>
                <span className="text-violet-400">${agent.cost_today.toFixed(2)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[var(--text-secondary)]">Total</span>
                <span>${agent.cost_total.toFixed(2)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[var(--text-secondary)]">Max/task</span>
                <span>${agent.max_cost_per_task.toFixed(2)}</span>
              </div>
              {agent.yolo_mode && (
                <div className="text-yellow-500 text-xs">⚡ YOLO Mode</div>
              )}
            </div>

            <div className="mt-4 pt-4 border-t border-[var(--border)]">
              <button
                onClick={() => updateStatus.mutate({ agentId: agent.id, status: agent.status === 'working' ? 'idle' : 'working' })}
                disabled={updateStatus.isPending}
                className={`w-full flex items-center justify-center gap-2 py-2 rounded-lg transition-colors ${
                  agent.status === 'working'
                    ? 'bg-yellow-500/20 text-yellow-500 hover:bg-yellow-500/30'
                    : 'bg-green-500/20 text-green-500 hover:bg-green-500/30'
                }`}
              >
                {agent.status === 'working' ? (
                  <>
                    <Pause size={16} /> Pause
                  </>
                ) : (
                  <>
                    <Play size={16} /> Start
                  </>
                )}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default Agents
