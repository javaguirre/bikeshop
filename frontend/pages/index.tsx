import Head from 'next/head'
import Link from 'next/link'

export default function Home() {
  return (
    <div>
      <Head>
        <title>Marcus's Bicycle Shop</title>
        <meta name="description" content="Custom bicycles and more" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main>
        <h1>Welcome to Marcus's Bicycle Shop</h1>
        <nav>
          <Link href="/products">
            View Products
          </Link>
          <Link href="/admin/products">
            Admin: Manage Products
          </Link>
        </nav>
      </main>
    </div>
  )
}
