import Link from 'next/link'
import { Product } from '../types'

interface ProductListProps {
  products: Product[]
}

export default function ProductList({ products }: ProductListProps) {
  return (
    <ul>
      {products.map((product) => (
        <li key={product.id}>
          <Link href={`/products/${product.id}`}>
            <a>{product.name} - ${product.base_price}</a>
          </Link>
        </li>
      ))}
    </ul>
  )
}
