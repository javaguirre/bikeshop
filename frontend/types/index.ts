export interface Product {
    id: number
    name: string
    description: string
  }

  export interface ProductCreate {
    name: string
    description: string
  }

export interface Part {
  id: string
  name: string
  options: string[]
}

export interface CartItem {
  productId: string
  parts: { [partId: string]: string }
}

