import { useRouter } from 'next/router'
import { useState, useEffect } from 'react'
import { getParts } from '../../services/api'
import Link from 'next/link'
import { Part } from '../../types'

const TEST_PRODUCT_ID = 1

export default function CartPage() {
  const router = useRouter()
  const { id } = router.query
  const [parts, setParts] = useState<Part[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedOptions, setSelectedOptions] = useState<Record<number, number>>({})

  useEffect(() => {
    async function fetchParts() {
        const data = await getParts(Number(TEST_PRODUCT_ID))
        if (data) {
          setLoading(false)
          setParts(data)
          const initialOptions: Record<number, number> = {}
          data.forEach(part => {
            if (part.options.length > 0) {
              initialOptions[part.id] = part.options[0].id
            }
          })
          setSelectedOptions(initialOptions)
        }
      }
    fetchParts()
  }, [id])

  const handleOptionChange = (partId: number, optionId: number) => {
    setSelectedOptions(prev => ({ ...prev, [partId]: optionId }))
  }

  if (loading) {
    return (
      <div className="container mt-5">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    )
  }

  if (parts.length === 0) {
    return (
      <div className="container mt-5">
        <div className="alert alert-warning" role="alert">
          No parts found
        </div>
      </div>
    )
  }

  return (
    <div className="container mt-5">
      <h1 className="mb-4">Customize Your Bike</h1>
      <form>
        {parts.map(part => (
          <div key={part.id} className="mb-3">
            <label htmlFor={`part-${part.id}`} className="form-label fw-bold">
              {part.name}
            </label>
            <select
              id={`part-${part.id}`}
              value={selectedOptions[part.id] || ''}
              onChange={(e) => handleOptionChange(part.id, Number(e.target.value))}
              className="form-select"
            >
              {part.options.map(option => (
                <option key={option.id} value={option.id}>
                  {option.name} - ${option.price.toFixed(2)}
                </option>
              ))}
            </select>
          </div>
        ))}
        <button type="submit" className="btn btn-primary">
          Add to Cart
        </button>
      </form>
    </div>
  )
}
