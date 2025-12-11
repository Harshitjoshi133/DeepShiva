import { useState, useEffect } from 'react'
import { ShoppingBag, Heart } from 'lucide-react'
import { motion } from 'framer-motion'
import { useLanguage } from '../contexts/LanguageContext'

export default function Culture() {
  const { t } = useLanguage()
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
    <div className="max-w-5xl mx-auto">
      <div className="mb-4">
        <h2 className="text-xl font-bold text-gray-800 mb-2">{t('culture.title', 'Culture & Artisan Hub')}</h2>
        <p className="text-gray-600 text-sm">{t('culture.description', 'Support local artisans and discover authentic Uttarakhand crafts')}</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {products.map((product, index) => (
          <motion.div
            key={product.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="glass-card group cursor-pointer hover:shadow-2xl"
          >
            <div className="relative mb-3 overflow-hidden rounded-lg bg-gray-200 aspect-square">
              <img
                src={product.image}
                alt={product.name}
                className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
              />
              <button
                onClick={() => toggleFavorite(product.id)}
                className="absolute top-2 right-2 p-1 bg-white rounded-full shadow-lg hover:scale-110 transition-transform"
              >
                <Heart
                  size={16}
                  className={favorites.has(product.id) ? 'fill-red-500 text-red-500' : 'text-gray-600'}
                />
              </button>
            </div>

            <h3 className="text-base font-bold text-gray-800 mb-1">{product.name}</h3>
            <p className="text-gray-600 text-xs mb-2">{product.description}</p>
            
            <div className="flex items-center justify-between">
              <div>
                <p className="text-lg font-bold text-saffron">₹{product.price}</p>
                <p className="text-xs text-gray-500">By {product.artisan}</p>
              </div>
              <button className="btn-primary py-1 px-3 text-xs flex items-center gap-1">
                <ShoppingBag size={14} />
                {t('common.view', 'View')}
              </button>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  )
}
