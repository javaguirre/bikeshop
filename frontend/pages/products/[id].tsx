import { useRouter } from 'next/router'
import { useState, useEffect } from 'react'
import { getProduct } from '../../services/api'
import Link from 'next/link'

interface Product {
  id: string
  name: string
  description: string
  price: number
}

export default function ProductPage() {
  const router = useRouter()
  const { id } = router.query
  const [product, setProduct] = useState<Product | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchProducts() {
      const data = await getProduct(Number(id))
      if (data) {
        setLoading(false)
        setProduct(data)
      }
    }
    fetchProducts()
  }, [])

  if (loading) {
    return <div>Loading...</div>
  }

  if (!product) {
    return <div>Product not found</div>
  }

  return (
    <div>
      <h1>{product.name}</h1>
      <p>{product.description}</p>

      <Link href="/cart">Customize</Link>
    </div>
  )
}
