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
        // Initialize selectedOptions with the first option of each part
        const initialOptions: Record<number, number> = {}
        data.forEach(part => {
        if (part.options.length > 0) {
            initialOptions[Number(part.id)] = part.options[0].id
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
    return <div>Loading...</div>
  }

  if (parts.length === 0) {
    return <div>No parts found</div>
  }

  return (
    <div>
      <h1>Customize Your Bike</h1>
      {parts.map(part => (
        <div key={part.id} className="mb-4">
          <label htmlFor={`part-${part.id}`} className="block mb-2 font-bold">
            {part.name}
          </label>
          <select
            id={`part-${part.id}`}
            value={selectedOptions[Number(part.id)] || ''}
            onChange={(e) => handleOptionChange(Number(part.id), Number(e.target.value))}
            className="w-full p-2 border rounded"
          >
            {part.options.map(option => (
              <option key={option.id} value={option.id}>
                {option.name} - ${option.price}
              </option>
            ))}
          </select>
        </div>
      ))}
      <Link href="/cart" className="mt-4 inline-block px-4 py-2 bg-blue-500 text-white rounded">
        Add to Cart
      </Link>
    </div>
  )
}
