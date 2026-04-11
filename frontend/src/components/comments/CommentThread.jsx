import { memo, useState } from 'react'
import { MoreHorizontal, Pencil, Trash2, CornerDownRight } from 'lucide-react'
import { useAuthStore } from '../../store/authStore.js'
import { commentsApi } from '../../api/index.js'
import { useToast, Avatar, Button } from '../ui/index.js'
import { CommentInput } from './CommentInput.jsx'
import clsx from 'clsx'

function timeAgo(dateString) {
  const seconds = Math.floor((Date.now() - new Date(dateString)) / 1000)
  if (seconds < 60)   return 'just now'
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`
  return `${Math.floor(seconds / 86400)}d ago`
}

// Single comment item
const CommentItem = memo(function CommentItem({
  comment,
  projectId,
  projectOwnerId,
  onReply,
  onDelete,
  onEdit,
  depth = 0,
}) {
  const { user } = useAuthStore()
  const toast    = useToast()

  const [editing,     setEditing]     = useState(false)
  const [editBody,    setEditBody]    = useState(comment.body)
  const [saving,      setSaving]      = useState(false)
  const [showMenu,    setShowMenu]    = useState(false)
  const [showReply,   setShowReply]   = useState(false)

  const isAuthor   = user?.id === comment.author_id
  const isOwner    = user?.id === projectOwnerId
  const canEdit    = isAuthor && !comment.is_deleted
  const canDelete  = (isAuthor || isOwner) && !comment.is_deleted

  // Edit is only allowed within 15 minutes of creation
  const createdAt  = new Date(comment.created_at)
  const canStillEdit = canEdit && (Date.now() - createdAt) < 15 * 60 * 1000

  const handleEdit = async () => {
    if (!editBody.trim()) return
    setSaving(true)
    try {
      await commentsApi.edit(projectId, comment.id, editBody)
      onEdit(comment.id, editBody)
      setEditing(false)
      toast('Comment updated.', 'success')
    } catch {
      toast('Failed to update comment.', 'error')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async () => {
    try {
      await commentsApi.delete(projectId, comment.id)
      onDelete(comment.id)
      toast('Comment deleted.', 'success')
    } catch {
      toast('Failed to delete comment.', 'error')
    }
  }

  return (
    <div className={clsx('flex gap-3', depth > 0 && 'ml-10 mt-3')}>
      {/* Avatar */}
      <Avatar
        src={comment.author?.avatar_url}
        name={comment.author?.display_name}
        size="sm"
        className="shrink-0 mt-0.5"
      />

      <div className="flex-1 min-w-0">
        {/* Header */}
        <div className="flex items-center gap-2 mb-1">
          <span className="text-sm font-semibold text-text-primary">
            {comment.author?.display_name ?? 'Deleted user'}
          </span>
          <span className="text-xs text-text-muted">
            {timeAgo(comment.created_at)}
          </span>
          {comment.is_edited && (
            <span className="text-xs text-text-muted italic">(edited)</span>
          )}

          {/* Actions menu */}
          {(canStillEdit || canDelete) && !comment.is_deleted && (
            <div className="relative ml-auto">
              <button
                onClick={() => setShowMenu((v) => !v)}
                aria-label="Comment options"
                className="p-1 rounded text-text-muted hover:text-text-primary hover:bg-surface-offwhite transition-colors"
              >
                <MoreHorizontal className="w-4 h-4" />
              </button>

              {showMenu && (
                <div className="absolute right-0 top-6 z-20 bg-surface-white border border-ui-border rounded-lg shadow-md py-1 min-w-[120px] animate-fade-in">
                  {canStillEdit && (
                    <button
                      onClick={() => { setEditing(true); setShowMenu(false) }}
                      className="flex items-center gap-2 w-full px-3 py-2 text-sm text-text-body hover:bg-surface-offwhite transition-colors"
                    >
                      <Pencil className="w-3.5 h-3.5" /> Edit
                    </button>
                  )}
                  {canDelete && (
                    <button
                      onClick={() => { handleDelete(); setShowMenu(false) }}
                      className="flex items-center gap-2 w-full px-3 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
                    >
                      <Trash2 className="w-3.5 h-3.5" /> Delete
                    </button>
                  )}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Body */}
        {comment.is_deleted ? (
          <p className="text-sm text-text-muted italic">[comment deleted]</p>
        ) : editing ? (
          <div className="flex flex-col gap-2">
            <textarea
              value={editBody}
              onChange={(e) => setEditBody(e.target.value)}
              rows={3}
              className="w-full px-3 py-2 rounded border border-ui-border text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-brand-primary resize-none"
              aria-label="Edit comment"
            />
            <div className="flex gap-2">
              <Button size="sm" onClick={handleEdit} loading={saving}>Save</Button>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => { setEditing(false); setEditBody(comment.body) }}
                disabled={saving}
              >
                Cancel
              </Button>
            </div>
          </div>
        ) : (
          <p className="text-sm text-text-body leading-relaxed whitespace-pre-wrap">
            {comment.body}
          </p>
        )}

        {/* Reply button — only one level deep */}
        {!comment.is_deleted && depth === 0 && (
          <button
            onClick={() => setShowReply((v) => !v)}
            className="flex items-center gap-1 mt-2 text-xs text-text-muted hover:text-brand-primary transition-colors"
          >
            <CornerDownRight className="w-3.5 h-3.5" />
            Reply
          </button>
        )}

        {/* Reply input */}
        {showReply && (
          <div className="mt-3 animate-fade-in">
            <CommentInput
              compact
              placeholder={`Reply to ${comment.author?.display_name}...`}
              onSubmit={async (body) => {
                await onReply(comment.id, body)
                setShowReply(false)
              }}
            />
          </div>
        )}

        {/* Nested replies */}
        {comment.replies?.length > 0 && (
          <div className="mt-3 flex flex-col gap-3">
            {comment.replies.map((reply) => (
              <CommentItem
                key={reply.id}
                comment={reply}
                projectId={projectId}
                projectOwnerId={projectOwnerId}
                onReply={onReply}
                onDelete={onDelete}
                onEdit={onEdit}
                depth={1}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  )
})

// Thread
export function CommentThread({ projectId, projectOwnerId, comments, onCommentsChange }) {
  const toast = useToast()

  const handlePost = async (body) => {
    try {
      const { data } = await commentsApi.post(projectId, { body })
      onCommentsChange([...comments, { ...data, replies: [] }])
    } catch {
      toast('Failed to post comment.', 'error')
      throw new Error('post failed')
    }
  }

  const handleReply = async (parentId, body) => {
    try {
      const { data } = await commentsApi.post(projectId, { body, parent_id: parentId })
      onCommentsChange(
        comments.map((c) =>
          c.id === parentId
            ? { ...c, replies: [...(c.replies ?? []), data] }
            : c
        )
      )
    } catch {
      toast('Failed to post reply.', 'error')
      throw new Error('reply failed')
    }
  }

  const handleDelete = (commentId) => {
    onCommentsChange(
      comments.map((c) => {
        if (c.id === commentId) return { ...c, is_deleted: true, body: '' }
        return {
          ...c,
          replies: c.replies?.map((r) =>
            r.id === commentId ? { ...r, is_deleted: true, body: '' } : r
          ),
        }
      })
    )
  }

  const handleEdit = (commentId, newBody) => {
    onCommentsChange(
      comments.map((c) => {
        if (c.id === commentId) return { ...c, body: newBody, is_edited: true }
        return {
          ...c,
          replies: c.replies?.map((r) =>
            r.id === commentId ? { ...r, body: newBody, is_edited: true } : r
          ),
        }
      })
    )
  }

  const topLevel = comments.filter((c) => !c.parent_id)

  return (
    <section aria-label="Comments" className="flex flex-col gap-6">
      <h3 className="text-base font-semibold text-text-primary">
        Comments ({comments.length})
      </h3>

      <CommentInput onSubmit={handlePost} />

      {topLevel.length > 0 ? (
        <div className="flex flex-col gap-5 divide-y divide-ui-border">
          {topLevel.map((comment) => (
            <div key={comment.id} className="pt-5 first:pt-0">
              <CommentItem
                comment={comment}
                projectId={projectId}
                projectOwnerId={projectOwnerId}
                onReply={handleReply}
                onDelete={handleDelete}
                onEdit={handleEdit}
              />
            </div>
          ))}
        </div>
      ) : (
        <p className="text-sm text-text-muted text-center py-8">
          No comments yet. Be the first to say something.
        </p>
      )}
    </section>
  )
}