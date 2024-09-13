export interface Product {
    id: number
    name: string
    description: string
    base_price: number
  }

  export interface ProductCreate {
    name: string
    description: string
    base_price: number
  }
