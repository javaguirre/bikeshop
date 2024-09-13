import { useEffect, useState } from 'react'
import { getProducts } from '../../services/api'
import ProductList from '../../components/ProductList'
import { Product } from '../../types'

export default function Products() {
  const [products, setProducts] = useState<Product[]>([])

  useEffect(() => {
    async function fetchProducts() {
      const data = await getProducts()
      setProducts(data)
    }
    fetchProducts()
  }, [])

  return (
    <div>
      <h1>Our Products</h1>
      <ProductList products={products} />
    </div>
  )
}
