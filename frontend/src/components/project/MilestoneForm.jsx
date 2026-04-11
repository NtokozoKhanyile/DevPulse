import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { useToast, Input, Textarea, Button } from '../ui/index.js'

export function MilestoneForm({ projectId, onMilestoneAdded }) {
  const toast   = useToast()
  const [loading, setLoading] = useState(false)

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm()

  const onSubmit = async (data) => {
    setLoading(true)
    try {
      await onMilestoneAdded({ title: data.title, body: data.body || undefined })
      reset()
      toast('Milestone posted!', 'success')
    } catch {
      toast('Failed to post milestone.', 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      noValidate
      className="flex flex-col gap-4 p-4 bg-brand-tint border border-brand-border rounded-lg"
    >
      <h4 className="text-sm font-semibold text-text-primary">Post a milestone</h4>

      <Input
        label="Title"
        placeholder="What did you achieve?"
        required
        error={errors.title?.message}
        {...register('title', {
          required:  'Milestone title is required',
          maxLength: { value: 200, message: 'Max 200 characters' },
        })}
      />

      <Textarea
        label="Details (optional)"
        placeholder="Add more context about this milestone..."
        rows={3}
        {...register('body')}
      />

      <div className="flex gap-3 justify-end">
        <Button type="submit" loading={loading} size="sm">
          Post milestone
        </Button>
      </div>
    </form>
  )
}