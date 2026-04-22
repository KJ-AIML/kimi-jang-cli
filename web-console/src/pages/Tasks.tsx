import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, MoreHorizontal, GitBranch, User } from 'lucide-react'

interface Task {
  id: string
  title: string
  description?: string
  status: 'todo' | 'doing' | 'review' | 'done'
  assignee_id?: string
  branch?: string
  estimated_cost?: number
  actual_cost: number
  created_at: string
}

interface Agent {
  id: string
  name: string
}

const columns = [
  { id: 'todo', label: 'Todo' },
  { id: 'doing', label: 'Doing' },
  { id: 'review', label: 'Review' },
  { id: 'done', label: 'Done' },
]

function Tasks() {
  const queryClient = useQueryClient()
  const [showNewTask, setShowNewTask] = useState(false)
  const [newTaskTitle, setNewTaskTitle] = useState('')

  const { data: tasks, isLoading } = useQuery<Task[]>({
    queryKey: ['tasks'],
    queryFn: async () => {
      const res = await fetch('/api/tasks')
      if (!res.ok) throw new Error('Failed to fetch tasks')
      return res.json()
    },
  })

  const { data: agents } = useQuery<Agent[]>({
    queryKey: ['agents'],
    queryFn: async () => {
      const res = await fetch('/api/agents')
      if (!res.ok) throw new Error('Failed to fetch agents')
      return res.json()
    },
  })

  const createTask = useMutation({
    mutationFn: async (title: string) => {
      const res = await fetch('/api/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title }),
      })
      if (!res.ok) throw new Error('Failed to create task')
      return res.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
      setShowNewTask(false)
      setNewTaskTitle('')
    },
  })

  const updateTaskStatus = useMutation({
    mutationFn: async ({ taskId, status }: { taskId: string; status: string }) => {
      const res = await fetch(`/api/tasks/${taskId}/status`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status }),
      })
      if (!res.ok) throw new Error('Failed to update task')
      return res.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
    },
  })

  if (isLoading) {
    return (
      <div className="p-8">
        <div className="animate-pulse">
          <div className="h-8 bg-[var(--bg-tertiary)] rounded w-48 mb-8"></div>
          <div className="grid grid-cols-4 gap-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-64 bg-[var(--bg-tertiary)] rounded"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  const tasksByColumn = columns.reduce((acc, col) => {
    acc[col.id] = tasks?.filter((t) => t.status === col.id) ?? []
    return acc
  }, {} as Record<string, Task[]>)

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-2xl font-bold">Tasks</h1>
        <button 
          onClick={() => setShowNewTask(true)}
          className="btn-primary flex items-center gap-2"
        >
          <Plus size={16} />
          New Task
        </button>
      </div>

      {showNewTask && (
        <div className="card mb-6">
          <input
            type="text"
            placeholder="Enter task title..."
            value={newTaskTitle}
            onChange={(e) => setNewTaskTitle(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && newTaskTitle) {
                createTask.mutate(newTaskTitle)
              }
              if (e.key === 'Escape') {
                setShowNewTask(false)
              }
            }}
            className="w-full bg-[var(--bg-tertiary)] border border-[var(--border)] rounded-lg px-4 py-2 mb-3"
          />
          <div className="flex gap-2">
            <button
              onClick={() => newTaskTitle && createTask.mutate(newTaskTitle)}
              disabled={!newTaskTitle || createTask.isPending}
              className="btn-primary"
            >
              Create Task
            </button>
            <button
              onClick={() => setShowNewTask(false)}
              className="btn-secondary"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      <div className="grid grid-cols-4 gap-4">
        {columns.map((col) => (
          <div key={col.id} className="bg-[var(--bg-secondary)] rounded-lg p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold">{col.label}</h3>
              <span className="text-sm text-[var(--text-secondary)]">
                {tasksByColumn[col.id]?.length ?? 0}
              </span>
            </div>
            
            <div className="space-y-2 min-h-[200px]">
              {tasksByColumn[col.id]?.map((task) => (
                <div 
                  key={task.id}
                  className="bg-[var(--bg-tertiary)] rounded-lg p-3 group cursor-pointer hover:border-violet-500 border border-transparent transition-all"
                >
                  <div className="flex items-start justify-between">
                    <h4 className="font-medium text-sm mb-2">{task.title}</h4>
                    <button 
                      onClick={() => {
                        const nextStatus = { todo: 'doing', doing: 'review', review: 'done', done: 'todo' }[task.status]
                        updateTaskStatus.mutate({ taskId: task.id, status: nextStatus })
                      }}
                      className="text-[var(--text-secondary)] hover:text-violet-400"
                    >
                      <MoreHorizontal size={14} />
                    </button>
                  </div>
                  
                  {task.branch && (
                    <div className="flex items-center gap-1 text-xs text-violet-400 mb-2">
                      <GitBranch size={12} />
                      {task.branch}
                    </div>
                  )}
                  
                  <div className="flex items-center justify-between text-xs text-[var(--text-secondary)]">
                    <div className="flex items-center gap-1">
                      <User size={12} />
                      {agents?.find(a => a.id === task.assignee_id)?.name ?? 'Unassigned'}
                    </div>
                    <span className="text-violet-400">
                      ${task.actual_cost.toFixed(2)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default Tasks
