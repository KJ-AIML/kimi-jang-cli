import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { FileText, Plus, Save } from 'lucide-react'
import { useState } from 'react'

interface Note {
  id: string
  title: string
  content: string
  type: 'session-summary' | 'decision' | 'doc'
  updated_at: string
}

function Knowledge() {
  const queryClient = useQueryClient()
  const [selectedNote, setSelectedNote] = useState<Note | null>(null)
  const [showNewNote, setShowNewNote] = useState(false)
  const [newNoteTitle, setNewNoteTitle] = useState('')
  const [editContent, setEditContent] = useState('')

  const { data: notes, isLoading } = useQuery<Note[]>({
    queryKey: ['notes'],
    queryFn: async () => {
      const res = await fetch('/api/notes')
      if (!res.ok) throw new Error('Failed to fetch notes')
      return res.json()
    },
  })

  const createNote = useMutation({
    mutationFn: async (title: string) => {
      const res = await fetch('/api/notes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, content: '', type: 'doc' }),
      })
      if (!res.ok) throw new Error('Failed to create note')
      return res.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notes'] })
      setShowNewNote(false)
      setNewNoteTitle('')
    },
  })

  const updateNote = useMutation({
    mutationFn: async ({ id, content }: { id: string; content: string }) => {
      const res = await fetch(`/api/notes/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content }),
      })
      if (!res.ok) throw new Error('Failed to update note')
      return res.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notes'] })
    },
  })

  const handleSelectNote = (note: Note) => {
    setSelectedNote(note)
    setEditContent(note.content)
  }

  const handleSave = () => {
    if (selectedNote && editContent !== selectedNote.content) {
      updateNote.mutate({ id: selectedNote.id, content: editContent })
    }
  }

  if (isLoading) {
    return (
      <div className="p-8">
        <div className="animate-pulse">
          <div className="h-8 bg-[var(--bg-tertiary)] rounded w-48 mb-8"></div>
          <div className="flex gap-4">
            <div className="w-64 h-96 bg-[var(--bg-tertiary)] rounded"></div>
            <div className="flex-1 h-96 bg-[var(--bg-tertiary)] rounded"></div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="p-8 h-full flex flex-col">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-2xl font-bold">Knowledge Base</h1>
        <button
          onClick={() => setShowNewNote(true)}
          className="btn-primary flex items-center gap-2"
        >
          <Plus size={16} />
          New Note
        </button>
      </div>

      {showNewNote && (
        <div className="card mb-6">
          <input
            type="text"
            placeholder="Note title..."
            value={newNoteTitle}
            onChange={(e) => setNewNoteTitle(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && newNoteTitle) {
                createNote.mutate(newNoteTitle)
              }
            }}
            className="w-full bg-[var(--bg-tertiary)] border border-[var(--border)] rounded-lg px-4 py-2 mb-3"
          />
          <div className="flex gap-2">
            <button
              onClick={() => newNoteTitle && createNote.mutate(newNoteTitle)}
              disabled={!newNoteTitle || createNote.isPending}
              className="btn-primary"
            >
              Create
            </button>
            <button
              onClick={() => setShowNewNote(false)}
              className="btn-secondary"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      <div className="flex gap-4 flex-1 min-h-0">
        {/* Sidebar */}
        <div className="w-64 bg-[var(--bg-secondary)] rounded-lg p-4 overflow-auto">
          <div className="space-y-1">
            {notes?.map((note) => (
              <button
                key={note.id}
                onClick={() => handleSelectNote(note)}
                className={`w-full text-left px-3 py-2 rounded-lg transition-colors ${
                  selectedNote?.id === note.id
                    ? 'bg-violet-500/20 text-violet-400'
                    : 'text-[var(--text-secondary)] hover:bg-[var(--bg-tertiary)]'
                }`}
              >
                <div className="flex items-center gap-2">
                  <FileText size={14} />
                  <span className="truncate">{note.title}</span>
                </div>
                <div className="text-xs text-[var(--text-secondary)] mt-1">
                  {new Date(note.updated_at).toLocaleDateString()}
                </div>
              </button>
            )) ?? (
              <div className="text-[var(--text-secondary)] text-center py-8">
                No notes yet
              </div>
            )}
          </div>
        </div>

        {/* Editor */}
        <div className="flex-1 bg-[var(--bg-secondary)] rounded-lg p-4 flex flex-col">
          {selectedNote ? (
            <>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold">{selectedNote.title}</h2>
                <div className="flex gap-2">
                  <button
                    onClick={handleSave}
                    disabled={updateNote.isPending || editContent === selectedNote.content}
                    className="btn-primary flex items-center gap-2"
                  >
                    <Save size={16} />
                    Save
                  </button>
                </div>
              </div>
              <textarea
                value={editContent}
                onChange={(e) => setEditContent(e.target.value)}
                className="flex-1 bg-[var(--bg-tertiary)] border border-[var(--border)] rounded-lg p-4 font-mono text-sm resize-none"
                placeholder="# Markdown content..."
              />
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center text-[var(--text-secondary)]">
              Select a note to edit
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Knowledge
