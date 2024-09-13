import { Product, ProductCreate } from '../types'

const API_URL = 'http://localhost:8000'

export async function getProducts(): Promise<Product[]> {
  const response = await fetch(`${API_URL}/products/`)
  return response.json()
}

export async function getProduct(id: number): Promise<Product> {
  const response = await fetch(`${API_URL}/products/${id}`)
  return response.json()
}

export async function createProduct(productData: ProductCreate): Promise<Product> {
  const response = await fetch(`${API_URL}/products/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(productData),
  })
  return response.json()
}
