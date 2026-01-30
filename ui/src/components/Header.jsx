import { motion } from 'framer-motion'

export default function Header() {
  return (
    <motion.header
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="border-b border-luxury-gold/20 backdrop-blur-sm bg-luxury-black/30"
    >
      <div className="container mx-auto px-4 py-8 flex justify-between items-center">
        <div className="flex items-center space-x-4">
          <div className="text-4xl font-serif font-bold text-luxury-gold tracking-[0.3em]">
            HERMÈS
          </div>
        </div>
        
        <nav className="hidden md:flex space-x-12 text-luxury-cream font-light tracking-wider text-sm uppercase">
          <a href="#" className="hover:text-luxury-gold transition-colors duration-300">Image Search</a>
          <a href="#" className="hover:text-luxury-gold transition-colors duration-300">Collections</a>
        </nav>
      </div>
    </motion.header>
  )
}
