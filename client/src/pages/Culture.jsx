import { useState, useEffect } from 'react'
import { ShoppingBag, Heart } from 'lucide-react'
import { motion } from 'framer-motion'

export default function Culture() {
  const [products, setProducts] = useState([])
  const [favorites, setFavorites] = useState(new Set())

  useEffect(() => {
    fetch('/api/v1/culture/products')
      .then(res => res.json())
      .then(data => setProducts(data))
      .catch(err => console.error(err))
  }, [])

  const toggleFavorite = (id) => {
    setFavorites(prev => {
      const newFavorites = new Set(prev)
      if (newFavorites.has(id)) {
        newFavorites.delete(id)
      } else {
        newFavorites.add(id)
      }
      return newFavorites
    })
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-800 mb-2">Culture & Artisan Hub</h2>
        <p className="text-gray-600">Support local artisans and discover authentic Uttarakhand crafts</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {products.map((product, index) => (
          <motion.div
            key={product.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="card group cursor-pointer"
          >
            <div className="relative mb-4 overflow-hidden rounded-lg bg-gray-200 aspect-square">
              <img
                src={product.image}
                alt={product.name}
                className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
              />
              <button
                onClick={() => toggleFavorite(product.id)}
                className="absolute top-3 right-3 p-2 bg-white rounded-full shadow-lg hover:scale-110 transition-transform"
              >
                <Heart
                  size={20}
                  className={favorites.has(product.id) ? 'fill-red-500 text-red-500' : 'text-gray-600'}
                />
              </button>
            </div>

            <h3 className="text-xl font-bold text-gray-800 mb-2">{product.name}</h3>
            <p className="text-gray-600 text-sm mb-3">{product.description}</p>
            
            <div className="flex items-center justify-between">
              <div>
                <p className="text-2xl font-bold text-saffron">₹{product.price}</p>
                <p className="text-xs text-gray-500">By {product.artisan}</p>
              </div>
              <button className="btn-primary py-2 px-4 text-sm flex items-center gap-2">
                <ShoppingBag size={16} />
                View
              </button>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  )
}
