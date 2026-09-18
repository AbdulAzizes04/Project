import React from 'react'
import { FiSun, FiMoon } from 'react-icons/fi'
import { useThemeStore } from '../store/store'
import { motion } from 'framer-motion'

export default function DarkModeToggle() {
  const { darkMode, toggleDarkMode } = useThemeStore()
  return (
    <button
      onClick={toggleDarkMode}
      className="p-2 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
      title={darkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
    >
      <motion.div
        key={darkMode ? 'moon' : 'sun'}
        initial={{ rotate: -90, opacity: 0 }}
        animate={{ rotate: 0, opacity: 1 }}
        transition={{ duration: 0.2 }}
      >
        {darkMode
          ? <FiSun className="text-xl text-yellow-400" />
          : <FiMoon className="text-xl text-gray-500" />
        }
      </motion.div>
    </button>
  )
}
