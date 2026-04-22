import { useQuery } from '@tanstack/react-query'
import { Activity, DollarSign, CheckCircle, Zap, Plus } from 'lucide-react'
import { Link } from 'react-router-dom'

interface DashboardData {
  sessions_today: number
  tasks_done_today: number
  total_cost: number
  active_agents: Agent[]
  recent_activities: Activity[]
}

interface Agent {
  id: string
  name: string
  status: 'idle' | 'working'
  current_task_id?: string
  cost_today: number
}

interface Activity {
  id: number
  type: string
  message: string
  created_at: string
}

function Dashboard() {
  const { data, isLoading } = useQuery<DashboardData>({
    queryKey: ['dashboard'],
    queryFn: async () => {
      const res = await fetch('/api/dashboard')
      if (!res.ok) throw new Error('Failed to fetch dashboard')
      return res.json()
    },
    refetchInterval: 5000,
  })

  if (isLoading) {
    return (
      <div className="p-8">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-[var(--bg-tertiary)] rounded w-48"></div>
          <div className="grid grid-cols-3 gap-4">
            <div className="h-32 bg-[var(--bg-tertiary)] rounded"></div>
            <div className="h-32 bg-[var(--bg-tertiary)] rounded"></div>
            <div className="h-32 bg-[var(--bg-tertiary)] rounded"></div>
          </div>
        </div>
      </div>
    )
  }

  const stats = [
    { label: 'Sessions Today', value: data?.sessions_today ?? 0, icon: Activity },
    { label: 'Tasks Done', value: data?.tasks_done_today ?? 0, icon: CheckCircle },
    { label: 'Total Cost', value: `$${(data?.total_cost ?? 0).toFixed(2)}`, icon: DollarSign },
  ]

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <div className="flex gap-2">
          <Link to="/tasks" className="btn-primary flex items-center gap-2">
            <Plus size={16} />
            New Task
          </Link>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        {stats.map((stat) => {
          const Icon = stat.icon
          return (
            <div key={stat.label} className="card">
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 bg-violet-500/20 rounded-lg">
                  <Icon size={20} className="text-violet-400" />
                </div>
                <span className="text-[var(--text-secondary)]">{stat.label}</span>
              </div>
              <div className="text-3xl font-bold">{stat.value}</div>
            </div>
          )
        })}
      </div>

      {/* Active Agents */}
      <div className="card mb-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <Zap size={18} className="text-violet-400" />
            Active Agents
          </h2>
          <Link to="/agents" className="text-sm text-violet-400 hover:text-violet-300">
            View all →
          </Link>
        </div>
        
        {data?.active_agents?.length ? (
          <div className="space-y-2">
            {data.active_agents.map((agent) => (
              <div 
                key={agent.id} 
                className="flex items-center justify-between p-3 bg-[var(--bg-tertiary)] rounded-lg"
              >
                <div className="flex items-center gap-3">
                  <div className={`status-dot ${agent.status === 'working' ? 'status-working' : 'status-idle'}`} />
                  <div>
                    <div className="font-medium">{agent.name}</div>
                    <div className="text-sm text-[var(--text-secondary)]">
                      {agent.status === 'working' ? `Task: ${agent.current_task_id}` : 'Idle'}
                    </div>
                  </div>
                </div>
                <div className="text-violet-400">${agent.cost_today.toFixed(2)}</div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-[var(--text-secondary)] text-center py-8">
            No active agents
          </div>
        )}
      </div>

      {/* Recent Activity */}
      <div className="card">
        <h2 className="text-lg font-semibold mb-4">Recent Activity</h2>
        <div className="space-y-2">
          {data?.recent_activities?.slice(0, 5).map((activity) => (
            <div key={activity.id} className="flex items-center gap-3 text-sm">
              <span className="text-[var(--text-secondary)] text-xs">
                {new Date(activity.created_at).toLocaleTimeString()}
              </span>
              <span>{activity.message}</span>
            </div>
          )) ?? (
            <div className="text-[var(--text-secondary)] text-center py-4">
              No recent activity
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Dashboard
