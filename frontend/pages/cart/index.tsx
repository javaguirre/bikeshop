import { useRouter } from 'next/router'
import { useState, useEffect } from 'react'
import { getParts, getProduct } from '../../services/api'
import Link from 'next/link'
import { Part } from '../../types'

const TEST_PRODUCT_ID = 1

export default function CartPage() {
  const router = useRouter()
  const { id } = router.query
  const [parts, setParts] = useState<Part[] | null>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchProducts() {
      const data = await getParts(Number(TEST_PRODUCT_ID))
      if (data) {
        setLoading(false)
        console.log(data)
        setParts(data)
      }
    }
    fetchProducts()
  }, [])

  if (loading) {
    return <div>Loading...</div>
  }

  if (!parts) {
    return <div>Parts not found</div>
  }

  return (
    <div>
      <h1>PARTS</h1>
      <p>{}</p>

      <Link href="/cart">Customize</Link>
    </div>
  )
}
