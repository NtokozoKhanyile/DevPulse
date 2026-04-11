import { useState } from 'react'
import { HandMetal, Clock, Users } from 'lucide-react'
import { useAuthStore } from '../../store/authStore.js'
import { collaborationsApi } from '../../api/index.js'
import { useToast, Button, Modal, Textarea } from '../ui/index.js'

export function CollabButton({ project }) {
  const { user, isAuthenticated } = useAuthStore()
  const toast = useToast()

  const [modalOpen,  setModalOpen]  = useState(false)
  const [message,    setMessage]    = useState('')
  const [loading,    setLoading]    = useState(false)
  const [reqStatus,  setReqStatus]  = useState(null) // null | 'pending' | 'accepted'

  // Hide entirely if this is the owner's own project
  const isOwner = user?.id === project?.owner_id
  if (isOwner || !isAuthenticated) return null

  // Accepted state
  if (reqStatus === 'accepted') {
    return (
      <div className="flex items-center gap-2 px-4 py-2 rounded bg-brand-tint border border-brand-border text-brand-primary text-sm font-medium">
        <Users className="w-4 h-4" />
        Collaborating
      </div>
    )
  }

  // Pending state
  if (reqStatus === 'pending') {
    return (
      <div className="flex items-center gap-2 px-4 py-2 rounded bg-surface-offwhite border border-ui-border text-text-muted text-sm font-medium cursor-not-allowed">
        <Clock className="w-4 h-4" />
        Request sent
      </div>
    )
  }

  const handleSubmit = async () => {
    setLoading(true)
    try {
      await collaborationsApi.raiseHand(project.id, message)
      setReqStatus('pending')
      setModalOpen(false)
      setMessage('')
      toast('Collaboration request sent!', 'success')
    } catch (err) {
      const detail = err.response?.data?.detail ?? 'Failed to send request.'
      toast(detail, 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <Button
        variant="secondary"
        onClick={() => setModalOpen(true)}
      >
        <HandMetal className="w-4 h-4" />
        Raise hand
      </Button>

      <Modal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        title="Request to collaborate"
        size="md"
      >
        <div className="flex flex-col gap-4">
          <p className="text-sm text-text-body">
            Let <span className="font-medium">{project?.owner?.display_name}</span> know
            why you'd like to collaborate on{' '}
            <span className="font-medium">"{project?.title}"</span>.
          </p>

          <Textarea
            label="Message (optional)"
            placeholder="What would you bring to this project?"
            rows={4}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
          />

          <div className="flex gap-3 justify-end pt-2">
            <Button
              variant="ghost"
              onClick={() => setModalOpen(false)}
              disabled={loading}
            >
              Cancel
            </Button>
            <Button
              onClick={handleSubmit}
              loading={loading}
            >
              Send request
            </Button>
          </div>
        </div>
      </Modal>
    </>
  )
}