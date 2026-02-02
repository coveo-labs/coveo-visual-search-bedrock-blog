import { motion } from 'framer-motion'

export default function Header() {
  return (
    <motion.header
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="border-b border-luxury-gold/20 backdrop-blur-sm bg-luxury-black/30"
    >
      <div className="container mx-auto px-4 py-8 flex justify-center items-center">
        <div className="flex items-center space-x-4">
          <div className="text-4xl font-serif font-bold text-luxury-gold tracking-[0.3em]">
            HERMÈS
          </div>
        </div>
      </div>
    </motion.header>
  )
}
